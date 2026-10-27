import asyncio
from typing import AsyncGenerator
import dns.asyncresolver
import httpx
from app.core.models import Finding, FindingStatus, TargetType
from app.modules.base import BaseModule

RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "SOA"]

class DnsLookupModule(BaseModule):
    name = "dns_lookup"
    category = "Network & Infrastructure"
    description = "Queries authoritative DNS servers for A, AAAA, MX, TXT (SPF/DMARC), NS, and SOA records."
    target_types = [TargetType.DOMAIN, TargetType.IP]
    author = "OmniTrace Core"

    async def _query_record(self, domain: str, rtype: str, resolver: dns.asyncresolver.Resolver):
        try:
            answers = await resolver.resolve(domain, rtype)
            values = []
            for r in answers:
                if rtype == "MX":
                    values.append(f"{r.preference} {str(r.exchange).rstrip('.')}")
                elif rtype == "TXT":
                    values.append(" ".join(t.decode("utf-8", "ignore") for t in r.strings))
                else:
                    values.append(str(r).rstrip("."))
            return rtype, values
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            return rtype, []
        except Exception:
            return rtype, None

    async def run(
        self,
        target: str,
        scan_id: str,
        client: httpx.AsyncClient
    ) -> AsyncGenerator[Finding, None]:
        domain = target.strip()
        resolver = dns.asyncresolver.Resolver()
        resolver.timeout = 5.0
        resolver.lifetime = 5.0

        tasks = [self._query_record(domain, rtype, resolver) for rtype in RECORD_TYPES]
        results = await asyncio.gather(*tasks)

        found_any = False
        for rtype, records in results:
            if records:
                found_any = True
                yield Finding(
                    scan_id=scan_id,
                    target=target,
                    target_type=TargetType.DOMAIN,
                    category="Network & Infrastructure",
                    source=f"DNS {rtype}",
                    status=FindingStatus.FOUND,
                    title=f"{rtype} Records ({len(records)})",
                    description=f"{', '.join(records[:5])}{' ...' if len(records) > 5 else ''}",
                    metadata={"record_type": rtype, "records": records}
                )

        if not found_any:
            yield Finding(
                scan_id=scan_id,
                target=target,
                target_type=TargetType.DOMAIN,
                category="Network & Infrastructure",
                source="DNS Lookup",
                status=FindingStatus.NOT_FOUND,
                title="No DNS Records Found",
                description=f"Could not resolve standard DNS records for {target}."
            )
