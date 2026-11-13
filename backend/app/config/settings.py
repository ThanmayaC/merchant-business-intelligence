"""
settings.py — ONE place that reads every secret/config value.

ANALOGY: Think of this as the "control panel" on the wall of a building.
Every machine (database, AI model, search) looks at this panel to know
its settings, instead of each machine hard-coding its own numbers.

CONCEPT — Pydantic Settings:
  Pydantic is a library that VALIDATES data using Python type hints.
  `BaseSettings` is a special Pydantic class that fills its fields from
  environment variables or the `.env` file automatically.
  If DATABASE_URL is missing or the wrong type, the app fails at startup
  with a clear error — instead of crashing later in a random place.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/config/settings.py  ->  parents[3] is the project root folder.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = PROJECT_ROOT / "backend"


class Settings(BaseSettings):
    # Each line = "field name: type = default value".
    # Pydantic reads an env variable with the same name (case-insensitive).
    app_env: str = "development"

    # Same idea as a MongoDB connection string:
    # dialect+driver://user:password@host:port/database
    database_url: str = "postgresql+psycopg://mbi_app:CHANGE_ME@localhost:5432/merchant_bi"

    # Ollama = a local "LLM server" running on your laptop (like a tiny OpenAI).
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3.2:3b"

    # Sentence-Transformers model that turns text into vectors (embeddings).
    embed_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Where the CSV files and policy documents live.
    data_dir: Path = PROJECT_ROOT / "data"

    # Which browser origins may call the API (React dev server).
    cors_origins: str = "http://localhost:5173"

    # Tell Pydantic where the .env file is, and to ignore unknown keys.
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Create ONE shared settings object. Everyone imports this same instance.
settings = Settings()
