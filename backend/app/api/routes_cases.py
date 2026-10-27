from typing import List
from fastapi import APIRouter, HTTPException
from app.core.database import create_case, delete_case, get_all_cases, get_case_by_id, update_case
from app.core.models import Case

router = APIRouter(prefix="/api/cases", tags=["Case Management"])

@router.get("", response_model=List[Case])
async def list_cases():
    return await get_all_cases()

@router.post("", response_model=Case)
async def api_create_case(case: Case):
    return await create_case(case)

@router.get("/{case_id}", response_model=Case)
async def api_get_case(case_id: str):
    c = await get_case_by_id(case_id)
    if not c:
        raise HTTPException(status_code=404, detail="Case not found.")
    return c

@router.put("/{case_id}")
async def api_update_case(case_id: str, payload: dict):
    await update_case(
        case_id=case_id,
        name=payload.get("name", "Untitled Case"),
        description=payload.get("description", ""),
        notes=payload.get("notes", ""),
        targets=payload.get("targets", [])
    )
    return {"status": "updated"}

@router.delete("/{case_id}")
async def api_delete_case(case_id: str):
    await delete_case(case_id)
    return {"status": "deleted"}
