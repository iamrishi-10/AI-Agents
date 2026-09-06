"""Minimal multi-tool assistant using the OpenAI Responses API."""

import json

from dotenv import load_dotenv
from openai import OpenAI

from tools import calculate, get_weather, convert_distance

load_dotenv()

client = OpenAI()

MODEL = "gpt-4o-mini"

# 2. Tool schemas shown to the model
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
                "city": {
                    "type": "string",
                    "description": "The city whose weather should be retrieved.",
                }
            },
            "required": ["city"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "convert_distance",
        "description": "Convert the distance from one unit to another.",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {"type": "number", "description": "The distance that needs to be converted."},
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
    }
]

# Maps tool name -> actual Python function to execute
TOOL_FUNCTIONS = {
    "calculate": calculate,
    "get_weather": get_weather,
    "convert_distance": convert_distance,
}


def run(user_message: str) -> str:
    # 3. First model call
    response = client.responses.create(
        model=MODEL,
        input=user_message,
        tools=TOOLS,
    )

    # 4. Inspect model output
    print("Raw model output:")
    print(response.output)

    # 5. Execute requested tool(s)
    tool_outputs = []

    for item in response.output:
        if item.type == "function_call":
            tool_name = item.name
            arguments = json.loads(item.arguments)

            print("Selected tool:", tool_name)
            print("Generated arguments:", arguments)

            tool_function = TOOL_FUNCTIONS[tool_name]
            result = tool_function(**arguments)

            print("Raw tool result:", result)

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

    # 6. Send tool result(s) back to the model
    final_response = client.responses.create(
        model=MODEL,
        previous_response_id=response.id,
        input=tool_outputs,
    )

    # 7. Final natural-language answer
    final_answer = final_response.output_text
    print(f"Final answer: {final_answer}\n")
    return final_answer


if __name__ == "__main__":
    prompts = [
        "What is 125 * 48?",
        "What is the weather in Hyderabad?",
        "Explain what REST API means.",
        "Convert 5 miles to kilometers.",
        "Convert 10 meters to feet.",
        "Convert 2 feet to inches.",
        "Convert 100 centimeters to meters.",
        "Convert 3 kilometers to miles.",
        "Convert 12 inches to centimeters.",
    ]
    for prompt in prompts:
        print(f"--- Prompt: {prompt} ---")
        run(prompt)
