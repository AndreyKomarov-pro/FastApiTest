from fastapi import FastAPI
from src.database import engine
from src.api.category import router as category_router
from src.api.cart import router as cart_router
from src.api.user import router as user_router
from src.api.product import router as product_router
from src.api.order import router as order_router
from src.api.order_item import router as order_item_router
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title="Internet Shop API", lifespan=lifespan)

# роутеры
app.include_router(category_router)
app.include_router(cart_router)
app.include_router(user_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(order_item_router)


@app.get("/")
async def root():
    return {"status": "ok"}