"""
NCプログラム生成APIエンドポイント
"""
import json
import logging
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse

from src.api.schemas.generate import (
    GenerateResponse,
    ProcessInfo,
    MachiningConditions,
    DrawingAnalysis
)
from src.services.nc_generator import NCGenerator
from src.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate_nc_program(
    drawing: UploadFile = File(..., description="図面画像ファイル"),
    process_info: str = Form(..., description="行程情報 (JSON)"),
    machining_conditions: str = Form(..., description="加工条件 (JSON)")
):
    """
    NCプログラムを生成する

    1. 図面画像をアップロード
    2. Gemini APIで図面を解析
    3. 知識ベースから類似サンプルを検索
    4. NCプログラムを生成して返却
    """
    try:
        # JSONパース
        process_data = json.loads(process_info)
        conditions_data = json.loads(machining_conditions)

        # バリデーション
        process = ProcessInfo(**process_data)
        conditions = MachiningConditions(**conditions_data)

        # ファイル検証
        if not drawing.content_type or not drawing.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="画像ファイルをアップロードしてください")

        # ファイルサイズ検証
        contents = await drawing.read()
        if len(contents) > settings.max_upload_size:
            raise HTTPException(
                status_code=400,
                detail=f"ファイルサイズが大きすぎます (最大: {settings.max_upload_size // 1024 // 1024}MB)"
            )

        logger.info(f"NCプログラム生成リクエスト: {process.process_name}, 材質: {conditions.material}")

        # NCプログラム生成
        generator = NCGenerator()
        program = await generator.generate(
            drawing_bytes=contents,
            process_info=process.model_dump(),
            machining_conditions=conditions.model_dump(),
            mime_type=drawing.content_type or "image/png"
        )

        # レスポンス作成
        analysis = DrawingAnalysis(
            process_type=program.analysis.get("process_type", ""),
            features=program.analysis.get("features", []),
            dimensions=program.analysis.get("dimensions", {}),
            tolerances=program.analysis.get("tolerances"),
            surface_finish=program.analysis.get("surface_finish")
        ) if program.analysis else None

        return GenerateResponse(
            success=True,
            nc_program=program.code,
            analysis=analysis,
            referenced_samples=program.referenced_samples,
            warnings=program.warnings,
            generated_at=program.generated_at
        )

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSONパースエラー: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"NCプログラム生成エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-drawing", response_class=HTMLResponse)
async def analyze_drawing(
    drawing: UploadFile = File(..., description="図面画像ファイル")
):
    """
    図面を解析してHTMXパーシャルを返す
    """
    try:
        # ファイル検証
        if not drawing.content_type or not drawing.content_type.startswith("image/"):
            return """<div class="text-red-500 p-4">画像ファイルをアップロードしてください</div>"""

        contents = await drawing.read()
        if len(contents) > settings.max_upload_size:
            return """<div class="text-red-500 p-4">ファイルサイズが大きすぎます</div>"""

        logger.info(f"図面解析リクエスト: {drawing.filename}, サイズ: {len(contents)} bytes")

        # Gemini APIで解析
        generator = NCGenerator()
        analysis = await generator.analyze_only(
            drawing_bytes=contents,
            mime_type=drawing.content_type or "image/png"
        )

        # 特徴リストをHTMLに変換
        features_html = "".join([
            f'<span class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm mr-1">{f}</span>'
            for f in analysis.get("features", [])
        ]) or '<span class="text-gray-500">検出なし</span>'

        # 寸法情報をHTMLに変換
        dims = analysis.get("dimensions", {})
        dims_html = ""
        if dims:
            dims_items = []
            if dims.get("diameter_start"):
                dims_items.append(f"開始径: φ{dims['diameter_start']}mm")
            if dims.get("diameter_end"):
                dims_items.append(f"終了径: φ{dims['diameter_end']}mm")
            if dims.get("length"):
                dims_items.append(f"長さ: {dims['length']}mm")
            dims_html = " / ".join(dims_items) if dims_items else "寸法未検出"
        else:
            dims_html = "寸法未検出"

        return f"""
        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 class="font-bold text-green-800 mb-3">図面解析結果</h4>
            <div class="space-y-2 text-sm">
                <div>
                    <span class="font-medium text-gray-700">加工タイプ:</span>
                    <span class="ml-2 px-2 py-1 bg-green-100 text-green-800 rounded">
                        {analysis.get('process_type', '不明')}
                    </span>
                </div>
                <div>
                    <span class="font-medium text-gray-700">検出された特徴:</span>
                    <div class="mt-1">{features_html}</div>
                </div>
                <div>
                    <span class="font-medium text-gray-700">寸法情報:</span>
                    <span class="ml-2 text-gray-600">{dims_html}</span>
                </div>
            </div>
        </div>
        """

    except Exception as e:
        logger.error(f"図面解析エラー: {str(e)}", exc_info=True)
        return f"""<div class="text-red-500 p-4 bg-red-50 rounded">エラー: {str(e)}</div>"""
