import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
# .env.example lives in the repo root; also accept backend/.env
load_dotenv(BASE_DIR.parent / ".env")
load_dotenv(BASE_DIR / ".env")
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

    # Public deployment: when set, the whole site requires HTTP Basic Auth
    access_user: str = os.getenv("OMNITRACE_USER", "admin")
    access_password: str | None = os.getenv("OMNITRACE_PASSWORD") or None
    cors_origins: list[str] = [
        o.strip() for o in os.getenv("OMNITRACE_CORS_ORIGINS", "").split(",") if o.strip()
    ]

settings = Settings()
