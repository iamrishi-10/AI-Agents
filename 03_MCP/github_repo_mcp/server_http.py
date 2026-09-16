from mcp.server.mcpserver import MCPServer

from services.github_service import (
    get_repo_info as fetch_repo_info,
    get_repo_readme as fetch_repo_readme,
    list_issues as fetch_issues,
)

mcp = MCPServer("GitHub Repo MCP HTTP")


@mcp.tool()
async def get_repo_info(owner: str, repo: str) -> dict:
    """Return metadata for a public GitHub repository."""
    return await fetch_repo_info(owner, repo)


@mcp.tool()
async def get_repo_readme(owner: str, repo: str) -> dict:
    """Return the decoded README for a public GitHub repository."""
    return await fetch_repo_readme(owner, repo)


@mcp.tool()
async def list_issues(owner: str, repo: str) -> list[dict]:
    """Return open issues for a public GitHub repository."""
    return await fetch_issues(owner, repo)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
