"""
1. Defines application settings using Pydantic BaseSettings to parse environment variables.
2. Manages API keys (OpenRouter, Tavily, LinkedIn, Twitter, Telegram) and database connection strings.
3. Validates configuration on application startup to fail fast on missing required credentials.
"""

from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project Root Directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / "backend" / ".env"


class Settings(BaseSettings):
    """
    Type-safe application configuration loaded from environment variables and .env file.
    """
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Core App
    PROJECT_NAME: str = "Social-Manager AI Brand Engine"
    API_V1_STR: str = "/api/v1"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # LLM & OpenRouter Routing
    OPENROUTER_API_KEY: str
    FAST_LLM_MODEL: str = "openrouter/deepseek/deepseek-chat"
    REASONING_LLM_MODEL: str = "openrouter/deepseek/deepseek-r1"
    WRITER_LLM_MODEL: str = "openrouter/google/gemini-2.5-flash"

    # Search & Scraping
    TAVILY_API_KEY: str
    GITHUB_TOKEN: Optional[str] = None

    # Agent Guardrails & Thresholds
    CRITIC_PASS_THRESHOLD: int = 85


# Export a global singleton instance
settings = Settings()
