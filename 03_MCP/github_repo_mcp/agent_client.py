import asyncio
import json
import sys

from mcp import Client, StdioServerParameters
from openai import AsyncOpenAI

from config.settings import MAX_RETRIES, MAX_ROUNDS, MODEL, openai_api_key

HTTP_SERVER_URL = "http://127.0.0.1:8000/mcp"

client = AsyncOpenAI(api_key=openai_api_key)


def build_server_target(transport: str):
    """Return what Client() should connect to for the given transport."""
    if transport == "http":
        return HTTP_SERVER_URL

    if transport == "stdio":
        return StdioServerParameters(
            command=sys.executable,
            args=["server_stdio.py"],
        )

    raise ValueError(f"Unknown transport '{transport}'. Use 'stdio' or 'http'.")


def convert_mcp_tools_to_openai(mcp_tools) -> list[dict]:
    """Convert MCP tool definitions into OpenAI function-tool schemas."""
    return [
        {
            "type": "function",
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.input_schema,
            "strict": False,
        }
        for tool in mcp_tools
    ]


def mcp_result_to_json(result) -> str:
    """Serialize an MCP CallToolResult into a JSON string the LLM can consume."""
    if result.structured_content is not None:
        return json.dumps(result.structured_content, ensure_ascii=False)

    content = [block.text for block in result.content if hasattr(block, "text")]

    return json.dumps({"content": content}, ensure_ascii=False)


async def ask_llm(user_prompt: str, tools: list[dict]):
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return await client.responses.create(
                model=MODEL,
                instructions=(
                    "You are a GitHub repository assistant. "
                    "Use the available tools whenever live GitHub data is required. "
                    "Do not invent repository information."
                ),
                input=user_prompt,
                tools=tools,
            )
        except Exception as exc:
            last_error = exc
            print(f"LLM call failed (attempt {attempt}/{MAX_RETRIES}): {exc}")

    raise last_error


async def run_agent(
    user_prompt: str,
    mcp_client,
    tools: list[dict],
) -> str:
    """Run the bounded LLM <-> MCP tool-calling loop and return the final answer."""
    response = await ask_llm(user_prompt, tools)

    for _ in range(MAX_ROUNDS):
        function_calls = [
            item for item in response.output if item.type == "function_call"
        ]

        if not function_calls:
            return response.output_text

        tool_outputs = []

        for call in function_calls:
            arguments = json.loads(call.arguments)
            result = await mcp_client.call_tool(call.name, arguments)

            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": mcp_result_to_json(result),
                }
            )

        response = await client.responses.create(
            model=MODEL,
            previous_response_id=response.id,
            input=tool_outputs,
            tools=tools,
        )

    raise RuntimeError(
        "Maximum MCP tool rounds reached without a final answer."
    )


async def main() -> None:
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    server = build_server_target(transport)

    print(f"Connecting over {transport} transport...")

    async with Client(server) as mcp_client:
        discovered = await mcp_client.list_tools()
        tools = convert_mcp_tools_to_openai(discovered.tools)

        while True:
            user_prompt = input("\nYou: ").strip()
            if user_prompt.lower() in {"quit", "exit"}:
                break

            answer = await run_agent(user_prompt, mcp_client, tools)
            print(f"\nAssistant: {answer}")


if __name__ == "__main__":
    asyncio.run(main())
