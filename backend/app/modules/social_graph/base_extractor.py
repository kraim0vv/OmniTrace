"""
OmniTrace Social Graph Mapping — Abstract Base Extractor
=========================================================
Provides an asynchronous, resilient, rate-limited foundation for platform-specific
social graph extractors (VK, Telegram, Instagram, etc.).

Features:
- Connection pooling with aiohttp.TCPConnector.
- Automatic exponential backoff with randomized jitter on HTTP 429/5xx.
- Adaptive rate throttling and request concurrency control.
- Clean lifecycle management via async context managers.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
import logging
import random
from typing import Any, Dict, Optional
import aiohttp
from yarl import URL

from app.modules.social_graph.models import ExtractionResult, PlatformType, ProfileNode

logger = logging.getLogger("omnitrace.social_graph.extractor")


class ExtractorRateLimitError(Exception):
    """Raised when request attempts exceed maximum backoff retries."""
    pass


class BaseExtractor(ABC):
    """
    Abstract Base Class for all social graph extractors.
    
    Subclasses implement extraction of target profiles and their friend/follower
    networks for a specific platform using native APIs or structured endpoints.
    """

    def __init__(
        self,
        platform: PlatformType,
        concurrency_limit: int = 5,
        rate_limit_delay: float = 0.5,
        max_retries: int = 4,
        backoff_factor: float = 2.0,
        request_timeout: float = 12.0,
        proxy_url: Optional[str] = None
    ) -> None:
        """
        Initializes the async extractor infrastructure.

        Args:
            platform: PlatformType enum handled by this extractor.
            concurrency_limit: Maximum concurrent network requests.
            rate_limit_delay: Minimum delay between consecutive requests (seconds).
            max_retries: Number of backoff attempts on 429 or transient errors.
            backoff_factor: Multiplier for exponential backoff.
            request_timeout: Timeout in seconds for individual HTTP requests.
            proxy_url: Optional upstream SOCKS5/HTTP proxy for OPSEC.
        """
        self.platform = platform
        self.concurrency_limit = concurrency_limit
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.request_timeout = request_timeout
        self.proxy_url = proxy_url

        self._session: Optional[aiohttp.ClientSession] = None
        self._semaphore: asyncio.Semaphore = asyncio.Semaphore(self.concurrency_limit)
        self._last_request_time: float = 0.0
        self._rate_lock: asyncio.Lock = asyncio.Lock()

    async def initialize(self) -> None:
        """
        Instantiates the aiohttp ClientSession with tuned TCP connection pooling.
        """
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=self.concurrency_limit * 2,
                limit_per_host=self.concurrency_limit,
                ttl_dns_cache=300,
                enable_cleanup_closed=True,
                ssl=False  # Avoid fatal SSL failures on custom target certs
            )
            timeout = aiohttp.ClientTimeout(total=self.request_timeout)
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json, text/html, */*",
                "Accept-Language": "en-US,en;q=0.9",
            }
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=headers
            )
            logger.debug(f"[{self.platform.value}] ClientSession initialized with pool limit {self.concurrency_limit}")

    async def close(self) -> None:
        """
        Gracefully closes the connection pool and underlying transports.
        """
        if self._session and not self._session.closed:
            await self._session.close()
            # Allow underlying SSL transports to terminate gracefully
            await asyncio.sleep(0.05)
            self._session = None
            logger.debug(f"[{self.platform.value}] ClientSession closed.")

    async def __aenter__(self) -> BaseExtractor:
        await self.initialize()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def _rate_limit_throttle(self) -> None:
        """
        Enforces a minimum time delta between consecutive calls to avoid triggering
        defensive platform anti-scraping / WAF rate limits.
        """
        async with self._rate_lock:
            loop = asyncio.get_running_loop()
            now = loop.time()
            elapsed = now - self._last_request_time
            if elapsed < self.rate_limit_delay:
                wait_time = self.rate_limit_delay - elapsed
                await asyncio.sleep(wait_time)
            self._last_request_time = loop.time()

    async def _execute_request(
        self,
        method: str,
        url: str | URL,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> aiohttp.ClientResponse:
        """
        Executes a managed asynchronous HTTP request with semaphore concurrency,
        rate-limiting delays, and exponential backoff on HTTP 429 or 5xx errors.

        Returns:
            aiohttp.ClientResponse: The active response object.

        Raises:
            ExtractorRateLimitError: If max backoff retries are exhausted.
            aiohttp.ClientError: On irrecoverable network faults.
        """
        if self._session is None or self._session.closed:
            await self.initialize()

        assert self._session is not None

        attempt = 0
        while attempt <= self.max_retries:
            await self._semaphore.acquire()
            try:
                await self._rate_limit_throttle()
                logger.debug(f"[{self.platform.value}] {method} -> {url} (Attempt {attempt + 1})")

                req_kwargs: Dict[str, Any] = {
                    "params": params,
                    "headers": headers,
                    "proxy": self.proxy_url,
                    **kwargs
                }
                if json_data is not None:
                    req_kwargs["json"] = json_data

                response = await self._session.request(method, url, **req_kwargs)

                # Handle Rate Limiting (429) and Server Overload (502/503/504)
                if response.status in (429, 502, 503, 504):
                    response.close()
                    attempt += 1
                    if attempt > self.max_retries:
                        raise ExtractorRateLimitError(
                            f"[{self.platform.value}] Max retries exceeded for {url}. Last HTTP: {response.status}"
                        )

                    # Compute exponential backoff with randomized jitter
                    jitter = random.uniform(0.1, 0.8)
                    backoff = (self.backoff_factor ** attempt) + jitter
                    logger.warning(
                        f"[{self.platform.value}] HTTP {response.status} from {url}. Backing off for {backoff:.2f}s..."
                    )
                    await asyncio.sleep(backoff)
                    continue

                return response

            except (aiohttp.ClientConnectorError, aiohttp.ServerTimeoutError, asyncio.TimeoutError) as net_err:
                attempt += 1
                if attempt > self.max_retries:
                    logger.error(f"[{self.platform.value}] Fatal network error querying {url}: {net_err}")
                    raise
                backoff = (self.backoff_factor ** attempt) + random.uniform(0.2, 0.5)
                logger.warning(f"[{self.platform.value}] Transient network error ({net_err}). Retrying in {backoff:.2f}s...")
                await asyncio.sleep(backoff)
            finally:
                self._semaphore.release()

        raise ExtractorRateLimitError(f"[{self.platform.value}] Request failed after {self.max_retries} attempts.")

    @abstractmethod
    def can_handle(self, seed: str) -> bool:
        """
        Inspects an input seed (URL, handle, or URN) and determines whether
        this extractor is capable of processing it.

        Args:
            seed: Target URL or handle (e.g. 'https://vk.com/id12345').
        """
        pass

    @abstractmethod
    async def extract_profile(self, seed: str) -> ProfileNode:
        """
        Extracts foundational profile information for the given seed.

        Args:
            seed: Normalized profile identifier or URL.

        Returns:
            ProfileNode: Structured profile data model.
        """
        pass

    @abstractmethod
    async def extract_connections(
        self,
        profile: ProfileNode,
        limit: Optional[int] = None
    ) -> ExtractionResult:
        """
        Retrieves friend lists, followers, mutual connections, or group links
        associated with the seed ProfileNode.

        Args:
            profile: Seed ProfileNode object.
            limit: Optional ceiling on the number of connections to harvest.

        Returns:
            ExtractionResult: Contains list of connected ProfileNodes and RelationshipEdges.
        """
        pass
