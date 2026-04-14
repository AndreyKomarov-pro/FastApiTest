from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.routers.healthcheck_router import router as healthcheck_router
from src.routers.categories_router import router as categories_router
from src.routers.products_router import router as products_router
from src.routers.users_router import router as users_router
from src.routers.orders_router import router as orders_router
from src.routers.order_items_router import router as order_items_router
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
    app.include_router(categories_router, prefix="/api/v1")
    app.include_router(products_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(orders_router, prefix="/api/v1")
    app.include_router(order_items_router, prefix="/api/v1")

    return app
