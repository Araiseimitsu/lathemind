"""
知識ベース管理サービス
サンプルコードと図面の検索・管理を行う
"""
import json
import logging
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class KnowledgeService:
    """知識ベースの検索・管理を行うサービス"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.samples_path = self.base_path / "samples"
        self.index_path = self.base_path / "index.json"
        self._ensure_structure()
        self.index = self._load_index()

    def _ensure_structure(self) -> None:
        """ディレクトリ構造を確保"""
        self.samples_path.mkdir(parents=True, exist_ok=True)
        if not self.index_path.exists():
            self._save_index(self._create_empty_index())

    def _create_empty_index(self) -> dict:
        """空のインデックスを作成"""
        return {
            "version": "1.0",
            "total_samples": 0,
            "samples": [],
            "process_types": ["roughing", "finishing", "threading", "drilling", "grooving"],
            "materials": ["SUS304", "SUS316", "S45C", "A5052", "C3604"]
        }

    def _load_index(self) -> dict:
        """インデックスファイルを読み込む"""
        try:
            if self.index_path.exists():
                content = self.index_path.read_text(encoding="utf-8")
                return json.loads(content)
        except Exception as e:
            logger.error(f"インデックス読み込みエラー: {e}")
        return self._create_empty_index()

    def _save_index(self, index: dict) -> None:
        """インデックスファイルを保存"""
        try:
            self.index_path.write_text(
                json.dumps(index, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            logger.error(f"インデックス保存エラー: {e}")

    def _rebuild_index(self) -> None:
        """インデックスを再構築"""
        samples = []
        process_types = set()
        materials = set()

        for sample_dir in self.samples_path.iterdir():
            if sample_dir.is_dir():
                metadata_path = sample_dir / "metadata.json"
                if metadata_path.exists():
                    try:
                        meta = json.loads(metadata_path.read_text(encoding="utf-8"))
                        samples.append({
                            "id": meta.get("id", sample_dir.name),
                            "name": meta.get("name", ""),
                            "path": f"samples/{sample_dir.name}",
                            "process_type": meta.get("process_type", ""),
                            "material": meta.get("material", ""),
                            "tags": meta.get("tags", [])
                        })
                        if meta.get("process_type"):
                            process_types.add(meta["process_type"])
                        if meta.get("material"):
                            materials.add(meta["material"])
                    except Exception as e:
                        logger.warning(f"メタデータ読み込みエラー ({sample_dir}): {e}")

        self.index = {
            "version": "1.0",
            "total_samples": len(samples),
            "samples": samples,
            "process_types": list(process_types) or self.index.get("process_types", []),
            "materials": list(materials) or self.index.get("materials", [])
        }
        self._save_index(self.index)

    def get_index(self) -> dict:
        """インデックスを取得"""
        return self.index

    def search_samples(
        self,
        process_type: Optional[str] = None,
        material: Optional[str] = None,
        features: Optional[list] = None,
        limit: int = 3
    ) -> list[dict]:
        """
        条件に合致するサンプルを検索

        スコアリング:
        - process_type一致: +10点
        - material一致: +5点
        - features一致: 各+2点
        """
        scored_samples = []

        for sample_meta in self.index.get("samples", []):
            score = 0

            if process_type and sample_meta.get("process_type") == process_type:
                score += 10

            if material and sample_meta.get("material") == material:
                score += 5

            if features:
                sample_tags = set(sample_meta.get("tags", []))
                matching_features = set(features) & sample_tags
                score += len(matching_features) * 2

            if score > 0:
                scored_samples.append((score, sample_meta))

        # スコア順にソートして上位を返却
        scored_samples.sort(key=lambda x: x[0], reverse=True)
        top_samples = [s[1] for s in scored_samples[:limit]]

        # 詳細データを読み込んで返却
        return [self.get_sample_detail(s["id"]) for s in top_samples if self.get_sample_detail(s["id"])]

    def get_sample_detail(self, sample_id: str) -> Optional[dict]:
        """サンプルの詳細情報を取得"""
        sample_path = self.samples_path / sample_id

        if not sample_path.exists():
            return None

        try:
            metadata_path = sample_path / "metadata.json"
            program_path = sample_path / "program.nc"
            drawing_path = sample_path / "drawing.png"

            if not metadata_path.exists() or not program_path.exists():
                return None

            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            nc_code = program_path.read_text(encoding="utf-8")

            return {
                "metadata": metadata,
                "nc_code": nc_code,
                "has_drawing": drawing_path.exists()
            }
        except Exception as e:
            logger.error(f"サンプル詳細取得エラー ({sample_id}): {e}")
            return None

    def get_drawing_path(self, sample_id: str) -> Optional[str]:
        """サンプルの図面パスを取得"""
        drawing_path = self.samples_path / sample_id / "drawing.png"
        if drawing_path.exists():
            return str(drawing_path)

        # JPG形式もチェック
        jpg_path = self.samples_path / sample_id / "drawing.jpg"
        if jpg_path.exists():
            return str(jpg_path)

        return None

    def register_sample(
        self,
        sample_id: str,
        metadata: dict,
        nc_code: str,
        drawing_bytes: Optional[bytes] = None
    ) -> bool:
        """新しいサンプルを登録"""
        sample_path = self.samples_path / sample_id

        try:
            # ディレクトリ作成
            sample_path.mkdir(parents=True, exist_ok=True)

            # メタデータ保存
            metadata["id"] = sample_id
            if "created_at" not in metadata:
                metadata["created_at"] = datetime.now().isoformat()

            (sample_path / "metadata.json").write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

            # NCコード保存
            (sample_path / "program.nc").write_text(nc_code, encoding="utf-8")

            # 図面保存
            if drawing_bytes:
                (sample_path / "drawing.png").write_bytes(drawing_bytes)

            # インデックス再構築
            self._rebuild_index()

            logger.info(f"サンプル登録成功: {sample_id}")
            return True

        except Exception as e:
            logger.error(f"サンプル登録エラー ({sample_id}): {e}")
            # ロールバック
            if sample_path.exists():
                shutil.rmtree(sample_path, ignore_errors=True)
            return False

    def delete_sample(self, sample_id: str) -> bool:
        """サンプルを削除"""
        sample_path = self.samples_path / sample_id

        if not sample_path.exists():
            return False

        try:
            shutil.rmtree(sample_path)
            self._rebuild_index()
            logger.info(f"サンプル削除成功: {sample_id}")
            return True
        except Exception as e:
            logger.error(f"サンプル削除エラー ({sample_id}): {e}")
            return False

    def get_samples_for_prompt(self, sample_ids: list[str]) -> str:
        """
        プロンプト用にサンプルをフォーマットして取得
        """
        result_parts = []

        for sample_id in sample_ids:
            detail = self.get_sample_detail(sample_id)
            if detail:
                meta = detail["metadata"]
                result_parts.append(f"""
### サンプル: {meta.get('name', sample_id)}
- 加工タイプ: {meta.get('process_type', 'N/A')}
- 材質: {meta.get('material', 'N/A')}
- 主軸回転数: {meta.get('spindle_speed', 'N/A')} rpm
- 送り速度: {meta.get('feed_rate', 'N/A')} mm/rev

```nc
{detail['nc_code']}
```
""")

        return "\n".join(result_parts) if result_parts else "参照サンプルなし"
