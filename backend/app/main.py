import base64
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes_cases import router as cases_router
from app.api.routes_modules import router as modules_router
from app.api.routes_scan import router as scan_router
from app.api.routes_settings import router as settings_router
from app.config import settings
from app.core.database import init_db

FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables
    await init_db()
    yield
    # Shutdown logic if needed

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Next-generation Open-Source OSINT Intelligence Platform",
    lifespan=lifespan
)

# Frontend is served from the same origin; extra origins only needed for a separate dev host
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def basic_auth(request: Request, call_next):
    if not settings.access_password or request.url.path == "/health":
        return await call_next(request)
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("basic "):
        try:
            user, _, password = base64.b64decode(auth[6:]).decode("utf-8").partition(":")
        except (ValueError, UnicodeDecodeError):
            user, password = "", ""
        if secrets.compare_digest(user.encode(), settings.access_user.encode()) and \
                secrets.compare_digest(password.encode(), settings.access_password.encode()):
            return await call_next(request)
    return Response(
        status_code=401,
        content="Authentication required",
        headers={"WWW-Authenticate": 'Basic realm="OmniTrace", charset="UTF-8"'},
    )

# Mount API Routers
app.include_router(scan_router)
app.include_router(cases_router)
app.include_router(modules_router)
app.include_router(settings_router)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.version,
        "proxy_active": bool(settings.proxy_url)
    }

# Serve Frontend static assets if built
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    dist_root = FRONTEND_DIST.resolve()

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = (dist_root / full_path).resolve()
        # Block path traversal (e.g. /..%2f..%2f.env) outside the dist folder
        if file_path.is_relative_to(dist_root) and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(dist_root / "index.html")
else:
    @app.get("/")
    async def root():
        return {
            "app": "OmniTrace OSINT Platform",
            "docs": "/docs",
            "status": "online"
        }

