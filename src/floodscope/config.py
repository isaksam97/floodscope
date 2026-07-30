"""Configuration, read from environment variables (see .env.example)."""
import os

DB_HOST = os.getenv("FLOODSCOPE_DB_HOST", "localhost")
DB_PORT = os.getenv("FLOODSCOPE_DB_PORT", "5432")
DB_NAME = os.getenv("FLOODSCOPE_DB_NAME", "floodscope")
DB_USER = os.getenv("FLOODSCOPE_DB_USER", "floodscope")
DB_PASSWORD = os.getenv("FLOODSCOPE_DB_PASSWORD", "floodscope")

TARGET_CRS = 27700  # British National Grid — metric, so distances are real metres


def database_url() -> str:
    return (
        f"postgresql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
