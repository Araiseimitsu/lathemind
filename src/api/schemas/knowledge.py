"""
知識ベース関連のPydanticスキーマ
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SampleMetadata(BaseModel):
    """サンプルメタデータ"""
    id: str = Field(..., description="サンプルID")
    name: str = Field(..., description="サンプル名")
    description: Optional[str] = Field(default=None, description="説明")
    process_type: str = Field(..., description="加工タイプ")
    material: str = Field(..., description="材質")
    tool_type: Optional[str] = Field(default=None, description="工具タイプ")
    spindle_speed: int = Field(..., description="主軸回転数")
    feed_rate: float = Field(..., description="送り速度")
    depth_of_cut: float = Field(default=0.5, description="切込み量")
    coolant: bool = Field(default=True, description="クーラント使用")
    tags: list[str] = Field(default=[], description="タグ")
    cincom_model: str = Field(default="L20", description="対応機種")
    created_at: Optional[datetime] = Field(default=None, description="作成日時")


class SampleSummary(BaseModel):
    """サンプル概要（リスト表示用）"""
    id: str
    name: str
    process_type: str
    material: str
    tags: list[str]


class SampleDetail(BaseModel):
    """サンプル詳細"""
    metadata: SampleMetadata
    nc_code: str = Field(..., description="NCプログラムコード")
    has_drawing: bool = Field(default=False, description="図面画像の有無")


class KnowledgeIndexResponse(BaseModel):
    """知識ベースインデックスレスポンス"""
    total_samples: int = Field(..., description="総サンプル数")
    samples: list[SampleSummary] = Field(default=[], description="サンプル一覧")
    process_types: list[str] = Field(default=[], description="利用可能な加工タイプ")
    materials: list[str] = Field(default=[], description="利用可能な材質")


class SampleCreateRequest(BaseModel):
    """サンプル作成リクエスト"""
    metadata: SampleMetadata
    nc_code: str = Field(..., description="NCプログラムコード")
