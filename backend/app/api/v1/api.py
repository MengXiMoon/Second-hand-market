from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, products, wallet, orders, websockets

api_router = APIRouter()
api_router.include_router(auth.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(wallet.router, prefix="/wallet", tags=["wallet"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(websockets.router, tags=["websockets"])
