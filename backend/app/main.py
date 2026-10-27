from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
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

# Enable CORS for local dev and docker setups
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
else:
    @app.get("/")
    async def root():
        return {
            "app": "OmniTrace OSINT Platform",
            "docs": "/docs",
            "status": "online"
        }

