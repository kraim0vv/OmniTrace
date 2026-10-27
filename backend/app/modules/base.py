from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Optional
import httpx
from app.core.models import Finding, TargetType

class BaseModule(ABC):
    name: str = "BaseModule"
    category: str = "General"
    description: str = "Base OSINT Module"
    target_types: List[TargetType] = []
    requires_api_key: Optional[str] = None
    author: str = "OmniTrace Core"

    @abstractmethod
    async def run(
        self,
        target: str,
        scan_id: str,
        client: httpx.AsyncClient
    ) -> AsyncGenerator[Finding, None]:
        """
        Executes the module asynchronously and yields Findings as they are discovered.
        """
        yield
