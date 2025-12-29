"""
NCプログラム生成関連のPydanticスキーマ
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProcessInfo(BaseModel):
    """行程情報"""
    process_name: str = Field(..., description="行程名")
    process_type: str = Field(..., description="加工タイプ (roughing/finishing/threading/drilling/grooving)")
    sequence: int = Field(default=1, description="行程順序")
    notes: Optional[str] = Field(default=None, description="備考")


class MachiningConditions(BaseModel):
    """加工条件"""
    material: str = Field(..., description="材質 (SUS304, S45C, A5052等)")
    spindle_speed: int = Field(..., ge=100, le=10000, description="主軸回転数 (rpm)")
    feed_rate: float = Field(..., gt=0, description="送り速度 (mm/rev)")
    depth_of_cut: float = Field(default=0.5, gt=0, description="切込み量 (mm)")
    coolant: bool = Field(default=True, description="クーラント使用")
    tool_number: str = Field(default="T0101", description="工具番号")
    tool_type: Optional[str] = Field(default=None, description="工具タイプ")
    cutting_direction: str = Field(default="negative_z", description="切削方向")
    coordinate_system: str = Field(default="G54", description="ワーク座標系")


class DrawingAnalysis(BaseModel):
    """図面解析結果"""
    process_type: str = Field(..., description="検出された加工タイプ")
    features: list[str] = Field(default=[], description="検出された形状特徴")
    dimensions: dict = Field(default={}, description="検出された寸法")
    tolerances: Optional[dict] = Field(default=None, description="公差情報")
    surface_finish: Optional[str] = Field(default=None, description="表面粗さ")


class GenerateRequest(BaseModel):
    """NCプログラム生成リクエスト"""
    process_info: ProcessInfo
    machining_conditions: MachiningConditions


class GenerateResponse(BaseModel):
    """NCプログラム生成レスポンス"""
    success: bool = Field(..., description="生成成功フラグ")
    nc_program: Optional[str] = Field(default=None, description="生成されたNCプログラム")
    analysis: Optional[DrawingAnalysis] = Field(default=None, description="図面解析結果")
    referenced_samples: list[str] = Field(default=[], description="参照したサンプルID")
    warnings: list[str] = Field(default=[], description="警告メッセージ")
    error: Optional[str] = Field(default=None, description="エラーメッセージ")
    generated_at: datetime = Field(default_factory=datetime.now, description="生成日時")
