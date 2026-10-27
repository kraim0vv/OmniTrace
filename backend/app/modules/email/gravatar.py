import hashlib
from typing import AsyncGenerator
import httpx
from app.core.models import Finding, FindingStatus, TargetType
from app.modules.base import BaseModule

class GravatarModule(BaseModule):
    name = "gravatar"
    category = "Email Intel"
    description = "Checks Gravatar for linked profiles, avatars, bios, and account identities."
    target_types = [TargetType.EMAIL]
    author = "OmniTrace Core"

    async def run(
        self,
        target: str,
        scan_id: str,
        client: httpx.AsyncClient
    ) -> AsyncGenerator[Finding, None]:
        email_clean = target.strip().lower()
        email_hash_md5 = hashlib.md5(email_clean.encode("utf-8")).hexdigest()
        email_hash_sha256 = hashlib.sha256(email_clean.encode("utf-8")).hexdigest()

        # Check Gravatar JSON profile
        profile_url = f"https://en.gravatar.com/{email_hash_md5}.json"
        avatar_url = f"https://www.gravatar.com/avatar/{email_hash_md5}?d=404"

        try:
            resp = await client.get(profile_url, timeout=6.0, follow_redirects=True)
            if resp.status_code == 200:
                data = resp.json()
                entry = data.get("entry", [{}])[0]
                display_name = entry.get("displayName", "")
                about_me = entry.get("aboutMe", "")
                photos = [p.get("value") for p in entry.get("photos", []) if p.get("value")]
                verified_accounts = [
                    f"{a.get('shortname')}: {a.get('url')}"
                    for a in entry.get("verifiedAccounts", [])
                ]
                profile_page = entry.get("profileUrl", f"https://gravatar.com/{email_hash_md5}")

                yield Finding(
                    scan_id=scan_id,
                    target=target,
                    target_type=TargetType.EMAIL,
                    category="Email Intel",
                    source="Gravatar Profile",
                    status=FindingStatus.FOUND,
                    url=profile_page,
                    title=f"Gravatar Profile Found: {display_name or email_clean}",
                    description=about_me or f"Active Gravatar with {len(verified_accounts)} linked accounts.",
                    metadata={
                        "display_name": display_name,
                        "avatar": photos[0] if photos else avatar_url,
                        "verified_accounts": verified_accounts,
                        "md5": email_hash_md5,
                        "sha256": email_hash_sha256,
                    }
                )
                return

            # Check avatar image if profile json was 404
            avatar_resp = await client.head(avatar_url, timeout=5.0)
            if avatar_resp.status_code == 200:
                yield Finding(
                    scan_id=scan_id,
                    target=target,
                    target_type=TargetType.EMAIL,
                    category="Email Intel",
                    source="Gravatar Avatar",
                    status=FindingStatus.FOUND,
                    url=avatar_url,
                    title="Gravatar Avatar Registered",
                    description="User has an avatar image associated with this email address.",
                    metadata={"avatar_url": avatar_url, "md5": email_hash_md5}
                )
            else:
                yield Finding(
                    scan_id=scan_id,
                    target=target,
                    target_type=TargetType.EMAIL,
                    category="Email Intel",
                    source="Gravatar",
                    status=FindingStatus.NOT_FOUND,
                    title="No Gravatar Found",
                    description="No avatar or public profile registered for this address.",
                    metadata={"md5": email_hash_md5}
                )
        except Exception as e:
            yield Finding(
                scan_id=scan_id,
                target=target,
                target_type=TargetType.EMAIL,
                category="Email Intel",
                source="Gravatar",
                status=FindingStatus.ERROR,
                title="Gravatar Check Failed",
                description=str(e),
                metadata={"error": str(e)}
            )
