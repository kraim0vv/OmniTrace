import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "omnitrace.db"

class Settings(BaseModel):
    app_name: str = "OmniTrace OSINT Platform"
    version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    database_url: str = f"sqlite+aiosqlite:///{DB_PATH}"
    
    # OPSEC & Proxy settings
    proxy_url: str | None = os.getenv("OMNITRACE_PROXY", None)
    default_timeout: float = float(os.getenv("OMNITRACE_TIMEOUT", "8.0"))
    max_concurrency: int = int(os.getenv("OMNITRACE_MAX_CONCURRENCY", "20"))
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
    
    # Optional API Keys (Self-hosted flexibility)
    hibp_api_key: str | None = os.getenv("HIBP_API_KEY", None)
    shodan_api_key: str | None = os.getenv("SHODAN_API_KEY", None)
    virustotal_api_key: str | None = os.getenv("VIRUSTOTAL_API_KEY", None)
    hunter_api_key: str | None = os.getenv("HUNTER_API_KEY", None)

settings = Settings()
