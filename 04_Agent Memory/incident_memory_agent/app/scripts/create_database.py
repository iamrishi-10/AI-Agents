from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.config.settings import DB_URL_SYNC

DB_NAME = "incident_memory_agent"


def create_database() -> None:
    try:
        admin_engine = create_engine(DB_URL_SYNC, isolation_level="AUTOCOMMIT")
    except Exception as exc:
        raise RuntimeError(f"Failed to create database engine: {exc}") from exc

    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": DB_NAME},
        ).scalar()

        if exists:
            print(f"Database '{DB_NAME}' already exists.")
        else:
            conn.execute(text(f'CREATE DATABASE "{DB_NAME}"'))
            print(f"Database '{DB_NAME}' created.")

    target_url = make_url(DB_URL_SYNC).set(database=DB_NAME)
    target_engine = create_engine(target_url, isolation_level="AUTOCOMMIT")

    with target_engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        print("Extension 'vector' is enabled.")

    target_engine.dispose()


if __name__ == "__main__":
    create_database()
