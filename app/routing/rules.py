from app.core.config import get_settings
from app.schemas.chat import ChatRequest


MODEL_PROVIDER_REGISTRY = {
    "llama3.2:latest": "ollama",
    "mistral": "ollama",
    "gpt-4o-mini": "openai",
    "gpt-4.1-mini": "openai",
    "claude-sonnet-4-20250514": "anthropic",
    "claude-opus-4-20250514": "anthropic",
}


class RoutingEngine:
    def choose_provider(self, request: ChatRequest) -> str:
        settings = get_settings()

        if request.provider:
            return request.provider

        if request.model and request.model in MODEL_PROVIDER_REGISTRY:
            return MODEL_PROVIDER_REGISTRY[request.model]

        return settings.default_provider

    def choose_model(self, request: ChatRequest, provider_name: str) -> str:
        settings = get_settings()

        if request.model:
            return request.model

        if provider_name == "openai":
            return settings.openai_default_model

        if provider_name == "anthropic":
            return settings.anthropic_default_model

        return settings.default_model
