from fastapi import APIRouter

from app.api.v1 import cartoes

router = APIRouter(prefix="/v1")

router.include_router(cartoes.router)
