import hashlib
import re
from typing import AsyncGenerator
from bs4 import BeautifulSoup
import httpx
from app.core.models import Finding, FindingStatus, TargetType
from app.modules.base import BaseModule

class HttpHeadersModule(BaseModule):
    name = "http_headers"
    category = "Network & Infrastructure"
    description = "Inspects HTTP/HTTPS response headers, web technologies, security headers, and page metadata."
    target_types = [TargetType.DOMAIN, TargetType.IP]
    author = "OmniTrace Core"

    async def run(
        self,
        target: str,
        scan_id: str,
        client: httpx.AsyncClient
    ) -> AsyncGenerator[Finding, None]:
        url = target.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"

        try:
            resp = await client.get(url, timeout=7.0, follow_redirects=True)
            headers = dict(resp.headers)
            server = headers.get("server", "Hidden / Not Disclosed")
            powered_by = headers.get("x-powered-by", None)

            # Security headers check
            hsts = "strict-transport-security" in headers
            csp = "content-security-policy" in headers
            xframe = headers.get("x-frame-options", "Missing")

            # Extract title using BeautifulSoup
            soup = BeautifulSoup(resp.text[:30000], "html.parser")
            page_title = soup.title.string.strip() if soup.title and soup.title.string else "No Title"

            yield Finding(
                scan_id=scan_id,
                target=target,
                target_type=TargetType.DOMAIN,
                category="Network & Infrastructure",
                source="HTTP Web Inspection",
                status=FindingStatus.FOUND,
                url=str(resp.url),
                title=f"Server: {server} | {page_title[:45]}",
                description=f"Status: HTTP {resp.status_code} | HSTS: {'Yes' if hsts else 'No'} | CSP: {'Yes' if csp else 'No'} | X-Frame: {xframe}",
                metadata={
                    "status_code": resp.status_code,
                    "server": server,
                    "title": page_title,
                    "x_powered_by": powered_by,
                    "hsts_enabled": hsts,
                    "csp_enabled": csp,
                    "x_frame_options": xframe,
                    "headers_count": len(headers)
                }
            )
        except Exception as e:
            yield Finding(
                scan_id=scan_id,
                target=target,
                target_type=TargetType.DOMAIN,
                category="Network & Infrastructure",
                source="HTTP Web Inspection",
                status=FindingStatus.INFO,
                title="Web Server Inspection Inactive",
                description=f"Could not connect via HTTPS: {str(e)[:80]}"
            )
