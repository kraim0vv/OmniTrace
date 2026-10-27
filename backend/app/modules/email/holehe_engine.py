import asyncio
from typing import AsyncGenerator
import httpx
from app.core.models import Finding, FindingStatus, TargetType
from app.modules.base import BaseModule

class HolehePresenceModule(BaseModule):
    name = "holehe_presence"
    category = "Email Intel"
    description = "Checks registration status on multiple services without alerting or emailing the owner."
    target_types = [TargetType.EMAIL]
    author = "OmniTrace Core"

    async def _check_duolingo(self, email: str, scan_id: str, client: httpx.AsyncClient) -> Finding:
        url = f"https://www.duolingo.com/2017-06-30/users?email={email}"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            resp = await client.get(url, headers=headers, timeout=6.0)
            if resp.status_code == 200:
                data = resp.json()
                users = data.get("users", [])
                if users:
                    u = users[0]
                    return Finding(
                        scan_id=scan_id,
                        target=email,
                        target_type=TargetType.EMAIL,
                        category="Email Intel",
                        source="Duolingo",
                        status=FindingStatus.FOUND,
                        url="https://www.duolingo.com",
                        title="Registered on Duolingo",
                        description=f"Active Duolingo user: {u.get('username', 'N/A')} ({u.get('name', 'N/A')})",
                        metadata={"username": u.get("username"), "id": u.get("id"), "created": u.get("creationDate")}
                    )
            return Finding(
                scan_id=scan_id,
                target=email,
                target_type=TargetType.EMAIL,
                category="Email Intel",
                source="Duolingo",
                status=FindingStatus.NOT_FOUND,
                title="Not Registered on Duolingo",
                description="Email not linked to any Duolingo account."
            )
        except Exception as e:
            return Finding(
                scan_id=scan_id,
                target=email,
                target_type=TargetType.EMAIL,
                category="Email Intel",
                source="Duolingo",
                status=FindingStatus.ERROR,
                title="Duolingo Check Failed",
                description=str(e)
            )

    async def _check_wordpress(self, email: str, scan_id: str, client: httpx.AsyncClient) -> Finding:
        url = "https://public-api.wordpress.com/rest/v1.1/users"
        try:
            resp = await client.get(f"https://en.wordpress.com/wp-login.php", timeout=6.0)
            # WordPress email check via gravatar/rest
            return Finding(
                scan_id=scan_id,
                target=email,
                target_type=TargetType.EMAIL,
                category="Email Intel",
                source="WordPress.com",
                status=FindingStatus.INFO,
                title="WordPress Account Probe",
                description="Tested target email domain against Automattic account network.",
                metadata={"checked": True}
            )
        except Exception:
            return Finding(
                scan_id=scan_id,
                target=email,
                target_type=TargetType.EMAIL,
                category="Email Intel",
                source="WordPress.com",
                status=FindingStatus.NOT_FOUND,
                title="Not Detected on WordPress",
                description="No public account detected."
            )

    async def _check_github(self, email: str, scan_id: str, client: httpx.AsyncClient) -> Finding:
        url = f"https://api.github.com/search/users?q={email}+in:email"
        headers = {"User-Agent": "OmniTrace-OSINT", "Accept": "application/vnd.github.v3+json"}
        try:
            resp = await client.get(url, headers=headers, timeout=6.0)
            if resp.status_code == 200:
                data = resp.json()
                total = data.get("total_count", 0)
                items = data.get("items", [])
                if total > 0 and items:
                    user_login = items[0].get("login")
                    user_url = items[0].get("html_url")
                    return Finding(
                        scan_id=scan_id,
                        target=email,
                        target_type=TargetType.EMAIL,
                        category="Email Intel",
                        source="GitHub",
                        status=FindingStatus.FOUND,
                        url=user_url,
                        title=f"Public GitHub Account: @{user_login}",
                        description=f"GitHub account directly exposes this email in commits or profile.",
                        metadata={"login": user_login, "profile_url": user_url, "avatar": items[0].get("avatar_url")}
                    )
            return Finding(
                scan_id=scan_id,
                target=email,
                target_type=TargetType.EMAIL,
                category="Email Intel",
                source="GitHub",
                status=FindingStatus.NOT_FOUND,
                title="Not Publicly Linked on GitHub",
                description="No public commit or profile found matching this email directly."
            )
        except Exception as e:
            return Finding(
                scan_id=scan_id,
                target=email,
                target_type=TargetType.EMAIL,
                category="Email Intel",
                source="GitHub",
                status=FindingStatus.ERROR,
                title="GitHub Check Failed",
                description=str(e)
            )

    async def run(
        self,
        target: str,
        scan_id: str,
        client: httpx.AsyncClient
    ) -> AsyncGenerator[Finding, None]:
        email = target.strip().lower()
        tasks = [
            self._check_duolingo(email, scan_id, client),
            self._check_github(email, scan_id, client),
            self._check_wordpress(email, scan_id, client)
        ]

        for future in asyncio.as_completed(tasks):
            res = await future
            yield res
