from typing import Literal

from pydantic import BaseModel, Field

ProviderName = Literal["ollama", "openai", "anthropic", "gemini"]
MessageRole = Literal["system", "user", "assistant"]


class Message(BaseModel):
    role: MessageRole
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    provider: ProviderName | None = None
    model: str | None = None
    messages: list[Message] = Field(min_length=1)
    stream: bool = False
    temperature: float | None = Field(default=0.7, ge=0, le=2)
    max_tokens: int | None = Field(default=1024, gt=0)


class ChatResponse(BaseModel):
    model: str
    provider: ProviderName
    content: str
