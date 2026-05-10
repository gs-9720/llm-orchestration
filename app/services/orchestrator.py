from collections.abc import AsyncGenerator

from fastapi import HTTPException

from app.core.config import get_settings
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.openai_provider import OpenAIProvider
from app.schemas.chat import ChatRequest, ChatResponse


class Orchestrator:
    def __init__(self) -> None:
        self.providers = {
            "ollama": OllamaProvider(),
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
            "gemini": GeminiProvider(),
        }

    def get_provider(self, provider_name: str):
        provider = self.providers.get(provider_name)
        if not provider:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported provider: {provider_name}",
            )
        return provider

    async def generate(self, request: ChatRequest) -> ChatResponse:
        settings = get_settings()
        provider_name = request.provider or settings.default_provider
        provider = self.get_provider(provider_name)
        return await provider.generate(request)

    async def stream_generate(self, request: ChatRequest):
        settings = get_settings()
        provider_name = request.provider or settings.default_provider
        provider = self.get_provider(provider_name)
        return await provider.stream_generate(request)


orchestrator = Orchestrator()
