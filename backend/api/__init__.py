from fastapi import APIRouter
from backend.api.upload import router as upload_router
from backend.api.query import router as query_router
from backend.api.agent import router as agent_router
from backend.api.logging import router as logging_router

router = APIRouter()
router.include_router(upload_router)
router.include_router(query_router)
router.include_router(agent_router)
router.include_router(logging_router)
