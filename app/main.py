from fastapi import FastAPI
from app.api.v1 import routes_models
from app.api.v1.router import api_router
from app.core.config import get_settings

import time
import logging
from fastapi import Request

settings = get_settings()

app = FastAPI(title=settings.app_name)
app.include_router(api_router, prefix=settings.api_v1_prefix)
app.include_router(routes_models.router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}



@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    logging.info(
        f"{request.client.host} - '{request.method} {request.url.path}' "
        f"{response.status_code} in {process_time:.0f}ms"
    )
    
    return response
