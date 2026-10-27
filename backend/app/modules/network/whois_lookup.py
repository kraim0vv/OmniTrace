from typing import AsyncGenerator
import httpx
from app.core.models import Finding, FindingStatus, TargetType
from app.modules.base import BaseModule

class WhoisLookupModule(BaseModule):
    name = "whois_lookup"
    category = "Network & Infrastructure"
    description = "Retrieves domain registrar, creation date, expiration, and status via modern RDAP protocols."
    target_types = [TargetType.DOMAIN, TargetType.IP]
    author = "OmniTrace Core"

    async def run(
        self,
        target: str,
        scan_id: str,
        client: httpx.AsyncClient
    ) -> AsyncGenerator[Finding, None]:
        url = f"https://rdap.org/domain/{target.strip()}"
        headers = {"Accept": "application/rdap+json, application/json", "User-Agent": "OmniTrace-RDAP/1.0"}

        try:
            resp = await client.get(url, headers=headers, follow_redirects=True, timeout=8.0)
            if resp.status_code == 200:
                data = resp.json()
                handle = data.get("handle", "")
                events = {e.get("eventAction"): e.get("eventDate") for e in data.get("events", [])}
                nameservers = [
                    ns.get("ldhName", "") for ns in data.get("nameservers", []) if ns.get("ldhName")
                ]
                status_list = data.get("status", [])

                created = events.get("registration", "Unknown")
                expires = events.get("expiration", "Unknown")
                updated = events.get("last changed", "Unknown")

                # Find registrar entity if available
                registrar = "Unknown"
                for entity in data.get("entities", []):
                    roles = entity.get("roles", [])
                    if "registrar" in roles:
                        vcard = entity.get("vcardArray", [])
                        if len(vcard) > 1:
                            for item in vcard[1]:
                                if item[0] == "fn":
                                    registrar = item[3]
                                    break

                yield Finding(
                    scan_id=scan_id,
                    target=target,
                    target_type=TargetType.DOMAIN,
                    category="Network & Infrastructure",
                    source="RDAP / WHOIS",
                    status=FindingStatus.FOUND,
                    title=f"Registrar: {registrar}",
                    description=f"Created: {created} | Expires: {expires} | Nameservers: {', '.join(nameservers[:2])}",
                    metadata={
                        "registrar": registrar,
                        "created": created,
                        "expires": expires,
                        "updated": updated,
                        "nameservers": nameservers,
                        "status": status_list,
                        "handle": handle
                    }
                )
                return

            yield Finding(
                scan_id=scan_id,
                target=target,
                target_type=TargetType.DOMAIN,
                category="Network & Infrastructure",
                source="RDAP / WHOIS",
                status=FindingStatus.NOT_FOUND,
                title="RDAP Record Not Found",
                description=f"No registration record returned for {target} (HTTP {resp.status_code})."
            )
        except Exception as e:
            yield Finding(
                scan_id=scan_id,
                target=target,
                target_type=TargetType.DOMAIN,
                category="Network & Infrastructure",
                source="RDAP / WHOIS",
                status=FindingStatus.ERROR,
                title="RDAP Query Failed",
                description=str(e)
            )
