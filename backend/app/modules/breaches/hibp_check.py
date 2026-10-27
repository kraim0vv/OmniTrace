import hashlib
from typing import AsyncGenerator
import httpx
from app.config import settings
from app.core.models import Finding, FindingStatus, TargetType
from app.modules.base import BaseModule

class HibpBreachModule(BaseModule):
    name = "hibp_breach"
    category = "Breaches & Exposure"
    description = "Checks data breach exposure via HaveIBeenPwned & k-Anonymity password hash checks."
    target_types = [TargetType.EMAIL, TargetType.HASH]
    author = "OmniTrace Core"

    async def _check_hash_pwned(
        self,
        target_hash: str,
        scan_id: str,
        client: httpx.AsyncClient
    ) -> Finding:
        # Pwned Passwords uses SHA-1 k-anonymity (first 5 chars)
        prefix = target_hash[:5].upper()
        suffix = target_hash[5:].upper()
        url = f"https://api.pwnedpasswords.com/range/{prefix}"

        try:
            resp = await client.get(url, headers={"Add-Padding": "true"}, timeout=6.0)
            if resp.status_code == 200:
                lines = resp.text.splitlines()
                count = 0
                for line in lines:
                    parts = line.split(":")
                    if len(parts) == 2 and parts[0].strip() == suffix:
                        count = int(parts[1].strip())
                        break

                if count > 0:
                    return Finding(
                        scan_id=scan_id,
                        target=target_hash,
                        target_type=TargetType.HASH,
                        category="Breaches & Exposure",
                        source="HIBP Pwned Passwords",
                        status=FindingStatus.FOUND,
                        title=f"Hash Compromised ({count:,} times)",
                        description=f"This SHA-1 hash was identified in public data dumps {count:,} times.",
                        metadata={"occurrences": count, "hash_prefix": prefix}
                    )
                else:
                    return Finding(
                        scan_id=scan_id,
                        target=target_hash,
                        target_type=TargetType.HASH,
                        category="Breaches & Exposure",
                        source="HIBP Pwned Passwords",
                        status=FindingStatus.NOT_FOUND,
                        title="Hash Not Seen in Public Dumps",
                        description="k-Anonymity lookup found 0 occurrences in breach databases."
                    )
            return Finding(
                scan_id=scan_id,
                target=target_hash,
                target_type=TargetType.HASH,
                category="Breaches & Exposure",
                source="HIBP Pwned Passwords",
                status=FindingStatus.ERROR,
                title="Lookup Error",
                description=f"HTTP {resp.status_code} returned by HIBP"
            )
        except Exception as e:
            return Finding(
                scan_id=scan_id,
                target=target_hash,
                target_type=TargetType.HASH,
                category="Breaches & Exposure",
                source="HIBP Pwned Passwords",
                status=FindingStatus.ERROR,
                title="Lookup Exception",
                description=str(e)
            )

    async def _check_email_breach(
        self,
        email: str,
        scan_id: str,
        client: httpx.AsyncClient
    ) -> Finding:
        if settings.hibp_api_key:
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false"
            headers = {"hibp-api-key": settings.hibp_api_key, "user-agent": "OmniTrace-OSINT"}
            try:
                resp = await client.get(url, headers=headers, timeout=7.0)
                if resp.status_code == 200:
                    breaches = resp.json()
                    breach_names = [b.get("Name") for b in breaches]
                    return Finding(
                        scan_id=scan_id,
                        target=email,
                        target_type=TargetType.EMAIL,
                        category="Breaches & Exposure",
                        source="HaveIBeenPwned API",
                        status=FindingStatus.FOUND,
                        title=f"Compromised in {len(breaches)} Breaches",
                        description=f"Appeared in: {', '.join(breach_names[:4])}{' ...' if len(breach_names) > 4 else ''}",
                        metadata={"breaches": breach_names, "count": len(breaches)}
                    )
                elif resp.status_code == 404:
                    return Finding(
                        scan_id=scan_id,
                        target=email,
                        target_type=TargetType.EMAIL,
                        category="Breaches & Exposure",
                        source="HaveIBeenPwned API",
                        status=FindingStatus.NOT_FOUND,
                        title="No Breaches Found",
                        description="Account has not appeared in known HIBP data breaches."
                    )
            except Exception as e:
                return Finding(
                    scan_id=scan_id,
                    target=email,
                    target_type=TargetType.EMAIL,
                    category="Breaches & Exposure",
                    source="HaveIBeenPwned API",
                    status=FindingStatus.ERROR,
                    title="HIBP API Error",
                    description=str(e)
                )

        # Fallback if no API key configured: provide informative guidance
        return Finding(
            scan_id=scan_id,
            target=email,
            target_type=TargetType.EMAIL,
            category="Breaches & Exposure",
            source="Breach Scanner",
            status=FindingStatus.INFO,
            title="HIBP Key Not Set (Optional)",
            description="Add your HIBP API key in Settings to unlock deep automated breach history checks.",
            metadata={"hint": "Set HIBP_API_KEY in Settings modal or .env"}
        )

    async def run(
        self,
        target: str,
        scan_id: str,
        client: httpx.AsyncClient
    ) -> AsyncGenerator[Finding, None]:
        if "@" in target:
            yield await self._check_email_breach(target, scan_id, client)
        else:
            yield await self._check_hash_pwned(target, scan_id, client)
