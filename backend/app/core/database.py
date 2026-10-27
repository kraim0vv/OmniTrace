import asyncio
import json
import sqlite3
import aiosqlite
from typing import Any, Dict, List, Optional
from app.config import DB_PATH
from app.core.models import Case, Finding, FindingStatus, ScanStatus, ScanSummary, TargetType

db_lock = asyncio.Lock()

async def init_db():
    async with aiosqlite.connect(DB_PATH, timeout=15.0) as db:
        await db.execute("PRAGMA journal_mode = WAL;")
        await db.execute("PRAGMA busy_timeout = 10000;")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                targets TEXT DEFAULT '[]',
                notes TEXT DEFAULT '',
                findings_count INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                scan_id TEXT PRIMARY KEY,
                case_id TEXT,
                target TEXT NOT NULL,
                target_type TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at REAL NOT NULL,
                ended_at REAL,
                total_checks INTEGER DEFAULT 0,
                found_count INTEGER DEFAULT 0,
                not_found_count INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS findings (
                id TEXT PRIMARY KEY,
                scan_id TEXT NOT NULL,
                target TEXT NOT NULL,
                target_type TEXT NOT NULL,
                category TEXT NOT NULL,
                source TEXT NOT NULL,
                status TEXT NOT NULL,
                url TEXT,
                title TEXT,
                description TEXT,
                metadata TEXT DEFAULT '{}',
                timestamp REAL NOT NULL,
                FOREIGN KEY (scan_id) REFERENCES scans (scan_id) ON DELETE CASCADE
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        await db.commit()

# Case Operations
async def get_all_cases() -> List[Case]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM cases ORDER BY updated_at DESC") as cursor:
            rows = await cursor.fetchall()
            return [
                Case(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"] or "",
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    targets=json.loads(row["targets"] or "[]"),
                    notes=row["notes"] or "",
                    findings_count=row["findings_count"] or 0
                )
                for row in rows
            ]

async def create_case(case: Case) -> Case:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO cases (id, name, description, created_at, updated_at, targets, notes, findings_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                case.id,
                case.name,
                case.description,
                case.created_at,
                case.updated_at,
                json.dumps(case.targets),
                case.notes,
                case.findings_count
            )
        )
        await db.commit()
    return case

async def get_case_by_id(case_id: str) -> Optional[Case]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM cases WHERE id = ?", (case_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None
            return Case(
                id=row["id"],
                name=row["name"],
                description=row["description"] or "",
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                targets=json.loads(row["targets"] or "[]"),
                notes=row["notes"] or "",
                findings_count=row["findings_count"] or 0
            )

async def update_case(case_id: str, name: str, description: str, notes: str, targets: List[str]):
    import time
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            UPDATE cases
            SET name = ?, description = ?, notes = ?, targets = ?, updated_at = ?
            WHERE id = ?
            """,
            (name, description, notes, json.dumps(targets), time.time(), case_id)
        )
        await db.commit()

async def delete_case(case_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM cases WHERE id = ?", (case_id,))
        await db.commit()

# Scan & Findings Operations
async def save_scan_start(scan: ScanSummary, case_id: Optional[str] = None):
    async with db_lock:
        async with aiosqlite.connect(DB_PATH, timeout=15.0) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO scans (scan_id, case_id, target, target_type, status, started_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (scan.scan_id, case_id, scan.target, scan.target_type.value, scan.status.value, scan.started_at)
            )
            await db.commit()

async def update_scan_finish(scan: ScanSummary):
    async with db_lock:
        async with aiosqlite.connect(DB_PATH, timeout=15.0) as db:
            await db.execute(
                """
                UPDATE scans
                SET status = ?, ended_at = ?, total_checks = ?, found_count = ?, not_found_count = ?, error_count = ?
                WHERE scan_id = ?
                """,
                (
                    scan.status.value,
                    scan.ended_at,
                    scan.total_checks,
                    scan.found_count,
                    scan.not_found_count,
                    scan.error_count,
                    scan.scan_id
                )
            )
            await db.commit()

async def save_finding(finding: Finding):
    async with db_lock:
        async with aiosqlite.connect(DB_PATH, timeout=15.0) as db:
            await db.execute(
                """
                INSERT INTO findings (id, scan_id, target, target_type, category, source, status, url, title, description, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    finding.id,
                    finding.scan_id,
                    finding.target,
                    finding.target_type.value,
                    finding.category,
                    finding.source,
                    finding.status.value,
                    finding.url,
                    finding.title,
                    finding.description,
                    json.dumps(finding.metadata),
                    finding.timestamp
                )
            )
            await db.commit()

async def get_scan_findings(scan_id: str) -> List[Finding]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM findings WHERE scan_id = ? ORDER BY timestamp ASC", (scan_id,)) as cursor:
            rows = await cursor.fetchall()
            return [
                Finding(
                    id=row["id"],
                    scan_id=row["scan_id"],
                    target=row["target"],
                    target_type=TargetType(row["target_type"]),
                    category=row["category"],
                    source=row["source"],
                    status=FindingStatus(row["status"]),
                    url=row["url"],
                    title=row["title"],
                    description=row["description"],
                    metadata=json.loads(row["metadata"] or "{}"),
                    timestamp=row["timestamp"]
                )
                for row in rows
            ]

async def get_recent_scans(limit: int = 20) -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM scans ORDER BY started_at DESC LIMIT ?", (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
