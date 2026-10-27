import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class TargetType(str, Enum):
    USERNAME = "username"
    EMAIL = "email"
    PHONE = "phone"
    DOMAIN = "domain"
    IP = "ip"
    HASH = "hash"
    UNKNOWN = "unknown"

class FindingStatus(str, Enum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    INFO = "info"

class ScanStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    STOPPED = "stopped"
    FAILED = "failed"

class DetectionResult(BaseModel):
    raw_query: str
    detected_type: TargetType
    confidence: float
    normalized_value: str
    recommended_modules: List[str]
    details: Dict[str, Any] = Field(default_factory=dict)

class Finding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scan_id: str
    target: str
    target_type: TargetType
    category: str  # Social, Code, Gaming, Email, DNS, WHOIS, Telecom, Leak, etc.
    source: str    # GitHub, Holehe:Twitter, DNS:MX, crt.sh, etc.
    status: FindingStatus
    url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)

class ScanRequest(BaseModel):
    target: str
    target_type: Optional[TargetType] = None
    modules: Optional[List[str]] = None
    case_id: Optional[str] = None
    proxy: Optional[str] = None

class ScanSummary(BaseModel):
    scan_id: str
    target: str
    target_type: TargetType
    status: ScanStatus
    started_at: float
    ended_at: Optional[float] = None
    total_checks: int = 0
    found_count: int = 0
    not_found_count: int = 0
    error_count: int = 0
    findings: List[Finding] = Field(default_factory=list)

class Case(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = ""
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    targets: List[str] = Field(default_factory=list)
    notes: Optional[str] = ""
    findings_count: int = 0
