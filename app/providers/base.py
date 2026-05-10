from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from app.schemas.chat import ChatRequest, ChatResponse


class BaseProvider(ABC):
    provider_name: str

    @abstractmethod
    async def generate(self, request: ChatRequest) -> ChatResponse:
        raise NotImplementedError

    @abstractmethod
    async def stream_generate(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        raise NotImplementedError
