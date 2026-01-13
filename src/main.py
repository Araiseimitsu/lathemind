"""
LatheMind - FastAPIアプリケーションエントリポイント
CINCOM L20 NC旋盤自動プログラミングツール
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from src.config import settings
from src.api.router import api_router

# ログ設定
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    # 起動時の初期化
    logger.info(f"{settings.app_name} を起動しています...")
    logger.info(f"対応機種: CINCOM {settings.cincom_model}")
    logger.info(f"知識ベースパス: {settings.knowledge_base_abs_path}")

    # 必要なディレクトリの確認
    knowledge_path = settings.knowledge_base_abs_path
    if not knowledge_path.exists():
        logger.warning(f"知識ベースディレクトリが存在しません: {knowledge_path}")

    yield

    # 終了時のクリーンアップ
    logger.info(f"{settings.app_name} を終了しています...")


# FastAPIアプリケーション作成
app = FastAPI(
    title=settings.app_name,
    description="CINCOM L20 NC旋盤の自動プログラミングツール",
    version="1.0.0",
    lifespan=lifespan
)

# 静的ファイルのマウント
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# テンプレート設定
templates_path = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

# APIルーターの登録
app.include_router(api_router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """メインページを表示"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "cincom_model": settings.cincom_model
        }
    )


@app.get("/knowledge", response_class=HTMLResponse)
async def knowledge_page(request: Request):
    """知識ベース管理ページを表示"""
    return templates.TemplateResponse(
        "knowledge.html",
        {
            "request": request,
            "app_name": settings.app_name
        }
    )


@app.get("/process", response_class=HTMLResponse)
async def process_page(request: Request):
    """工程管理ページを表示"""
    return templates.TemplateResponse(
        "process.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "cincom_model": settings.cincom_model
        }
    )
