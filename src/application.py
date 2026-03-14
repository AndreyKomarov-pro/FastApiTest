from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.healthcheck.router import router as healthcheck_router
from src.router.category.router import router as category_router
from src.router.user.router import router as user_router
from src.router.product.router import router as product_router
from src.router.cart.router import router as cart_router
from src.router.order.router import router as order_router
from src.router.order_item.router import router as order_item_router


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

    app.include_router(healthcheck_router)
    app.include_router(category_router, prefix="/api/v1")
    app.include_router(user_router, prefix="/api/v1")
    app.include_router(product_router, prefix="/api/v1")
    app.include_router(cart_router, prefix="/api/v1")
    app.include_router(order_router, prefix="/api/v1")
    app.include_router(order_item_router, prefix="/api/v1")

    return app
