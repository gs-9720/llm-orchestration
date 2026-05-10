import json
from collections.abc import AsyncGenerator

import httpx
from fastapi import HTTPException

from app.core.config import get_settings
from app.providers.base import BaseProvider
from app.schemas.chat import ChatRequest, ChatResponse


class OpenAIProvider(BaseProvider):
    provider_name = "openai"

    async def generate(self, request: ChatRequest) -> ChatResponse:
        settings = get_settings()

        if not settings.openai_api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured")

        model = request.model or settings.default_model

        payload = {
            "model": model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in request.messages
            ],
            "stream": False,
        }

        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{settings.openai_base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            raise HTTPException(status_code=504, detail="OpenAI request timed out") from exc
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"OpenAI HTTP error: {exc.response.text}",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Could not connect to OpenAI: {str(exc)}",
            ) from exc

        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            or ""
        ).strip()

        if not content:
            raise HTTPException(
                status_code=502,
                detail=f"OpenAI returned unexpected response: {data}",
            )

        return ChatResponse(
            model=data.get("model", model),
            provider=self.provider_name,
            content=content,
        )

    async def stream_generate(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        settings = get_settings()

        if not settings.openai_api_key:
            async def error_generator():
                yield f" {json.dumps({'type': 'error', 'content': 'OPENAI_API_KEY is not configured'})}\n\n"
            return error_generator()

        model = request.model or settings.default_model

        payload = {
            "model": model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in request.messages
            ],
            "stream": True,
        }

        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }

        async def generator() -> AsyncGenerator[str, None]:
            try:
                async with httpx.AsyncClient(timeout=None) as client:
                    async with client.stream(
                        "POST",
                        f"{settings.openai_base_url}/chat/completions",
                        json=payload,
                        headers=headers,
                    ) as response:
                        response.raise_for_status()

                        async for line in response.aiter_lines():
                            if not line:
                                continue
                            if not line.startswith(" "):
                                continue

                            data_str = line[6:].strip()

                            if data_str == "[DONE]":
                                yield f" {json.dumps({'type': 'done', 'model': model, 'provider': self.provider_name})}\n\n"
                                break

                            try:
                                chunk = json.loads(data_str)
                            except json.JSONDecodeError:
                                continue

                            choices = chunk.get("choices", [])
                            if not choices:
                                continue

                            delta = choices[0].get("delta", {})
                            content = delta.get("content") or ""

                            if content:
                                yield f" {json.dumps({'type': 'token', 'content': content})}\n\n"

            except httpx.TimeoutException:
                yield f" {json.dumps({'type': 'error', 'content': 'OpenAI request timed out'})}\n\n"
            except httpx.HTTPStatusError as exc:
                yield f" {json.dumps({'type': 'error', 'content': f'OpenAI HTTP error: {exc.response.text}'})}\n\n"
            except httpx.RequestError as exc:
                yield f" {json.dumps({'type': 'error', 'content': f'Could not connect to OpenAI: {str(exc)}'})}\n\n"

        return generator()
