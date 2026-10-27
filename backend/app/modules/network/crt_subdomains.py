from typing import AsyncGenerator, Set
import httpx
from app.core.models import Finding, FindingStatus, TargetType
from app.modules.base import BaseModule

class CrtSubdomainsModule(BaseModule):
    name = "crt_subdomains"
    category = "Network & Infrastructure"
    description = "Passive subdomain enumeration via public Certificate Transparency (crt.sh) logs."
    target_types = [TargetType.DOMAIN]
    author = "OmniTrace Core"

    async def run(
        self,
        target: str,
        scan_id: str,
        client: httpx.AsyncClient
    ) -> AsyncGenerator[Finding, None]:
        domain = target.strip().lower()
        url = f"https://crt.sh/?q=%25.{domain}&output=json"

        headers = {
            "User-Agent": "OmniTrace-OSINT/1.0",
            "Accept": "application/json"
        }

        try:
            resp = await client.get(url, headers=headers, timeout=12.0)
            if resp.status_code == 200:
                data = resp.json()
                subdomains: Set[str] = set()

                for entry in data:
                    name_value = entry.get("name_value", "")
                    for sub in name_value.split("\n"):
                        sub_clean = sub.strip().lower().lstrip("*.")
                        if sub_clean and sub_clean.endswith(domain) and sub_clean != domain:
                            subdomains.add(sub_clean)

                sorted_subs = sorted(list(subdomains))
                if sorted_subs:
                    yield Finding(
                        scan_id=scan_id,
                        target=target,
                        target_type=TargetType.DOMAIN,
                        category="Network & Infrastructure",
                        source="crt.sh (Certificate Transparency)",
                        status=FindingStatus.FOUND,
                        title=f"Discovered {len(sorted_subs)} Passive Subdomains",
                        description=f"Extracted from SSL/TLS certificates: {', '.join(sorted_subs[:8])}{' ...' if len(sorted_subs) > 8 else ''}",
                        metadata={
                            "count": len(sorted_subs),
                            "subdomains": sorted_subs[:100]  # First 100 subdomains
                        }
                    )
                    return

            yield Finding(
                scan_id=scan_id,
                target=target,
                target_type=TargetType.DOMAIN,
                category="Network & Infrastructure",
                source="crt.sh",
                status=FindingStatus.NOT_FOUND,
                title="No Subdomains Found",
                description=f"No certificate entries found for %25.{domain} on crt.sh."
            )
        except Exception as e:
            yield Finding(
                scan_id=scan_id,
                target=target,
                target_type=TargetType.DOMAIN,
                category="Network & Infrastructure",
                source="crt.sh",
                status=FindingStatus.ERROR,
                title="Subdomain Enumeration Failed",
                description=f"crt.sh query timed out or failed: {str(e)}"
            )
