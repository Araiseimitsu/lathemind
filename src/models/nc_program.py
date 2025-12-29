"""
NCプログラムデータモデル
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class NCProgram:
    """NCプログラム"""
    code: str                               # NCコード本体
    program_number: Optional[str] = None    # プログラム番号 (O0001等)
    analysis: Optional[dict] = None         # 図面解析結果
    referenced_samples: list[str] = field(default_factory=list)  # 参照したサンプル
    warnings: list[str] = field(default_factory=list)            # 警告
    generated_at: datetime = field(default_factory=datetime.now) # 生成日時

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "program_number": self.program_number,
            "analysis": self.analysis,
            "referenced_samples": self.referenced_samples,
            "warnings": self.warnings,
            "generated_at": self.generated_at.isoformat()
        }

    def get_lines(self) -> list[str]:
        """NCコードを行のリストとして取得"""
        return self.code.strip().split("\n")

    def get_line_count(self) -> int:
        """NCコードの行数を取得"""
        return len(self.get_lines())

    def extract_program_number(self) -> Optional[str]:
        """NCコードからプログラム番号を抽出"""
        for line in self.get_lines():
            line = line.strip()
            if line.startswith("O"):
                return line.split()[0] if " " in line else line
        return None


@dataclass
class NCBlock:
    """NCブロック（1行のNCコード）"""
    line_number: int
    content: str
    g_codes: list[str] = field(default_factory=list)
    m_codes: list[str] = field(default_factory=list)
    is_comment: bool = False

    @classmethod
    def parse(cls, line_number: int, content: str) -> "NCBlock":
        """NCコード行をパースしてNCBlockを生成"""
        content = content.strip()
        is_comment = content.startswith("(") or content.startswith(";")

        g_codes = []
        m_codes = []

        if not is_comment:
            import re
            g_codes = re.findall(r"G\d+\.?\d*", content.upper())
            m_codes = re.findall(r"M\d+", content.upper())

        return cls(
            line_number=line_number,
            content=content,
            g_codes=g_codes,
            m_codes=m_codes,
            is_comment=is_comment
        )
