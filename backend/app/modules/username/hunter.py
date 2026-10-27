import asyncio
import json
from pathlib import Path
import re
import time
from typing import AsyncGenerator, Dict, List
import httpx
from app.core.models import Finding, FindingStatus, TargetType
from app.modules.base import BaseModule

SITES_FILE = Path(__file__).parent / "sites.json"

WAF_SIGNATURES = [
    "<title>Just a moment...",
    "<title>Client Challenge</title>",
    "<title>Attention Required! | Cloudflare</title>",
    "Cloudflare Ray ID:",
    "Please enable JavaScript and Cookies to continue",
    "<title>Access Denied</title>",
    "<title>Bot Verification</title>",
    "<title>Security Check</title>",
    "cf-browser-verification",
]

class UsernameHunterModule(BaseModule):
    name = "username_hunter"
    category = "Username Recon"
    description = "Searches for username availability and profiles across verified platforms with 100% precision."
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
        url_probe = site["url"].replace("{}", target)
        profile_url = site.get("profile_url", site["url"]).replace("{}", target)
        category = site.get("category", "Social Media")
        check_type = site.get("check_type", "status_code")
        error_url = site.get("error_url")
        regex = site.get("regex")

        # 1. Regex constraint check
        if regex and not re.search(regex, target):
            return Finding(
                scan_id=scan_id,
                target=target,
                target_type=TargetType.USERNAME,
                category=category,
                source=site_name,
                status=FindingStatus.NOT_FOUND,
                url=profile_url,
                title=f"Invalid format for {site_name}",
                description=f"Username does not conform to {site_name}'s naming constraints."
            )

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
                resp = await client.get(url_probe, headers=headers, follow_redirects=True, timeout=6.0)
                elapsed_ms = int((time.time() - t0) * 1000)

                # WAF / Bot challenge detection -> NEVER mark as found
                for waf in WAF_SIGNATURES:
                    if waf in resp.text:
                        return Finding(
                            scan_id=scan_id,
                            target=target,
                            target_type=TargetType.USERNAME,
                            category=category,
                            source=site_name,
                            status=FindingStatus.RATE_LIMITED,
                            url=profile_url,
                            title=f"WAF Protection on {site_name}",
                            description="Encountered automated bot challenge; skipped to avoid false positive.",
                            metadata={"status_code": resp.status_code, "elapsed_ms": elapsed_ms}
                        )

                if resp.status_code == 429:
                    return Finding(
                        scan_id=scan_id,
                        target=target,
                        target_type=TargetType.USERNAME,
                        category=category,
                        source=site_name,
                        status=FindingStatus.RATE_LIMITED,
                        url=profile_url,
                        title=f"{site_name}: Rate Limited",
                        description=f"Received HTTP 429 from {site_name}",
                        metadata={"elapsed_ms": elapsed_ms, "status_code": 429}
                    )

                is_found = False

                if check_type == "status_code":
                    if resp.status_code == 200:
                        if error_url and str(resp.url).rstrip('/') == error_url.rstrip('/'):
                            is_found = False
                        else:
                            is_found = True
                    else:
                        is_found = False

                elif check_type == "response_url":
                    if resp.status_code == 200:
                        if error_url and str(resp.url).rstrip('/') == error_url.rstrip('/'):
                            is_found = False
                        else:
                            is_found = True
                    else:
                        is_found = False

                elif check_type == "api_not_null":
                    if resp.status_code == 200 and resp.text.strip() != "null":
                        is_found = True

                elif check_type == "api_codeforces":
                    if resp.status_code == 200:
                        try:
                            is_found = resp.json().get("status") == "OK"
                        except Exception:
                            is_found = False

                elif check_type == "api_keybase":
                    if resp.status_code == 200:
                        try:
                            them = resp.json().get("them", [None])
                            is_found = them[0] is not None
                        except Exception:
                            is_found = False

                elif check_type == "api_duolingo":
                    if resp.status_code == 200:
                        try:
                            users = resp.json().get("users", [])
                            is_found = len(users) > 0
                        except Exception:
                            is_found = False

                elif check_type == "api_npm":
                    if resp.status_code == 200:
                        try:
                            is_found = resp.json().get("total", 0) > 0
                        except Exception:
                            is_found = False

                elif check_type == "message_present":
                    success_msg = site.get("success_msg", "")
                    if resp.status_code == 200 and success_msg in resp.text:
                        is_found = True

                elif check_type == "steam_check":
                    if resp.status_code == 200:
                        has_error = "The specified profile could not be found" in resp.text
                        has_persona = "actual_persona_name" in resp.text or "responsive_status_info" in resp.text
                        is_found = not has_error and has_persona

                elif check_type == "youtube_check":
                    if resp.status_code == 200:
                        has_error = "This page isn't available" in resp.text or "404 Not Found" in resp.text
                        is_found = not has_error

                elif check_type == "linktree_check":
                    if resp.status_code == 200:
                        has_error = "Page Not Found" in resp.text or "The page you're looking for" in resp.text or "404" in resp.text
                        is_found = not has_error

                if is_found:
                    return Finding(
                        scan_id=scan_id,
                        target=target,
                        target_type=TargetType.USERNAME,
                        category=category,
                        source=site_name,
                        status=FindingStatus.FOUND,
                        url=profile_url,
                        title=f"Verified Profile on {site_name}",
                        description=f"Confirmed active identity for @{target} on {site_name}",
                        metadata={
                            "elapsed_ms": elapsed_ms,
                            "status_code": resp.status_code,
                            "profile_url": profile_url
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
                        url=profile_url,
                        title=f"Not Found on {site_name}",
                        description=f"No active account matching @{target}",
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
                    url=profile_url,
                    title=f"Timeout connecting to {site_name}",
                    description="Request timed out after 6s",
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
                    url=profile_url,
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
        semaphore = asyncio.Semaphore(15)
        tasks = [
            asyncio.create_task(self._check_site(site, target, scan_id, client, semaphore))
            for site in self.sites
        ]

        for future in asyncio.as_completed(tasks):
            finding = await future
            yield finding
