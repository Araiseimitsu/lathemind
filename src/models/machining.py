"""
加工条件データモデル
"""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class ProcessType(str, Enum):
    """加工タイプ"""
    ROUGHING = "roughing"      # 荒加工
    FINISHING = "finishing"    # 仕上げ加工
    THREADING = "threading"    # ねじ切り
    DRILLING = "drilling"      # 穴あけ
    GROOVING = "grooving"      # 溝入れ
    FACING = "facing"          # 端面加工
    BORING = "boring"          # 中ぐり


class Material(str, Enum):
    """材質"""
    SUS304 = "SUS304"
    SUS316 = "SUS316"
    S45C = "S45C"
    S50C = "S50C"
    A5052 = "A5052"
    A6061 = "A6061"
    C3604 = "C3604"
    C2801 = "C2801"


@dataclass
class CuttingCondition:
    """切削条件"""
    spindle_speed: int          # 主軸回転数 (rpm)
    feed_rate: float            # 送り速度 (mm/rev)
    depth_of_cut: float         # 切込み量 (mm)
    coolant: bool = True        # クーラント使用

    def to_dict(self) -> dict:
        return {
            "spindle_speed": self.spindle_speed,
            "feed_rate": self.feed_rate,
            "depth_of_cut": self.depth_of_cut,
            "coolant": self.coolant
        }


@dataclass
class Tool:
    """工具情報"""
    number: str                 # 工具番号 (T0101等)
    type: Optional[str] = None  # 工具タイプ (CNMG120408等)
    offset: int = 1             # 工具補正番号
    nose_radius: float = 0.4    # ノーズR

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "type": self.type,
            "offset": self.offset,
            "nose_radius": self.nose_radius
        }


@dataclass
class MachiningOperation:
    """加工オペレーション"""
    process_type: ProcessType
    material: str
    cutting_condition: CuttingCondition
    tool: Tool
    coordinate_system: str = "G54"
    cutting_direction: str = "negative_z"
    notes: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "process_type": self.process_type.value,
            "material": self.material,
            "cutting_condition": self.cutting_condition.to_dict(),
            "tool": self.tool.to_dict(),
            "coordinate_system": self.coordinate_system,
            "cutting_direction": self.cutting_direction,
            "notes": self.notes
        }
