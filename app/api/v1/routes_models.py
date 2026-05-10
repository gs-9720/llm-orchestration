from fastapi import APIRouter
import httpx

from app.core.config import get_settings
from app.schemas.model import ModelInfo, ModelListResponse

router = APIRouter()


@router.get("/", response_model=ModelListResponse)
async def list_models() -> ModelListResponse:
    settings = get_settings()
    models: list[ModelInfo] = []

    async with httpx.AsyncClient(timeout=15.0) as client:
        models.extend(await _fetch_ollama_models(client, settings))
        models.extend(await _fetch_openai_models(client, settings))
        models.extend(await _fetch_anthropic_models(client, settings))

    models.extend(_get_gemini_models(settings))
    models.sort(key=lambda model: (model.provider, model.name.lower()))

    return ModelListResponse(
        models=models,
        default_model=settings.default_model,
        default_provider=settings.default_provider,
    )


async def _fetch_ollama_models(client: httpx.AsyncClient, settings) -> list[ModelInfo]:
    headers = {}
    if settings.ollama_api_key:
        headers["Authorization"] = f"Bearer {settings.ollama_api_key}"

    try:
        response = await client.get(
            f"{settings.ollama_base_url}/tags",
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()

        return [
            ModelInfo(
                id=(model.get("digest") or model["name"])[:12],
                name=model["name"],
                provider="ollama",
                owned_by="ollama-cloud" if settings.ollama_api_key else "local",
                supports_stream=True,
                status="enabled",
                size=model.get("size"),
                modified=model.get("modified_at"),
            )
            for model in data.get("models", [])
            if model.get("name")
        ]
    except Exception:
        return []


async def _fetch_openai_models(client: httpx.AsyncClient, settings) -> list[ModelInfo]:
    if not settings.openai_api_key:
        return []

    try:
        response = await client.get(
            f"{settings.openai_base_url}/models",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
        )
        response.raise_for_status()
        data = response.json()

        return [
            ModelInfo(
                id=model["id"],
                name=model["id"],
                provider="openai",
                owned_by=model.get("owned_by", "openai"),
                supports_stream=True,
                status="enabled",
                size=None,
                modified=None,
            )
            for model in data.get("data", [])
            if model.get("id")
        ]
    except Exception:
        return []


async def _fetch_anthropic_models(client: httpx.AsyncClient, settings) -> list[ModelInfo]:
    if not settings.anthropic_api_key:
        return []

    try:
        response = await client.get(
            f"{settings.anthropic_base_url}/v1/models",
            headers={
                "x-api-key": settings.anthropic_api_key,
                "anthropic-version": "2023-06-01",
            },
        )
        response.raise_for_status()
        data = response.json()

        items = data.get("data", [])
        if not isinstance(items, list):
            return []

        return [
            ModelInfo(
                id=model["id"],
                name=model.get("display_name") or model["id"],
                provider="anthropic",
                owned_by="anthropic",
                supports_stream=True,
                status="enabled",
                size=None,
                modified=model.get("created_at"),
            )
            for model in items
            if model.get("id")
        ]
    except Exception:
        return []


def _get_gemini_models(settings) -> list[ModelInfo]:
    if not settings.gemini_api_key:
        return []

    return [
        ModelInfo(
            id="gemini-2.5-flash",
            name="gemini-2.5-flash",
            provider="gemini",
            owned_by="google",
            supports_stream=True,
            status="enabled",
            size=None,
            modified=None,
        ),
        ModelInfo(
            id="gemini-2.5-pro",
            name="gemini-2.5-pro",
            provider="gemini",
            owned_by="google",
            supports_stream=True,
            status="enabled",
            size=None,
            modified=None,
        ),
    ]
