from fastapi import APIRouter, HTTPException, Response
from sse_starlette.sse import EventSourceResponse
from app.core.database import get_recent_scans, get_scan_findings
from app.core.detector import detect_entity
from app.core.engine import engine
from app.core.models import DetectionResult, Finding, ScanRequest, ScanStatus, ScanSummary, TargetType
from app.core.reporter import generate_csv_report, generate_html_report, generate_json_report

router = APIRouter(prefix="/api/scan", tags=["Scanning"])

@router.post("/detect", response_model=DetectionResult)
async def api_detect_entity(payload: dict):
    query = payload.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    return detect_entity(query)

@router.post("/start")
async def start_scan(req: ScanRequest):
    if not req.target or not req.target.strip():
        raise HTTPException(status_code=400, detail="Target cannot be empty.")
    
    scan_id = await engine.start_scan(req)
    return {"scan_id": scan_id, "status": "started"}

@router.get("/{scan_id}/stream")
async def stream_scan(scan_id: str):
    return EventSourceResponse(engine.stream_scan_events(scan_id))

@router.post("/{scan_id}/stop")
async def stop_scan(scan_id: str):
    success = engine.stop_scan(scan_id)
    return {"scan_id": scan_id, "stopped": success}

@router.get("/{scan_id}/results")
async def get_results(scan_id: str):
    findings = await get_scan_findings(scan_id)
    summary = engine.scan_summaries.get(scan_id)
    return {
        "scan_id": scan_id,
        "summary": summary.model_dump() if summary else None,
        "findings": [f.model_dump() for f in findings]
    }

@router.get("/{scan_id}/export/{format}")
async def export_scan_results(scan_id: str, format: str):
    findings = await get_scan_findings(scan_id)
    summary = engine.scan_summaries.get(scan_id)
    if not summary:
        # Reconstruct summary from findings
        target = findings[0].target if findings else "unknown"
        target_type = findings[0].target_type if findings else TargetType.UNKNOWN
        found_cnt = sum(1 for f in findings if f.status.value == "found")
        not_found_cnt = sum(1 for f in findings if f.status.value == "not_found")
        err_cnt = sum(1 for f in findings if f.status.value in ("error", "rate_limited"))
        summary = ScanSummary(
            scan_id=scan_id,
            target=target,
            target_type=target_type,
            status=ScanStatus.COMPLETED,
            started_at=0,
            total_checks=len(findings),
            found_count=found_cnt,
            not_found_count=not_found_cnt,
            error_count=err_cnt
        )

    fmt = format.lower()
    if fmt == "json":
        content = generate_json_report(summary, findings)
        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=omnitrace_{summary.target}_{scan_id[:6]}.json"}
        )
    elif fmt == "csv":
        content = generate_csv_report(findings)
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=omnitrace_{summary.target}_{scan_id[:6]}.csv"}
        )
    elif fmt in ("html", "pdf"):
        content = generate_html_report(summary, findings)
        return Response(
            content=content,
            media_type="text/html",
            headers={"Content-Disposition": f"inline; filename=omnitrace_{summary.target}_{scan_id[:6]}.html"}
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Supported: json, csv, html")

@router.get("/recent/list")
async def list_recent_scans():
    return await get_recent_scans(limit=25)
