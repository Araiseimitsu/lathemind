"""
APIルーター統合
"""
from fastapi import APIRouter

from src.api.endpoints import generate, knowledge, health

api_router = APIRouter()

# 各エンドポイントを登録
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(generate.router, tags=["Generate"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge"])
