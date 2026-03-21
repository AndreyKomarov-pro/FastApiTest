from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.healthcheck.router import router as healthcheck_router
from src.router.catalog.router import router as catalog_router
from src.router.users.router import router as users_router
from src.router.orders.router import router as orders_router
from src.middleware import RequestIdMiddleware


def get_app() -> FastAPI:
    app = FastAPI(
        title="Internet Shop API",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(healthcheck_router)
    app.include_router(catalog_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(orders_router, prefix="/api/v1")

    return app
