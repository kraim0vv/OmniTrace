import asyncio
import base64

import pytest

from app.core.database import save_finding, save_scan_start
from app.core.models import Finding, FindingStatus, ScanStatus, ScanSummary, TargetType
from app.main import FRONTEND_DIST


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@pytest.mark.skipif(not FRONTEND_DIST.exists(), reason="frontend not built")
@pytest.mark.parametrize("path", [
    "/..%2f..%2fbackend%2frequirements.txt",
    "/%2e%2e/%2e%2e/backend/requirements.txt",
])
def test_spa_blocks_path_traversal(client, path):
    resp = client.get(path)
    assert resp.status_code == 200
    assert "fastapi" not in resp.text
    assert "<!doctype html>" in resp.text.lower()


def test_settings_validation(client, restore_settings):
    assert client.post("/api/settings", json={"proxy_url": "ftp://x"}).status_code == 400
    assert client.post("/api/settings", json={"default_timeout": -1}).status_code == 422
    resp = client.post("/api/settings", json={"proxy_url": "socks5://127.0.0.1:9050", "default_timeout": "5"})
    assert resp.status_code == 200
    assert restore_settings.proxy_url == "socks5://127.0.0.1:9050"
    assert restore_settings.default_timeout == 5.0


def test_basic_auth(client, restore_settings):
    restore_settings.access_password = "s3cret"
    assert client.get("/api/modules").status_code == 401
    assert client.get("/health").status_code == 200
    bad = base64.b64encode(b"admin:wrong").decode()
    good = base64.b64encode(b"admin:s3cret").decode()
    assert client.get("/api/modules", headers={"Authorization": f"Basic {bad}"}).status_code == 401
    assert client.get("/api/modules", headers={"Authorization": "Basic !!!"}).status_code == 401
    assert client.get("/api/modules", headers={"Authorization": f"Basic {good}"}).status_code == 200


def test_too_many_active_scans(client, restore_settings):
    restore_settings.max_active_scans = 0
    resp = client.post("/api/scan/start", json={"target": "torvalds"})
    assert resp.status_code == 429


def test_target_length_limit(client):
    assert client.post("/api/scan/start", json={"target": "a" * 600}).status_code == 422


def test_export_with_non_latin_target(client):
    scan_id = "export-test-scan"
    target = "тест<script>"

    async def seed():
        await save_scan_start(ScanSummary(
            scan_id=scan_id, target=target, target_type=TargetType.USERNAME,
            status=ScanStatus.COMPLETED, started_at=0,
        ), None)
        await save_finding(Finding(
            scan_id=scan_id, target=target, target_type=TargetType.USERNAME,
            category="Social", source="Example", status=FindingStatus.FOUND,
            title=target, url="https://example.com",
        ))

    asyncio.run(seed())
    for fmt in ("html", "json", "csv"):
        resp = client.get(f"/api/scan/{scan_id}/export/{fmt}")
        assert resp.status_code == 200, fmt
        disposition = resp.headers["content-disposition"]
        disposition.encode("latin-1")
        assert "<" not in disposition
    assert "<script>" not in client.get(f"/api/scan/{scan_id}/export/html").text
    assert client.get(f"/api/scan/{scan_id}/export/xml").status_code == 400
