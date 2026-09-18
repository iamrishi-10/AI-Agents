import os
from dotenv import load_dotenv

load_dotenv()



DB_URL = os.getenv("DATABASE_URL2")
DB_URL_SYNC = os.getenv("DATABASE_URL2_SYNC")


OPENAI_KEY = os.getenv("OPENAI_API_KEY")
NVIDIA_KEY = os.getenv("NVIDIA_API_KEY")


LLM_MODEL="gpt-5.4-mini"

EMBEDDING_MODEL="nvidia/nemotron-3-embed-1b"
EMBEDDING_DIMS= 2048


if __name__ == "__main__":
    print("DB_URL:", DB_URL_SYNC)
    print("DB_URL:", DB_URL)
    print(f"Nvidia Embedding Model= {EMBEDDING_MODEL}")
    print(f"Embedding Dimensions={EMBEDDING_DIMS, type(EMBEDDING_DIMS)}")

    if not OPENAI_KEY:
        print("Open AI Key is not set please setup key")
    else:
        print(f"Open AI key is set and active starting with {OPENAI_KEY[:8]}")

    if not NVIDIA_KEY:
        print("NVIDIA_KEY is not set please setup key")
    else:
        print(f"NVIDIA_KEY is set and active starting with {NVIDIA_KEY[:8]}")