import socket
from typing import AsyncGenerator
import httpx
from app.core.models import Finding, FindingStatus, TargetType
from app.modules.base import BaseModule

class GeoIpModule(BaseModule):
    name = "geo_ip"
    category = "Network & Infrastructure"
    description = "Resolves IP geolocation, Autonomous System (ASN), ISP, and geographic coordinates."
    target_types = [TargetType.IP, TargetType.DOMAIN]
    author = "OmniTrace Core"

    async def run(
        self,
        target: str,
        scan_id: str,
        client: httpx.AsyncClient
    ) -> AsyncGenerator[Finding, None]:
        ip_target = target.strip()

        # If domain, resolve to IP first
        if not ip_target.replace(".", "").isdigit() and ":" not in ip_target:
            try:
                ip_target = socket.gethostbyname(ip_target)
            except Exception as e:
                yield Finding(
                    scan_id=scan_id,
                    target=target,
                    target_type=TargetType.IP,
                    category="Network & Infrastructure",
                    source="GeoIP",
                    status=FindingStatus.ERROR,
                    title="Domain to IP Resolution Failed",
                    description=str(e)
                )
                return

        # Query ip-api.com
        url = f"http://ip-api.com/json/{ip_target}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        try:
            resp = await client.get(url, timeout=6.0)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    country = data.get("country", "Unknown")
                    city = data.get("city", "Unknown")
                    isp = data.get("isp", "Unknown")
                    as_num = data.get("as", "Unknown")
                    lat = data.get("lat")
                    lon = data.get("lon")

                    yield Finding(
                        scan_id=scan_id,
                        target=target,
                        target_type=TargetType.IP,
                        category="Network & Infrastructure",
                        source="IP Geolocation & ASN",
                        status=FindingStatus.FOUND,
                        title=f"{city}, {country} ({ip_target})",
                        description=f"ISP: {isp} | ASN: {as_num} | Coordinates: {lat}, {lon}",
                        metadata={
                            "ip": ip_target,
                            "country": country,
                            "country_code": data.get("countryCode"),
                            "city": city,
                            "isp": isp,
                            "org": data.get("org"),
                            "as": as_num,
                            "lat": lat,
                            "lon": lon,
                            "timezone": data.get("timezone")
                        }
                    )
                    return

            yield Finding(
                scan_id=scan_id,
                target=target,
                target_type=TargetType.IP,
                category="Network & Infrastructure",
                source="GeoIP",
                status=FindingStatus.NOT_FOUND,
                title="IP Location Not Found",
                description=f"Could not determine geolocation for {ip_target}."
            )
        except Exception as e:
            yield Finding(
                scan_id=scan_id,
                target=target,
                target_type=TargetType.IP,
                category="Network & Infrastructure",
                source="GeoIP",
                status=FindingStatus.ERROR,
                title="GeoIP Query Failed",
                description=str(e)
            )
