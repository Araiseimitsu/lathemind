"""
NCプログラム生成統括サービス
Gemini APIと知識ベースを連携してNCプログラムを生成
"""
import logging
from typing import Optional
from datetime import datetime

from src.services.gemini_service import GeminiService
from src.services.knowledge_service import KnowledgeService
from src.models.nc_program import NCProgram
from src.config import settings

logger = logging.getLogger(__name__)


class NCGenerator:
    """NCプログラム生成を統括するサービス"""

    def __init__(
        self,
        gemini_service: Optional[GeminiService] = None,
        knowledge_service: Optional[KnowledgeService] = None
    ):
        self.gemini = gemini_service or GeminiService()
        self.knowledge = knowledge_service or KnowledgeService(
            str(settings.knowledge_base_abs_path)
        )

    async def generate(
        self,
        drawing_bytes: bytes,
        process_info: dict,
        machining_conditions: dict,
        mime_type: str = "image/png"
    ) -> NCProgram:
        """
        NCプログラムを生成する

        処理フロー:
        1. 図面を解析
        2. 関連サンプルを検索
        3. プログラムを生成
        4. 検証して返却

        Args:
            drawing_bytes: 図面画像のバイトデータ
            process_info: 行程情報
            machining_conditions: 加工条件
            mime_type: 画像のMIMEタイプ

        Returns:
            NCProgram: 生成されたNCプログラム
        """
        warnings = []

        # Step 1: 図面解析
        logger.info("Step 1: 図面解析を開始")
        analysis = await self.gemini.analyze_drawing(drawing_bytes, mime_type)
        logger.info(f"図面解析完了: {analysis.get('process_type')}, 特徴: {analysis.get('features')}")

        if not self.gemini.is_available():
            warnings.append("Gemini APIが未接続のため、フォールバックモードで動作しています")

        # Step 2: 関連サンプル検索
        logger.info("Step 2: 関連サンプル検索を開始")
        samples = self.knowledge.search_samples(
            process_type=analysis.get("process_type"),
            material=machining_conditions.get("material"),
            features=analysis.get("features", []),
            limit=settings.max_reference_samples
        )
        sample_ids = [s["metadata"]["id"] for s in samples if s and "metadata" in s]
        logger.info(f"関連サンプル検索完了: {len(sample_ids)}件")

        if not sample_ids:
            warnings.append("参照可能なサンプルが見つかりませんでした")

        # サンプルをプロンプト用にフォーマット
        samples_text = self.knowledge.get_samples_for_prompt(sample_ids)

        # Step 3: プログラム生成
        logger.info("Step 3: NCプログラム生成を開始")
        nc_code = await self.gemini.generate_nc_program(
            drawing_analysis=analysis,
            process_info=process_info,
            machining_conditions=machining_conditions,
            reference_samples=samples_text
        )
        logger.info("NCプログラム生成完了")

        # Step 4: 検証
        logger.info("Step 4: NCコード検証を開始")
        validated_code, validation_warnings = self._validate_nc_code(nc_code)
        warnings.extend(validation_warnings)

        # NCProgramオブジェクトを作成
        program = NCProgram(
            code=validated_code,
            analysis=analysis,
            referenced_samples=sample_ids,
            warnings=warnings,
            generated_at=datetime.now()
        )

        # プログラム番号を抽出
        program.program_number = program.extract_program_number()

        logger.info(f"NCプログラム生成完了: {program.get_line_count()}行")
        return program

    def _validate_nc_code(self, code: str) -> tuple[str, list[str]]:
        """
        NCコードの基本検証

        Args:
            code: NCコード

        Returns:
            (検証済みコード, 警告リスト)
        """
        warnings = []
        lines = code.strip().split("\n")

        # プログラム番号の確認
        has_program_number = any(
            line.strip().startswith("O") for line in lines
        )
        if not has_program_number:
            warnings.append("プログラム番号（O番号）がありません")
            # 先頭にO0001を追加
            lines.insert(0, "O0001")

        # M30の確認
        has_end = any(
            "M30" in line.upper() or "M02" in line.upper()
            for line in lines
        )
        if not has_end:
            warnings.append("プログラム終了コード（M30）がありません")
            lines.append("M30")

        # 危険なコードのチェック
        dangerous_codes = ["G10", "G92"]  # 座標系設定等
        for line in lines:
            for dangerous in dangerous_codes:
                if dangerous in line.upper():
                    warnings.append(f"注意: {dangerous} コードが含まれています。確認してください。")

        return "\n".join(lines), warnings

    async def analyze_only(
        self,
        drawing_bytes: bytes,
        mime_type: str = "image/png"
    ) -> dict:
        """
        図面解析のみを実行

        Args:
            drawing_bytes: 図面画像のバイトデータ
            mime_type: 画像のMIMEタイプ

        Returns:
            解析結果の辞書
        """
        return await self.gemini.analyze_drawing(drawing_bytes, mime_type)
