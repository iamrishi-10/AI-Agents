"""Configuration values for the GitHub repository MCP server."""

import os

from dotenv import load_dotenv

load_dotenv()


openai_api_key = os.getenv("OPENAI_API_KEY")
GITHUB_API_BASE_URL = os.getenv("GITHUB_API_BASE_URL")

if not GITHUB_API_BASE_URL:
    raise RuntimeError(
        "GITHUB_API_BASE_URL is not set. Add it to your .env file, "
        "e.g. GITHUB_API_BASE_URL=https://api.github.com"
    )
if not openai_api_key:
    raise RuntimeError(
        "OpenAI_API_KEY is not set. Add it to your .env file, "
    )


MODEL = "gpt-5"
MAX_ROUNDS = 3
MAX_RETRIES = 3


