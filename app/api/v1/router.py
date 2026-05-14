from fastapi import APIRouter

from app.api.v1 import cartoes, contratos, licitacoes, viagens

router = APIRouter(prefix="/v1")

router.include_router(cartoes.router)
router.include_router(viagens.router)
router.include_router(contratos.router)
router.include_router(licitacoes.router)
