import asyncio
import json
import time
import uuid
from typing import AsyncGenerator, Dict, List, Optional
import httpx
from app.config import settings
from app.core.database import save_finding, save_scan_start, update_scan_finish
from app.core.detector import detect_entity
from app.core.models import Finding, FindingStatus, ScanRequest, ScanStatus, ScanSummary, TargetType
from app.modules.base import BaseModule

# Import modules
from app.modules.breaches.hibp_check import HibpBreachModule
from app.modules.email.gravatar import GravatarModule
from app.modules.email.holehe_engine import HolehePresenceModule
from app.modules.email.validator import EmailValidatorModule
from app.modules.network.crt_subdomains import CrtSubdomainsModule
from app.modules.network.dns_lookup import DnsLookupModule
from app.modules.network.geo_ip import GeoIpModule
from app.modules.network.whois_lookup import WhoisLookupModule
from app.modules.phone.phonelookup import PhoneLookupModule
from app.modules.username.hunter import UsernameHunterModule

class ScanEngine:
    def __init__(self):
        self.modules: Dict[str, BaseModule] = {
            "username_hunter": UsernameHunterModule(),
            "email_validator": EmailValidatorModule(),
            "gravatar": GravatarModule(),
            "holehe_presence": HolehePresenceModule(),
            "dns_lookup": DnsLookupModule(),
            "whois_lookup": WhoisLookupModule(),
            "crt_subdomains": CrtSubdomainsModule(),
            "geo_ip": GeoIpModule(),
            "phone_lookup": PhoneLookupModule(),
            "hibp_breach": HibpBreachModule(),
        }
        self.active_scans: Dict[str, asyncio.Task] = {}
        self.scan_queues: Dict[str, asyncio.Queue] = {}
        self.scan_summaries: Dict[str, ScanSummary] = {}

    def get_available_modules(self) -> List[Dict]:
        return [
            {
                "id": key,
                "name": mod.name,
                "category": mod.category,
                "description": mod.description,
                "target_types": [t.value for t in mod.target_types],
                "requires_api_key": mod.requires_api_key,
                "author": mod.author,
            }
            for key, mod in self.modules.items()
        ]

    async def start_scan(self, req: ScanRequest) -> str:
        scan_id = str(uuid.uuid4())
        
        # Auto-detect target type if not supplied
        detection = detect_entity(req.target)
        target_type = req.target_type or detection.detected_type
        target = detection.normalized_value

        # Select modules
        if req.modules and len(req.modules) > 0:
            selected_keys = [k for k in req.modules if k in self.modules]
        else:
            # Use recommended modules by target type
            selected_keys = [
                key for key, mod in self.modules.items()
                if target_type in mod.target_types
            ]
            if not selected_keys and target_type == TargetType.USERNAME:
                selected_keys = ["username_hunter"]

        summary = ScanSummary(
            scan_id=scan_id,
            target=target,
            target_type=target_type,
            status=ScanStatus.RUNNING,
            started_at=time.time(),
            total_checks=0,
            found_count=0,
            not_found_count=0,
            error_count=0
        )
        self.scan_summaries[scan_id] = summary
        queue = asyncio.Queue()
        self.scan_queues[scan_id] = queue

        await save_scan_start(summary, req.case_id)

        # Start async worker task
        task = asyncio.create_task(
            self._execute_scan(scan_id, target, target_type, selected_keys, queue, req.proxy)
        )
        self.active_scans[scan_id] = task
        return scan_id

    async def _execute_scan(
        self,
        scan_id: str,
        target: str,
        target_type: TargetType,
        module_keys: List[str],
        queue: asyncio.Queue,
        custom_proxy: Optional[str] = None
    ):
        summary = self.scan_summaries[scan_id]
        proxy = custom_proxy or settings.proxy_url
        client_kwargs = {
            "timeout": settings.default_timeout,
            "headers": {"User-Agent": settings.user_agent},
            "follow_redirects": True
        }
        if proxy:
            client_kwargs["proxy"] = proxy

        try:
            # Send initial scan info event
            await queue.put({
                "event": "scan_start",
                "data": {
                    "scan_id": scan_id,
                    "target": target,
                    "target_type": target_type.value,
                    "modules": module_keys,
                    "started_at": summary.started_at
                }
            })

            async with httpx.AsyncClient(**client_kwargs) as client:
                for key in module_keys:
                    module = self.modules.get(key)
                    if not module:
                        continue

                    await queue.put({
                        "event": "module_start",
                        "data": {"module": key, "category": module.category}
                    })

                    try:
                        async for finding in module.run(target, scan_id, client):
                            summary.total_checks += 1
                            if finding.status == FindingStatus.FOUND:
                                summary.found_count += 1
                            elif finding.status == FindingStatus.NOT_FOUND:
                                summary.not_found_count += 1
                            elif finding.status in (FindingStatus.ERROR, FindingStatus.RATE_LIMITED):
                                summary.error_count += 1

                            summary.findings.append(finding)
                            # Persist asynchronously
                            asyncio.create_task(save_finding(finding))

                            # Stream to UI
                            await queue.put({
                                "event": "finding",
                                "data": finding.model_dump()
                            })
                    except Exception as mod_err:
                        err_finding = Finding(
                            scan_id=scan_id,
                            target=target,
                            target_type=target_type,
                            category=module.category,
                            source=module.name,
                            status=FindingStatus.ERROR,
                            title=f"Module '{module.name}' Exception",
                            description=str(mod_err)
                        )
                        summary.error_count += 1
                        summary.findings.append(err_finding)
                        await queue.put({
                            "event": "finding",
                            "data": err_finding.model_dump()
                        })

            summary.status = ScanStatus.COMPLETED
            summary.ended_at = time.time()
            await update_scan_finish(summary)

            await queue.put({
                "event": "scan_complete",
                "data": summary.model_dump()
            })

        except asyncio.CancelledError:
            summary.status = ScanStatus.STOPPED
            summary.ended_at = time.time()
            await update_scan_finish(summary)
            await queue.put({
                "event": "scan_stopped",
                "data": {"scan_id": scan_id, "message": "Scan cancelled by user."}
            })
        except Exception as e:
            summary.status = ScanStatus.FAILED
            summary.ended_at = time.time()
            await update_scan_finish(summary)
            await queue.put({
                "event": "scan_failed",
                "data": {"scan_id": scan_id, "error": str(e)}
            })
        finally:
            if scan_id in self.active_scans:
                del self.active_scans[scan_id]

    async def stream_scan_events(self, scan_id: str) -> AsyncGenerator[Dict, None]:
        queue = self.scan_queues.get(scan_id)
        if not queue:
            # Check if scan exists in DB/history
            yield {
                "event": "error",
                "data": json.dumps({"error": f"Scan {scan_id} not active or not found."})
            }
            return

        while True:
            try:
                # Wait for next event or timeout
                event_data = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield {
                    "event": event_data["event"],
                    "data": json.dumps(event_data["data"])
                }
                queue.task_done()

                # If terminal event, finish stream
                if event_data["event"] in ("scan_complete", "scan_stopped", "scan_failed"):
                    break
            except asyncio.TimeoutError:
                # Keep-alive heartbeat comment
                yield {"comment": "keep-alive"}
            except asyncio.CancelledError:
                break

    def stop_scan(self, scan_id: str) -> bool:
        task = self.active_scans.get(scan_id)
        if task and not task.done():
            task.cancel()
            return True
        return False

# Global Singleton
engine = ScanEngine()
