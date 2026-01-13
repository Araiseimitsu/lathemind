"""
工程データモデル
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class Operation(BaseModel):
    """工程データモデル"""

    correction: str = Field(..., description="補正番号（例: A12, S12）")
    tool: str = Field(..., description="ツール番号（例: T1, T11）")
    name: str = Field(..., description="工程名・工具名（例: ZAGURI, DAN-DRILL）")

    class Config:
        json_schema_extra = {
            "example": {
                "correction": "A12",
                "tool": "T1",
                "name": "ZAGURI"
            }
        }


class ProcessData(BaseModel):
    """工程データセット"""

    front_operations: List[Operation] = Field(
        default_factory=list,
        description="正面側工程リスト"
    )
    back_operations: List[Operation] = Field(
        default_factory=list,
        description="背面側工程リスト"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "front_operations": [
                    {"correction": "A12", "tool": "T1", "name": "ZAGURI"},
                    {"correction": "A14", "tool": "T2", "name": "NEJI"}
                ],
                "back_operations": [
                    {"correction": "S12", "tool": "T11", "name": "DAN-DRILL"}
                ]
            }
        }


class ProcessUpdate(BaseModel):
    """工程更新リクエスト"""

    front_operations: List[Operation] = Field(default_factory=list)
    back_operations: List[Operation] = Field(default_factory=list)


class ProcessUploadResponse(BaseModel):
    """XLSXアップロードレスポンス"""

    success: bool = Field(..., description="パース成功与否")
    message: str = Field(..., description="メッセージ")
    data: Optional[ProcessData] = Field(None, description="工程データ")
