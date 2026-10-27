import re
from typing import AsyncGenerator
import dns.asyncresolver
import httpx
from app.core.models import Finding, FindingStatus, TargetType
from app.modules.base import BaseModule

DISPOSABLE_DOMAINS = {
    "mailinator.com", "guerrillamail.com", "tempmail.com", "10minutemail.com",
    "yopmail.com", "throwawaymail.com", "sharklasers.com", "getairmail.com",
    "mohmal.com", "dispostable.com", "trashmail.com", "temp-mail.org",
    "fakeinbox.com", "generator.email", "burnermail.io", "protonmail.ch"
}

class EmailValidatorModule(BaseModule):
    name = "email_validator"
    category = "Email Intel"
    description = "Validates email syntax, checks DNS MX records, and detects disposable mail providers."
    target_types = [TargetType.EMAIL]
    author = "OmniTrace Core"

    async def run(
        self,
        target: str,
        scan_id: str,
        client: httpx.AsyncClient
    ) -> AsyncGenerator[Finding, None]:
        email = target.strip().lower()
        if "@" not in email:
            yield Finding(
                scan_id=scan_id,
                target=target,
                target_type=TargetType.EMAIL,
                category="Email Intel",
                source="Syntax Checker",
                status=FindingStatus.ERROR,
                title="Invalid Email Format",
                description="Email does not contain an '@' delimiter.",
            )
            return

        username, domain = email.split("@", 1)
        is_disposable = domain in DISPOSABLE_DOMAINS

        # 1. Syntax & Disposable status
        yield Finding(
            scan_id=scan_id,
            target=target,
            target_type=TargetType.EMAIL,
            category="Email Intel",
            source="Email Syntax & Structure",
            status=FindingStatus.FOUND,
            title="Valid Email Format",
            description=f"Parsed username '{username}' on host '{domain}'. Disposable: {'Yes (Temp Mail)' if is_disposable else 'No (Legitimate Host)'}.",
            metadata={
                "username": username,
                "domain": domain,
                "is_disposable": is_disposable
            }
        )

        # 2. MX Record Resolution
        try:
            resolver = dns.asyncresolver.Resolver()
            resolver.timeout = 4.0
            resolver.lifetime = 4.0
            answers = await resolver.resolve(domain, "MX")
            mx_records = [str(r.exchange).rstrip(".") for r in answers]
            
            yield Finding(
                scan_id=scan_id,
                target=target,
                target_type=TargetType.EMAIL,
                category="Email Intel",
                source="MX Verification",
                status=FindingStatus.FOUND,
                title=f"MX Records Found ({len(mx_records)})",
                description=f"Mail servers configured for {domain}: {', '.join(mx_records[:3])}",
                metadata={"mx_servers": mx_records, "domain": domain}
            )
        except dns.resolver.NXDOMAIN:
            yield Finding(
                scan_id=scan_id,
                target=target,
                target_type=TargetType.EMAIL,
                category="Email Intel",
                source="MX Verification",
                status=FindingStatus.NOT_FOUND,
                title=f"Domain Does Not Exist ({domain})",
                description=f"DNS returned NXDOMAIN for {domain}. Email cannot receive messages.",
                metadata={"domain": domain}
            )
        except Exception as e:
            yield Finding(
                scan_id=scan_id,
                target=target,
                target_type=TargetType.EMAIL,
                category="Email Intel",
                source="MX Verification",
                status=FindingStatus.ERROR,
                title="MX Lookup Failed",
                description=f"Failed to query mail exchange servers for {domain}: {str(e)}",
                metadata={"error": str(e)}
            )
