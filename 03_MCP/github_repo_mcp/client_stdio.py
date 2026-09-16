import asyncio
import sys

from mcp import Client, StdioServerParameters


async def main() -> None:
    server = StdioServerParameters(
        command=sys.executable,
        args=["server_stdio.py"],
    )

    async with Client(server) as client:
        print("Connected to:", client.server_info)

        tools = await client.list_tools()

        print("\nAvailable tools:")
        for tool in tools.tools:
            print(f"- {tool.name}: {tool.description}")

        while True:
            owner = input("\nOwner (or 'quit'): ").strip()
            if owner.lower() in {"quit", "exit"}:
                break

            repo = input("Repo: ").strip()

            for tool in tools.tools:
                result = await client.call_tool(
                    tool.name,
                    {"owner": owner, "repo": repo},
                )
                print(f"\n--- {tool.name} ---")
                if result.structured_content is not None:
                    print(result.structured_content)
                else:
                    for block in result.content:
                        print(getattr(block, "text", block))


if __name__ == "__main__":
    asyncio.run(main())
