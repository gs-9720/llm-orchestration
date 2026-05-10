from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LLM Gateway"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    api_v1_prefix: str = "/api/v1"

    default_provider: str = "ollama"
    default_model: str = "llama3.2:latest"

    ollama_base_url: str = "http://localhost:11434/api"
    ollama_default_model: str = "llama3.2:latest"
    ollama_api_key: str | None = None

    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_default_model: str = "gpt-4o-mini"

    anthropic_api_key: str | None = None
    anthropic_base_url: str = "https://api.anthropic.com"
    anthropic_default_model: str = "claude-sonnet-4-20250514"

    gemini_api_key: str | None = None
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai"
    gemini_default_model: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
