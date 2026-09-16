import asyncio

from mcp import Client

SERVER_URL = "http://127.0.0.1:8000/mcp"


async def main() -> None:
    async with Client(SERVER_URL) as client:
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
