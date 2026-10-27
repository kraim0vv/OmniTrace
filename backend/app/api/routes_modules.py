from fastapi import APIRouter
from app.core.engine import engine

router = APIRouter(prefix="/api/modules", tags=["Modules"])

@router.get("")
async def list_modules():
    return engine.get_available_modules()
