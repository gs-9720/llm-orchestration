from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest
from app.services.orchestrator import orchestrator

router = APIRouter()


@router.post("/completions")
async def chat_completions(request: ChatRequest):
    if request.stream:
        stream = await orchestrator.stream_generate(request)
        return StreamingResponse(
            stream,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    return await orchestrator.generate(request)
