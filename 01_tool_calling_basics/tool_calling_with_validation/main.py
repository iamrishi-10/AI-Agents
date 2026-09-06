"""Multi-tool assistant with a reliability-focused tool execution layer."""

import os
import json
import uuid
from unittest.mock import patch

from dotenv import load_dotenv
from openai import OpenAI

from tools import calculate, get_weather, convert_distance, send_email

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

MODEL = "gpt-4o-mini"

TOOLS = [
    {
        "type": "function",
        "name": "calculate",
        "description": "Perform a basic arithmetic calculation.",
        "parameters": {
            "type": "object",
            "properties": {
                "number1": {"type": "number", "description": "The first number"},
                "number2": {"type": "number", "description": "The second number"},
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The arithmetic operation to perform",
                },
            },
            "required": ["number1", "number2", "operation"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get the current mocked weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "The city whose weather should be retrieved."},
            },
            "required": ["city"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "convert_distance",
        "description": "Convert a distance value from one unit to another.",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {"type": "number", "description": "The distance value to convert."},
                "from_unit": {
                    "type": "string",
                    "enum": ["meters", "kilometers", "miles", "centimeters", "inches", "feet"],
                    "description": "The unit to convert from",
                },
                "to_unit": {
                    "type": "string",
                    "enum": ["meters", "kilometers", "miles", "centimeters", "inches", "feet"],
                    "description": "The unit to convert to",
                },
            },
            "required": ["value", "from_unit", "to_unit"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "send_email",
        "description": "Send an email to a recipient.",
        "parameters": {
            "type": "object",
            "properties": {
                "recipient": {"type": "string", "description": "The recipient's email address."},
                "subject": {"type": "string", "description": "The subject of the email."},
                "body": {"type": "string", "description": "The message body of the email."},
            },
            "required": ["recipient", "subject", "body"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]

TOOL_FUNCTIONS = {
    "calculate": calculate,
    "get_weather": get_weather,
    "convert_distance": convert_distance,
    "send_email": send_email,
}

READ_ONLY_TOOLS = {"calculate", "get_weather", "convert_distance"}
SIDE_EFFECT_TOOLS = {"send_email"}

MAX_ATTEMPTS = 3

# Mocked approval gate. A real system would check a human/policy decision here;
# this stands in for that by rejecting one hardcoded recipient.
UNAPPROVED_RECIPIENTS = {"blocked@example.com"}


def is_approved(tool_name: str, arguments: dict) -> bool:
    if tool_name not in SIDE_EFFECT_TOOLS:
        return True
    return arguments.get("recipient") not in UNAPPROVED_RECIPIENTS


def execute_tool(tool_name: str, arguments: dict) -> dict:
    """Resolve, validate, and run a tool with retries, approval, and idempotency awareness."""
    tool_function = TOOL_FUNCTIONS.get(tool_name)
    if tool_function is None:
        return {"status": "error", "error_type": "permanent", "message": f"Unknown tool: {tool_name}"}

    is_side_effect = tool_name in SIDE_EFFECT_TOOLS

    if is_side_effect:
        if not is_approved(tool_name, arguments):
            return {"status": "error", "error_type": "permanent", "message": f"{tool_name} was not approved"}

        # Idempotency is infrastructure policy, not semantic content — the backend
        # mints the key once per request, never the LLM, and reuses it across
        # every retry attempt of that same request below.
        idempotency_key = str(uuid.uuid4())
        print("Backend-assigned idempotency_key:", idempotency_key)
        arguments = {**arguments, "idempotency_key": idempotency_key}

    # Read-only tools and approved side-effecting tools may retry transient failures.
    # A side-effecting retry reuses the same `arguments` dict, so it goes out with
    # the same idempotency_key every attempt.
    max_attempts = MAX_ATTEMPTS if (tool_name in READ_ONLY_TOOLS or is_side_effect) else 1

    for attempt in range(1, max_attempts + 1):
        try:
            result = tool_function(**arguments)
            return {"status": "success", "data": result}
        except (TimeoutError, ConnectionError) as exc:
            if attempt == max_attempts:
                return {"status": "error", "error_type": "transient", "message": str(exc)}
            continue
        except (ValueError, TypeError) as exc:
            return {"status": "error", "error_type": "permanent", "message": str(exc)}
        except Exception as exc:
            return {"status": "error", "error_type": "internal", "message": str(exc)}


def run_user_message(message: str) -> str:
    response = client.responses.create(model=MODEL, input=message, tools=TOOLS)

    print("Raw model output:", response.output)

    tool_outputs = []

    for item in response.output:
        if item.type == "function_call":
            tool_name = item.name
            arguments = json.loads(item.arguments)

            print("Selected tool:", tool_name)
            print("Generated arguments:", arguments)

            result = execute_tool(tool_name, arguments)
            print("Execution result:", result)

            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result),
                }
            )

    if not tool_outputs:
        final_answer = response.output_text
        print(f"Final answer: {final_answer}\n")
        return final_answer

    final_response = client.responses.create(
        model=MODEL,
        previous_response_id=response.id,
        input=tool_outputs,
    )

    final_answer = final_response.output_text
    print(f"Final answer: {final_answer}\n")
    return final_answer


if __name__ == "__main__":
    prompts = [
        "What is 10 plus 5?",
        "What is 10 divided by 2?",
        "What is 10 divided by 0?",
        "What is 10 mod 5?",
        "What is apple plus 5?",
        "What is the weather in Hyderabad?",
        "What is the weather in Atlantis?",
        "What's the weather like in Timeout City today?",
        "What's the weather like today?",
        "Convert 5 miles to kilometers.",
        "Convert 5 lightyears to meters.",
        "Convert a few miles to kilometers.",
        "Send an email to aman@example.com letting him know the meeting is at 5 PM.",
        "Send an email to aman@example.com letting him know the meeting is at 5 PM.",
        "Send an email to blocked@example.com letting them know the meeting is cancelled.",
        "Send an email to timeout@example.com letting them know the server will be down for maintenance.",
        "Send a text message to +1-555-1234 saying the meeting is at 5.",
    ]

    for prompt in prompts:
        print(f"--- Prompt: {prompt} ---")
        run_user_message(prompt)

    # Since the backend mints a fresh idempotency_key per request, two separate
    # prompts never naturally share one. To prove send_email's duplicate
    # detection actually works, force uuid4() to return the same value twice
    # and call execute_tool directly, simulating a retried request.
    print("--- Test: send_email duplicate detection (forced same idempotency_key) ---")
    fixed_key = "forced-duplicate-key-1"
    with patch("main.uuid.uuid4", return_value=fixed_key):
        first = execute_tool(
            "send_email",
            {"recipient": "aman@example.com", "subject": "First send", "body": "b1"},
        )
        second = execute_tool(
            "send_email",
            {"recipient": "aman@example.com", "subject": "Second send", "body": "b2"},
        )
    print("First call result:", first)
    print("Second call result:", second)
    assert second["data"]["status"] == "duplicate", "Expected the second call to be reported as a duplicate"
    assert second["data"]["subject"] == "First send", "Expected the original (first) subject, not a resend"
    print("OK: repeated idempotency_key did not resend the email.\n")
