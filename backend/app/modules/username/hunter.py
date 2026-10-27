import asyncio
import json
from pathlib import Path
import time
from typing import AsyncGenerator, Dict, List
import httpx
from app.core.models import Finding, FindingStatus, TargetType
from app.modules.base import BaseModule

SITES_FILE = Path(__file__).parent / "sites.json"

class UsernameHunterModule(BaseModule):
    name = "username_hunter"
    category = "Username Recon"
    description = "Searches for username availability and profiles across 40+ popular platforms (Sherlock-style)."
    target_types = [TargetType.USERNAME]
    author = "OmniTrace Core"

    def __init__(self):
        self.sites: List[Dict] = []
        if SITES_FILE.exists():
            with open(SITES_FILE, "r", encoding="utf-8") as f:
                self.sites = json.load(f)

    async def _check_site(
        self,
        site: Dict,
        target: str,
        scan_id: str,
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore
    ) -> Finding:
        site_name = site["name"]
        url_pattern = site["url"]
        url = url_pattern.replace("{}", target)
        category = site.get("category", "Social Media")
        check_type = site.get("check_type", "status_code")
        error_code = site.get("error_code", 404)
        error_msg = site.get("error_msg", "")

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

        async with semaphore:
            t0 = time.time()
            try:
                resp = await client.get(url, headers=headers, follow_redirects=True, timeout=7.0)
                elapsed_ms = int((time.time() - t0) * 1000)

                if resp.status_code == 429:
                    return Finding(
                        scan_id=scan_id,
                        target=target,
                        target_type=TargetType.USERNAME,
                        category=category,
                        source=site_name,
                        status=FindingStatus.RATE_LIMITED,
                        url=url,
                        title=f"{site_name}: Rate Limited",
                        description=f"Received HTTP 429 from {site_name}",
                        metadata={"elapsed_ms": elapsed_ms, "status_code": 429}
                    )

                is_found = False
                if check_type == "status_code":
                    if resp.status_code == 200:
                        is_found = True
                    elif resp.status_code == error_code:
                        is_found = False
                    else:
                        is_found = False
                elif check_type == "message":
                    if error_msg and error_msg in resp.text:
                        is_found = False
                    elif resp.status_code == 200:
                        is_found = True

                if is_found:
                    return Finding(
                        scan_id=scan_id,
                        target=target,
                        target_type=TargetType.USERNAME,
                        category=category,
                        source=site_name,
                        status=FindingStatus.FOUND,
                        url=url,
                        title=f"Profile Found on {site_name}",
                        description=f"Confirmed active profile for @{target} on {site_name}",
                        metadata={
                            "elapsed_ms": elapsed_ms,
                            "status_code": resp.status_code,
                            "profile_url": url
                        }
                    )
                else:
                    return Finding(
                        scan_id=scan_id,
                        target=target,
                        target_type=TargetType.USERNAME,
                        category=category,
                        source=site_name,
                        status=FindingStatus.NOT_FOUND,
                        url=url,
                        title=f"Not Found on {site_name}",
                        description=f"No account matching @{target}",
                        metadata={"elapsed_ms": elapsed_ms, "status_code": resp.status_code}
                    )

            except httpx.TimeoutException:
                return Finding(
                    scan_id=scan_id,
                    target=target,
                    target_type=TargetType.USERNAME,
                    category=category,
                    source=site_name,
                    status=FindingStatus.ERROR,
                    url=url,
                    title=f"Timeout connecting to {site_name}",
                    description="Request timed out after 7s",
                    metadata={"error": "timeout"}
                )
            except Exception as e:
                return Finding(
                    scan_id=scan_id,
                    target=target,
                    target_type=TargetType.USERNAME,
                    category=category,
                    source=site_name,
                    status=FindingStatus.ERROR,
                    url=url,
                    title=f"Error checking {site_name}",
                    description=str(e),
                    metadata={"error": str(e)}
                )

    async def run(
        self,
        target: str,
        scan_id: str,
        client: httpx.AsyncClient
    ) -> AsyncGenerator[Finding, None]:
        semaphore = asyncio.Semaphore(12)
        tasks = [
            asyncio.create_task(self._check_site(site, target, scan_id, client, semaphore))
            for site in self.sites
        ]

        for future in asyncio.as_completed(tasks):
            finding = await future
            yield finding
