from typing import AsyncGenerator
import httpx
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from app.core.models import Finding, FindingStatus, TargetType
from app.modules.base import BaseModule

class PhoneLookupModule(BaseModule):
    name = "phone_lookup"
    category = "Telephony & Mobile"
    description = "Parses international phone numbers, resolves carrier, region, timezones, and generates messaging links."
    target_types = [TargetType.PHONE]
    author = "OmniTrace Core"

    async def run(
        self,
        target: str,
        scan_id: str,
        client: httpx.AsyncClient
    ) -> AsyncGenerator[Finding, None]:
        raw_number = target.strip()
        if not raw_number.startswith("+"):
            raw_number = "+" + raw_number

        try:
            parsed = phonenumbers.parse(raw_number, None)
            is_valid = phonenumbers.is_valid_number(parsed)
            is_possible = phonenumbers.is_possible_number(parsed)

            if not is_possible:
                yield Finding(
                    scan_id=scan_id,
                    target=target,
                    target_type=TargetType.PHONE,
                    category="Telephony & Mobile",
                    source="LibPhoneNumber",
                    status=FindingStatus.ERROR,
                    title="Impossible Phone Number",
                    description=f"'{target}' is not a valid or possible phone number structure."
                )
                return

            country_name = geocoder.description_for_number(parsed, "en") or "Unknown"
            carrier_name = carrier.name_for_number(parsed, "en") or "Unknown Carrier"
            timezones_list = list(timezone.time_zones_for_number(parsed))

            e164_fmt = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            int_fmt = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            nat_fmt = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)

            wa_link = f"https://wa.me/{e164_fmt.lstrip('+')}"
            tg_link = f"https://t.me/{e164_fmt}"

            yield Finding(
                scan_id=scan_id,
                target=target,
                target_type=TargetType.PHONE,
                category="Telephony & Mobile",
                source="LibPhoneNumber",
                status=FindingStatus.FOUND if is_valid else FindingStatus.INFO,
                title=f"{country_name} ({carrier_name})",
                description=f"Format: {int_fmt} | National: {nat_fmt} | Timezones: {', '.join(timezones_list[:2])}",
                metadata={
                    "is_valid": is_valid,
                    "country": country_name,
                    "carrier": carrier_name,
                    "timezones": timezones_list,
                    "e164": e164_fmt,
                    "international": int_fmt,
                    "national": nat_fmt,
                    "whatsapp_link": wa_link,
                    "telegram_link": tg_link,
                }
            )
        except Exception as e:
            yield Finding(
                scan_id=scan_id,
                target=target,
                target_type=TargetType.PHONE,
                category="Telephony & Mobile",
                source="LibPhoneNumber",
                status=FindingStatus.ERROR,
                title="Phone Parsing Failed",
                description=str(e)
            )
