import json
from collections.abc import AsyncGenerator

import httpx
from fastapi import HTTPException

from app.core.config import get_settings
from app.providers.base import BaseProvider
from app.schemas.chat import ChatRequest, ChatResponse


class AnthropicProvider(BaseProvider):
    provider_name = "anthropic"

    async def generate(self, request: ChatRequest) -> ChatResponse:
        settings = get_settings()

        if not settings.anthropic_api_key:
            raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY is not configured")

        model = request.model or settings.default_model

        system_messages = [m.content for m in request.messages if m.role == "system"]
        non_system_messages = [
            {"role": m.role, "content": m.content}
            for m in request.messages
            if m.role != "system"
        ]

        payload = {
            "model": model,
            "messages": non_system_messages,
            "max_tokens": request.max_tokens or 1024,
            "stream": False,
        }

        if system_messages:
            payload["system"] = "\n".join(system_messages)
        if request.temperature is not None:
            payload["temperature"] = request.temperature

        headers = {
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{settings.anthropic_base_url}/v1/messages",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            raise HTTPException(status_code=504, detail="Anthropic request timed out") from exc
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Anthropic HTTP error: {exc.response.text}",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Could not connect to Anthropic: {str(exc)}",
            ) from exc

        text_parts = [
            block.get("text", "")
            for block in data.get("content", [])
            if block.get("type") == "text"
        ]
        content = "".join(text_parts).strip()

        if not content:
            raise HTTPException(
                status_code=502,
                detail=f"Anthropic returned unexpected response: {data}",
            )

        return ChatResponse(
            model=data.get("model", model),
            provider=self.provider_name,
            content=content,
        )

    async def stream_generate(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        settings = get_settings()

        if not settings.anthropic_api_key:
            async def error_generator():
                yield f" {json.dumps({'type': 'error', 'content': 'ANTHROPIC_API_KEY is not configured'})}\n\n"
            return error_generator()

        model = request.model or settings.default_model

        system_messages = [m.content for m in request.messages if m.role == "system"]
        non_system_messages = [
            {"role": m.role, "content": m.content}
            for m in request.messages
            if m.role != "system"
        ]

        payload = {
            "model": model,
            "messages": non_system_messages,
            "max_tokens": request.max_tokens or 1024,
            "stream": True,
        }

        if system_messages:
            payload["system"] = "\n".join(system_messages)
        if request.temperature is not None:
            payload["temperature"] = request.temperature

        headers = {
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        async def generator() -> AsyncGenerator[str, None]:
            try:
                async with httpx.AsyncClient(timeout=None) as client:
                    async with client.stream(
                        "POST",
                        f"{settings.anthropic_base_url}/v1/messages",
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

                            try:
                                event = json.loads(data_str)
                            except json.JSONDecodeError:
                                continue

                            event_type = event.get("type")

                            if event_type == "content_block_delta":
                                delta = event.get("delta", {})
                                if delta.get("type") == "text_delta":
                                    text = delta.get("text", "")
                                    if text:
                                        yield f" {json.dumps({'type': 'token', 'content': text})}\n\n"

                            elif event_type == "message_stop":
                                yield f" {json.dumps({'type': 'done', 'model': model, 'provider': self.provider_name})}\n\n"
                                break

            except httpx.TimeoutException:
                yield f" {json.dumps({'type': 'error', 'content': 'Anthropic request timed out'})}\n\n"
            except httpx.HTTPStatusError as exc:
                yield f" {json.dumps({'type': 'error', 'content': f'Anthropic HTTP error: {exc.response.text}'})}\n\n"
            except httpx.RequestError as exc:
                yield f" {json.dumps({'type': 'error', 'content': f'Could not connect to Anthropic: {str(exc)}'})}\n\n"

        return generator()
