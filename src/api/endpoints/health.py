"""
ヘルスチェックエンドポイント
"""
from fastapi import APIRouter

from src.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """アプリケーションのヘルスチェック"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": "1.0.0",
        "cincom_model": settings.cincom_model
    }
