import ipaddress
import re
from typing import Optional
from app.core.models import DetectionResult, TargetType

# Regular expressions for entity classification
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
DOMAIN_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-_]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
)
PHONE_REGEX = re.compile(r"^\+?[1-9]\d{6,14}$")
HASH_MD5_REGEX = re.compile(r"^[a-fA-F0-9]{32}$")
HASH_SHA1_REGEX = re.compile(r"^[a-fA-F0-9]{40}$")
HASH_SHA256_REGEX = re.compile(r"^[a-fA-F0-9]{64}$")
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_\-\.]{2,32}$")

def is_valid_ip(val: str) -> bool:
    try:
        ipaddress.ip_address(val.strip())
        return True
    except ValueError:
        return False

def detect_entity(query: str) -> DetectionResult:
    cleaned = query.strip()
    
    # 1. Check IP Address
    if is_valid_ip(cleaned):
        ip_obj = ipaddress.ip_address(cleaned)
        version = f"IPv{ip_obj.version}"
        return DetectionResult(
            raw_query=query,
            detected_type=TargetType.IP,
            confidence=0.99,
            normalized_value=cleaned,
            recommended_modules=["geo_ip", "dns_lookup", "whois_lookup"],
            details={"version": version, "is_private": ip_obj.is_private}
        )

    # 2. Check Email Address
    if EMAIL_REGEX.match(cleaned):
        domain_part = cleaned.split("@")[1]
        return DetectionResult(
            raw_query=query,
            detected_type=TargetType.EMAIL,
            confidence=0.98,
            normalized_value=cleaned.lower(),
            recommended_modules=["email_validator", "holehe_presence", "gravatar", "hibp_breach"],
            details={"domain": domain_part}
        )

    # 3. Check Hash
    if HASH_SHA256_REGEX.match(cleaned):
        return DetectionResult(
            raw_query=query,
            detected_type=TargetType.HASH,
            confidence=0.99,
            normalized_value=cleaned.lower(),
            recommended_modules=["hash_lookup"],
            details={"hash_type": "SHA-256"}
        )
    if HASH_MD5_REGEX.match(cleaned):
        return DetectionResult(
            raw_query=query,
            detected_type=TargetType.HASH,
            confidence=0.95,
            normalized_value=cleaned.lower(),
            recommended_modules=["hash_lookup"],
            details={"hash_type": "MD5"}
        )
    if HASH_SHA1_REGEX.match(cleaned):
        return DetectionResult(
            raw_query=query,
            detected_type=TargetType.HASH,
            confidence=0.95,
            normalized_value=cleaned.lower(),
            recommended_modules=["hash_lookup"],
            details={"hash_type": "SHA-1"}
        )

    # 4. Check Phone Number (e.g. +14155552671 or numbers with dashes/spaces stripped)
    sanitized_phone = re.sub(r"[\s\(\)\-]", "", cleaned)
    if PHONE_REGEX.match(sanitized_phone) and (sanitized_phone.startswith("+") or len(sanitized_phone) >= 10):
        return DetectionResult(
            raw_query=query,
            detected_type=TargetType.PHONE,
            confidence=0.90,
            normalized_value=sanitized_phone if sanitized_phone.startswith("+") else f"+{sanitized_phone}",
            recommended_modules=["phone_lookup"],
            details={"digits_length": len(sanitized_phone)}
        )

    # 5. Check Domain Name (strip http:// or https:// if present)
    domain_candidate = cleaned
    if domain_candidate.startswith("http://"):
        domain_candidate = domain_candidate[7:]
    elif domain_candidate.startswith("https://"):
        domain_candidate = domain_candidate[8:]
    domain_candidate = domain_candidate.split("/")[0].split(":")[0]

    if DOMAIN_REGEX.match(domain_candidate) and not domain_candidate.endswith((".exe", ".png", ".jpg", ".pdf")):
        return DetectionResult(
            raw_query=query,
            detected_type=TargetType.DOMAIN,
            confidence=0.95,
            normalized_value=domain_candidate.lower(),
            recommended_modules=["dns_lookup", "crt_subdomains", "whois_lookup", "geo_ip", "http_headers"],
            details={"apex_domain": domain_candidate.lower()}
        )

    # 6. Fallback / Default: Username
    # Usernames can start with @ (e.g. @kraim0v -> kraim0v)
    username_candidate = cleaned.lstrip("@")
    if USERNAME_REGEX.match(username_candidate):
        return DetectionResult(
            raw_query=query,
            detected_type=TargetType.USERNAME,
            confidence=0.90,
            normalized_value=username_candidate,
            recommended_modules=["username_hunter"],
            details={"length": len(username_candidate)}
        )

    # Fallback to Unknown / Generic Username
    return DetectionResult(
        raw_query=query,
        detected_type=TargetType.USERNAME,
        confidence=0.60,
        normalized_value=cleaned.lstrip("@"),
        recommended_modules=["username_hunter"],
        details={"note": "Assumed username by default"}
    )
