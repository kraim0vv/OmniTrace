import asyncio
import json

import httpx

from app.core.database import get_scan_findings, init_db
from app.core.engine import ScanEngine
from app.core.models import Finding, FindingStatus, ScanRequest, TargetType
from app.modules.base import BaseModule
from app.modules.username.hunter import UsernameHunterModule


class SlowModule(BaseModule):
    name = "slow"
    target_types = [TargetType.USERNAME]

    def __init__(self, log):
        self.log = log

    async def run(self, target, scan_id, client):
        self.log.append(f"{self.name}:start")
        await asyncio.sleep(0.05)
        self.log.append(f"{self.name}:end")
        yield Finding(scan_id=scan_id, target=target, target_type=TargetType.USERNAME,
                      category="Test", source=self.name, status=FindingStatus.FOUND)


class OtherSlowModule(SlowModule):
    name = "other"


class BrokenModule(BaseModule):
    name = "broken"
    target_types = [TargetType.USERNAME]

    async def run(self, target, scan_id, client):
        raise RuntimeError("boom")
        yield  # pragma: no cover


def test_modules_run_concurrently_and_results_persist():
    async def scenario():
        await init_db()
        log = []
        engine = ScanEngine()
        engine.modules = {"slow": SlowModule(log), "other": OtherSlowModule(log), "broken": BrokenModule()}
        scan_id = await engine.start_scan(ScanRequest(target="alice"))
        events = [e async for e in engine.stream_scan_events(scan_id) if "event" in e]
        return log, scan_id, events, await get_scan_findings(scan_id)

    log, scan_id, events, stored = asyncio.run(scenario())

    # Both modules started before either finished
    assert log.index("other:start") < log.index("slow:end") or log.index("slow:start") < log.index("other:end")
    assert log[:2] in (["slow:start", "other:start"], ["other:start", "slow:start"])

    assert events[-1]["event"] == "scan_complete"
    summary = json.loads(events[-1]["data"])
    assert summary["found_count"] == 2
    assert summary["error_count"] == 1
    assert "findings" not in summary
    assert len(stored) == 3
    assert any(f.status == FindingStatus.ERROR and "boom" in f.description for f in stored)


def test_username_is_url_encoded_in_probes():
    seen = []

    def handler(request):
        seen.append(str(request.url))
        return httpx.Response(404)

    async def scenario():
        module = UsernameHunterModule()
        site = {"name": "Example", "url": "https://example.com/u/{}", "check_type": "status_code"}
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            await module._check_site(site, "../admin?x=1", "scan", client, asyncio.Semaphore(1))

    asyncio.run(scenario())
    assert seen == ["https://example.com/u/..%2Fadmin%3Fx%3D1"]
