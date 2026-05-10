from typing import Literal

from pydantic import BaseModel


ProviderName = Literal["ollama", "openai", "anthropic", "gemini"]


class ModelInfo(BaseModel):
    id: str
    name: str
    provider: ProviderName
    owned_by: str | None = None
    supports_stream: bool = True
    status: str = "enabled"
    size: int | None = None
    modified: str | None = None


class ModelListResponse(BaseModel):
    models: list[ModelInfo]
    default_model: str
    default_provider: ProviderName
