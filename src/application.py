import asyncio
import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.exceptions import AppException
from src.exceptions.handler import app_exception_handler, validation_exception_handler
from src.exceptions.validation import ValidationException
from src.routers.healthcheck_router import router as healthcheck_router
from src.routers.catalog_router import router as catalog_router
from src.routers.users_router import router as users_router
from src.routers.orders_router import router as orders_router
from src.schemas.log import RequestLogExtra
from src.workers.category_worker import category_worker

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(category_worker())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


def _include_routers(app: FastAPI) -> None:
    app.include_router(healthcheck_router)
    app.include_router(catalog_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(orders_router, prefix="/api/v1")


def _add_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(ValidationException, validation_exception_handler)


def get_app() -> FastAPI:
    app = FastAPI(
        title="Internet Shop API",
        docs_url="/docs",
        openapi_url="/openapi.json",
        default_response_class=JSONResponse,
        lifespan=lifespan,
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

    _add_handlers(app)
    _include_routers(app)

    return app
