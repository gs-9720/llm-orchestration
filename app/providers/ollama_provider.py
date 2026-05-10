import json
from collections.abc import AsyncGenerator

import httpx
from fastapi import HTTPException

from app.core.config import get_settings
from app.providers.base import BaseProvider
from app.schemas.chat import ChatRequest, ChatResponse


class OllamaProvider(BaseProvider):
    provider_name = "ollama"

    def _get_headers(self, settings) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if settings.ollama_api_key:
            headers["Authorization"] = f"Bearer {settings.ollama_api_key}"
        return headers

    async def generate(self, request: ChatRequest) -> ChatResponse:
        settings = get_settings()
        model = request.model or settings.ollama_default_model

        payload = {
            "model": model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in request.messages
            ],
            "stream": False,
        }

        options = {}
        if request.temperature is not None:
            options["temperature"] = request.temperature
        if request.max_tokens is not None:
            options["num_predict"] = request.max_tokens
        if options:
            payload["options"] = options

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{settings.ollama_base_url}/chat",
                    json=payload,
                    headers=self._get_headers(settings),
                )
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            raise HTTPException(status_code=504, detail="Ollama request timed out") from exc
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Ollama HTTP error: {exc.response.text}",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Could not connect to Ollama: {str(exc)}",
            ) from exc

        content = (data.get("message", {}).get("content") or "").strip()
        if not content:
            raise HTTPException(
                status_code=502,
                detail=f"Ollama returned unexpected response: {data}",
            )

        return ChatResponse(
            model=data.get("model", model),
            provider=self.provider_name,
            content=content,
        )

    async def stream_generate(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        settings = get_settings()
        model = request.model or settings.ollama_default_model

        payload = {
            "model": model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in request.messages
            ],
            "stream": True,
        }

        options = {}
        if request.temperature is not None:
            options["temperature"] = request.temperature
        if request.max_tokens is not None:
            options["num_predict"] = request.max_tokens
        if options:
            payload["options"] = options

        async def generator() -> AsyncGenerator[str, None]:
            try:
                async with httpx.AsyncClient(timeout=None) as client:
                    async with client.stream(
                        "POST",
                        f"{settings.ollama_base_url}/chat",
                        json=payload,
                        headers=self._get_headers(settings),
                    ) as response:
                        response.raise_for_status()

                        async for line in response.aiter_lines():
                            if not line:
                                continue

                            try:
                                chunk = json.loads(line)
                            except json.JSONDecodeError:
                                continue

                            content = chunk.get("message", {}).get("content") or ""
                            if content:
                                yield f" {json.dumps({'type': 'token', 'content': content})}\n\n"

                            if chunk.get("done") is True:
                                yield f" {json.dumps({'type': 'done', 'model': chunk.get('model', model), 'provider': self.provider_name})}\n\n"
                                break

            except httpx.TimeoutException:
                yield f" {json.dumps({'type': 'error', 'content': 'Ollama request timed out'})}\n\n"
            except httpx.HTTPStatusError as exc:
                yield f" {json.dumps({'type': 'error', 'content': f'Ollama HTTP error: {exc.response.text}'})}\n\n"
            except httpx.RequestError as exc:
                yield f" {json.dumps({'type': 'error', 'content': f'Could not connect to Ollama: {str(exc)}'})}\n\n"

        return generator()
