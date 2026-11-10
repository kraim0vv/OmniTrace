from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
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

class SettingsUpdate(BaseModel):
    proxy_url: Optional[str] = None
    default_timeout: Optional[float] = Field(default=None, gt=0, le=120)
    hibp_api_key: Optional[str] = None
    shodan_api_key: Optional[str] = None
    virustotal_api_key: Optional[str] = None


@router.post("")
async def update_settings(payload: SettingsUpdate):
    if payload.proxy_url is not None:
        proxy = payload.proxy_url.strip()
        if proxy and not proxy.startswith(("http://", "https://", "socks5://", "socks5h://")):
            raise HTTPException(status_code=400, detail="Proxy must start with http://, https://, socks5:// or socks5h://")
        settings.proxy_url = proxy or None
    if payload.default_timeout is not None:
        settings.default_timeout = payload.default_timeout
    for key in ("hibp_api_key", "shodan_api_key", "virustotal_api_key"):
        value = getattr(payload, key)
        if value and value.strip():
            setattr(settings, key, value.strip())

    return {"status": "saved", "message": "Settings updated successfully."}
