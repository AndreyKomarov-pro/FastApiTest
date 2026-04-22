import logging
import time
import uuid
from typing import TypedDict

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.routers.healthcheck_router import router as healthcheck_router
from src.routers.catalog_router import router as catalog_router
from src.routers.users_router import router as users_router
from src.routers.orders_router import router as orders_router

logger = logging.getLogger("app")


class RequestLogExtra(TypedDict):
    request_id: str
    method: str
    path: str
    status_code: int
    duration_ms: float


def _register_routers(app: FastAPI) -> None:
    app.include_router(healthcheck_router)
    app.include_router(catalog_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(orders_router, prefix="/api/v1")


def get_app() -> FastAPI:
    app = FastAPI(
        title="Internet Shop API",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        response.headers["X-Request-Id"] = request_id

        extra: RequestLogExtra = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
        }
        logger.info("request completed", extra=extra)

        return response

    _register_routers(app)

    return app
