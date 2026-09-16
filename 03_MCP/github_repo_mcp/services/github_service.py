"""Client for the GitHub REST API."""

import base64

import httpx

from config.settings import GITHUB_API_BASE_URL

TIMEOUT_SECONDS = 15.0


class GitHubServiceError(Exception):
    """Raised when a GitHub API request fails."""





async def get_repo_info(owner: str, repo: str) -> dict:
    """Fetch selected repository metadata from the GitHub REST API."""
    url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo}"

    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, follow_redirects=True) as client:
        try:
            response = await client.get(url)
        except httpx.RequestError as exc:
            raise GitHubServiceError(f"Failed to reach GitHub API: {exc}") from exc

    if response.status_code == 404:
        raise GitHubServiceError(f"Repository '{owner}/{repo}' not found.")

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise GitHubServiceError(
            f"GitHub API request failed with status {response.status_code}"
        ) from exc

    data = response.json()

    return {
        "name": data["name"],
        "full_name": data["full_name"],
        "description": data["description"],
        "url": data["html_url"],
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "open_issues": data["open_issues_count"],
        "default_branch": data["default_branch"],
        "language": data["language"],
    }




async def get_repo_readme(owner: str, repo: str) -> dict:
    """Fetch and decode the README from the GitHub REST API."""
    url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo}/readme"

    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, follow_redirects=True) as client:
        try:
            response = await client.get(url)
        except httpx.RequestError as exc:
            raise GitHubServiceError(f"Failed to reach GitHub API: {exc}") from exc

    if response.status_code == 404:
        raise GitHubServiceError(
            f"Repository '{owner}/{repo}' has no README, or does not exist."
        )

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise GitHubServiceError(
            f"GitHub API request failed with status {response.status_code}"
        ) from exc

    data = response.json()
    content = base64.b64decode(data["content"]).decode("utf-8")

    return {
        "name": data["name"],
        "path": data["path"],
        "url": data["html_url"],
        "content": content,
    }


MAX_ISSUE_PAGES = 5


async def list_issues(owner: str, repo: str, limit: int = 30) -> list[dict]:
    """Fetch open issues for a repository from the GitHub REST API.

    GitHub's /issues endpoint mixes pull requests in with real issues, sorted
    by most recent activity. A single page can be entirely pull requests for
    an active repo even though it has real open issues, so this paginates
    (up to MAX_ISSUE_PAGES) until `limit` real issues are collected or the
    repository runs out of pages.
    """
    issues: list[dict] = []

    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, follow_redirects=True) as client:
        for page in range(1, MAX_ISSUE_PAGES + 1):
            if len(issues) >= limit:
                break

            url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo}/issues"

            try:
                response = await client.get(url, params={"per_page": 100, "page": page})
            except httpx.RequestError as exc:
                raise GitHubServiceError(f"Failed to reach GitHub API: {exc}") from exc

            if response.status_code == 404:
                raise GitHubServiceError(f"Repository '{owner}/{repo}' not found.")

            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise GitHubServiceError(
                    f"GitHub API request failed with status {response.status_code}"
                ) from exc

            data = response.json()
            if not data:
                break

            issues.extend(
                {
                    "number": item["number"],
                    "title": item["title"],
                    "state": item["state"],
                    "url": item["html_url"],
                    "author": item["user"]["login"],
                    "created_at": item["created_at"],
                    "comments": item["comments"],
                }
                for item in data
                if "pull_request" not in item
            )

    return issues[:limit]




