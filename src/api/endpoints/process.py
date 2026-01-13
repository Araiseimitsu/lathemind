"""
工程管理APIエンドポイント
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict
import logging

from src.models.process import Operation, ProcessData, ProcessUploadResponse
from src.services.xlsx_parser import parse_process_file_bytes

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/process", tags=["process"])

# メモリストレージ（実運用ではデータベースを使用）
_current_process: ProcessData = ProcessData()


@router.get("", response_model=ProcessData)
async def get_process() -> ProcessData:
    """
    現在の工程データを取得する
    """
    return _current_process


@router.post("/upload", response_model=ProcessUploadResponse)
async def upload_process_file(file: UploadFile = File(...)) -> ProcessUploadResponse:
    """
    XLSX工程管理ファイルをアップロードしてパースする

    Args:
        file: アップロードされたXLSXファイル

    Returns:
        パース結果を含むレスポンス
    """
    global _current_process

    # ファイル形式チェック
    if not file.filename or not file.filename.endswith((".xlsx", ".xls")):
        return ProcessUploadResponse(
            success=False,
            message="XLSXファイルのみアップロード可能です"
        )

    try:
        # ファイル内容を読み込み
        content = await file.read()

        # パース実行
        parsed_data = parse_process_file_bytes(content)

        # 工程データを変換
        front_ops = [
            Operation(
                correction=op.get("correction", ""),
                tool=op.get("tool", ""),
                name=op.get("name", "")
            )
            for op in parsed_data["front_operations"]
        ]
        back_ops = [
            Operation(
                correction=op.get("correction", ""),
                tool=op.get("tool", ""),
                name=op.get("name", "")
            )
            for op in parsed_data["back_operations"]
        ]

        # データを保存
        _current_process = ProcessData(
            front_operations=front_ops,
            back_operations=back_ops
        )

        return ProcessUploadResponse(
            success=True,
            message=f"パース完了: 正面側 {len(front_ops)}工程, 背面側 {len(back_ops)}工程",
            data=_current_process
        )

    except Exception as e:
        logger.error(f"XLSXアップロードエラー: {e}")
        return ProcessUploadResponse(
            success=False,
            message=f"パースエラー: {str(e)}"
        )


@router.put("", response_model=ProcessData)
async def update_process(data: ProcessData) -> ProcessData:
    """
    工程データを更新する

    Args:
        data: 更新する工程データ

    Returns:
        更新後の工程データ
    """
    global _current_process
    _current_process = data
    logger.info(
        f"工程データ更新: 正面側 {len(data.front_operations)}工程, "
        f"背面側 {len(data.back_operations)}工程"
    )
    return _current_process


@router.delete("", response_model=ProcessData)
async def clear_process() -> ProcessData:
    """
    工程データをクリアする
    """
    global _current_process
    _current_process = ProcessData()
    logger.info("工程データをクリアしました")
    return _current_process
