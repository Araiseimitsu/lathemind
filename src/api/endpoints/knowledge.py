"""
知識ベース管理APIエンドポイント
"""
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from typing import Optional

from src.api.schemas.knowledge import (
    SampleMetadata,
    SampleSummary,
    SampleDetail,
    KnowledgeIndexResponse
)
from src.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=KnowledgeIndexResponse)
async def get_knowledge_index():
    """
    知識ベースのインデックスを取得
    """
    # TODO: Phase 2 で KnowledgeService を使用
    from src.services.knowledge_service import KnowledgeService

    try:
        service = KnowledgeService(str(settings.knowledge_base_abs_path))
        index = service.get_index()

        samples = [
            SampleSummary(
                id=s.get("id", ""),
                name=s.get("name", ""),
                process_type=s.get("process_type", ""),
                material=s.get("material", ""),
                tags=s.get("tags", [])
            )
            for s in index.get("samples", [])
        ]

        return KnowledgeIndexResponse(
            total_samples=index.get("total_samples", 0),
            samples=samples,
            process_types=index.get("process_types", []),
            materials=index.get("materials", [])
        )

    except Exception as e:
        logger.error(f"知識ベースインデックス取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{sample_id}", response_model=SampleDetail)
async def get_sample_detail(sample_id: str):
    """
    サンプルの詳細を取得
    """
    from src.services.knowledge_service import KnowledgeService

    try:
        service = KnowledgeService(str(settings.knowledge_base_abs_path))
        detail = service.get_sample_detail(sample_id)

        if detail is None:
            raise HTTPException(status_code=404, detail=f"サンプルが見つかりません: {sample_id}")

        return SampleDetail(
            metadata=SampleMetadata(**detail["metadata"]),
            nc_code=detail["nc_code"],
            has_drawing=detail.get("has_drawing", False)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"サンプル詳細取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{sample_id}/drawing")
async def get_sample_drawing(sample_id: str):
    """
    サンプルの図面画像を取得
    """
    from src.services.knowledge_service import KnowledgeService
    from pathlib import Path

    try:
        service = KnowledgeService(str(settings.knowledge_base_abs_path))
        drawing_path = service.get_drawing_path(sample_id)

        if drawing_path is None or not Path(drawing_path).exists():
            raise HTTPException(status_code=404, detail="図面が見つかりません")

        return FileResponse(drawing_path, media_type="image/png")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"図面取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_sample(
    metadata: str = Form(..., description="メタデータ (JSON)"),
    nc_code: str = Form(..., description="NCプログラムコード"),
    drawing: Optional[UploadFile] = File(default=None, description="図面画像")
):
    """
    新しいサンプルを登録
    """
    import json
    from src.services.knowledge_service import KnowledgeService

    try:
        # JSONパース
        meta_dict = json.loads(metadata)
        meta = SampleMetadata(**meta_dict)

        # 図面データ取得
        drawing_bytes = None
        if drawing and drawing.content_type.startswith("image/"):
            drawing_bytes = await drawing.read()

        # サービスで登録
        service = KnowledgeService(str(settings.knowledge_base_abs_path))
        success = service.register_sample(
            sample_id=meta.id,
            metadata=meta.model_dump(),
            nc_code=nc_code,
            drawing_bytes=drawing_bytes
        )

        if success:
            logger.info(f"サンプル登録成功: {meta.id}")
            return {"success": True, "sample_id": meta.id}
        else:
            raise HTTPException(status_code=500, detail="サンプル登録に失敗しました")

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSONパースエラー: {str(e)}")
    except Exception as e:
        logger.error(f"サンプル登録エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{sample_id}")
async def delete_sample(sample_id: str):
    """
    サンプルを削除

    注意: この操作は取り消せません
    """
    from src.services.knowledge_service import KnowledgeService

    try:
        service = KnowledgeService(str(settings.knowledge_base_abs_path))
        success = service.delete_sample(sample_id)

        if success:
            logger.info(f"サンプル削除成功: {sample_id}")
            return {"success": True, "message": f"サンプル {sample_id} を削除しました"}
        else:
            raise HTTPException(status_code=404, detail=f"サンプルが見つかりません: {sample_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"サンプル削除エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/html", response_class=HTMLResponse)
async def get_knowledge_list_html():
    """
    知識ベースリストをHTMLで取得（HTMX用）
    """
    from src.services.knowledge_service import KnowledgeService

    try:
        service = KnowledgeService(str(settings.knowledge_base_abs_path))
        index = service.get_index()
        samples = index.get("samples", [])

        if not samples:
            return """
            <div class="text-center py-8 text-gray-500">
                <p>サンプルが登録されていません</p>
                <p class="text-sm mt-2">サンプルを追加してください</p>
            </div>
            """

        html_items = []
        for s in samples:
            tags_html = " ".join([
                f'<span class="px-2 py-1 text-xs bg-gray-100 rounded">{tag}</span>'
                for tag in s.get("tags", [])[:3]
            ])
            html_items.append(f"""
            <div class="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                 hx-get="/api/knowledge/{s['id']}"
                 hx-target="#sample-detail"
                 hx-swap="innerHTML">
                <div class="font-medium">{s.get('name', s['id'])}</div>
                <div class="text-sm text-gray-600 mt-1">
                    {s.get('process_type', '')} | {s.get('material', '')}
                </div>
                <div class="flex gap-1 mt-2">{tags_html}</div>
            </div>
            """)

        return f"""
        <div class="space-y-3">
            {''.join(html_items)}
        </div>
        """

    except Exception as e:
        logger.error(f"知識ベースリスト取得エラー: {str(e)}")
        return f"""<div class="text-red-500">エラー: {str(e)}</div>"""
