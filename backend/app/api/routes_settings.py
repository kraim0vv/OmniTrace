from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/api/settings", tags=["Settings & OPSEC"])

@router.get("")
async def get_settings():
    return {
        "proxy_url": settings.proxy_url or "",
        "default_timeout": settings.default_timeout,
        "max_concurrency": settings.max_concurrency,
        "user_agent": settings.user_agent,
        "hibp_api_key_set": bool(settings.hibp_api_key),
        "shodan_api_key_set": bool(settings.shodan_api_key),
        "virustotal_api_key_set": bool(settings.virustotal_api_key),
        "hunter_api_key_set": bool(settings.hunter_api_key),
    }

@router.post("")
async def update_settings(payload: dict):
    if "proxy_url" in payload:
        settings.proxy_url = payload["proxy_url"].strip() or None
    if "default_timeout" in payload:
        try:
            settings.default_timeout = float(payload["default_timeout"])
        except ValueError:
            pass
    if "hibp_api_key" in payload and payload["hibp_api_key"]:
        settings.hibp_api_key = payload["hibp_api_key"].strip()
    if "shodan_api_key" in payload and payload["shodan_api_key"]:
        settings.shodan_api_key = payload["shodan_api_key"].strip()
    if "virustotal_api_key" in payload and payload["virustotal_api_key"]:
        settings.virustotal_api_key = payload["virustotal_api_key"].strip()

    return {"status": "saved", "message": "Settings updated successfully."}
