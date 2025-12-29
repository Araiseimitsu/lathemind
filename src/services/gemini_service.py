"""
Gemini API連携サービス
図面解析とNCプログラム生成を担当
"""
import logging
import base64
from typing import Optional

from google import genai
from google.genai import types

from src.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Gemini APIとの連携を管理するサービスクラス"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        self.model = settings.gemini_model
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Geminiクライアントを初期化"""
        if not self.api_key:
            logger.warning("Gemini API キーが設定されていません")
            return

        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"Gemini API クライアント初期化成功 (モデル: {self.model})")
        except Exception as e:
            logger.error(f"Gemini API クライアント初期化エラー: {e}")
            self.client = None

    def is_available(self) -> bool:
        """APIが利用可能かどうか"""
        return self.client is not None

    async def analyze_drawing(
        self,
        image_bytes: bytes,
        mime_type: str = "image/png"
    ) -> dict:
        """
        図面画像を解析し、加工特徴を抽出

        Args:
            image_bytes: 画像のバイトデータ
            mime_type: MIMEタイプ

        Returns:
            解析結果の辞書
        """
        if not self.is_available():
            return self._get_fallback_analysis()

        try:
            prompt = self._build_analysis_prompt()

            # 画像データを準備
            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            )

            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt, image_part],
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=2000
                )
            )

            # レスポンスをパース
            result_text = response.text
            return self._parse_analysis_response(result_text)

        except Exception as e:
            logger.error(f"図面解析エラー: {e}")
            return self._get_fallback_analysis()

    async def generate_nc_program(
        self,
        drawing_analysis: dict,
        process_info: dict,
        machining_conditions: dict,
        reference_samples: str
    ) -> str:
        """
        NCプログラムを生成

        Args:
            drawing_analysis: 図面解析結果
            process_info: 行程情報
            machining_conditions: 加工条件
            reference_samples: 参照サンプル（フォーマット済み文字列）

        Returns:
            生成されたNCプログラム
        """
        if not self.is_available():
            return self._get_fallback_nc_program(machining_conditions)

        try:
            prompt = self._build_generation_prompt(
                drawing_analysis,
                process_info,
                machining_conditions,
                reference_samples
            )

            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=4000
                )
            )

            nc_code = response.text

            # コードブロックの抽出
            nc_code = self._extract_nc_code(nc_code)

            return nc_code

        except Exception as e:
            logger.error(f"NCプログラム生成エラー: {e}")
            return self._get_fallback_nc_program(machining_conditions)

    def _build_analysis_prompt(self) -> str:
        """図面解析用プロンプトを構築"""
        return """あなたはCINCOM NC旋盤のエキスパートプログラマーです。
提供された図面画像を解析し、以下の情報をJSON形式で抽出してください。

## 抽出項目
1. process_type: 加工タイプ（roughing/finishing/threading/drilling/grooving/facing/boring のいずれか）
2. features: 検出された形状特徴のリスト（外径、内径、テーパー、R面取り、ねじ、溝 等）
3. dimensions: 主要寸法の辞書
   - diameter_start: 開始直径 (mm)
   - diameter_end: 終了直径 (mm)
   - length: 加工長さ (mm)
   - taper_angle: テーパー角度 (度) ※ある場合
   - radius: R寸法 (mm) ※ある場合
4. tolerances: 公差情報（検出できる場合）
5. surface_finish: 表面粗さ指示（検出できる場合）

## 出力形式
JSONのみを出力してください（説明不要）:

```json
{
  "process_type": "...",
  "features": ["...", "..."],
  "dimensions": {
    "diameter_start": 0.0,
    "diameter_end": 0.0,
    "length": 0.0
  },
  "tolerances": null,
  "surface_finish": null
}
```
"""

    def _build_generation_prompt(
        self,
        analysis: dict,
        process_info: dict,
        conditions: dict,
        samples: str
    ) -> str:
        """NCプログラム生成用プロンプトを構築"""
        import json

        return f"""あなたはCINCOM NC旋盤のエキスパートプログラマーです。
以下の情報を基に、CINCOM {settings.cincom_model}用のNCプログラムを生成してください。

## 図面解析結果
```json
{json.dumps(analysis, ensure_ascii=False, indent=2)}
```

## 行程情報
- 行程名: {process_info.get('process_name', 'N/A')}
- 加工タイプ: {process_info.get('process_type', 'N/A')}
- 備考: {process_info.get('notes', 'なし')}

## 加工条件
- 材質: {conditions.get('material', 'N/A')}
- 主軸回転数: {conditions.get('spindle_speed', 1000)} rpm
- 送り速度: {conditions.get('feed_rate', 0.1)} mm/rev
- 切込み量: {conditions.get('depth_of_cut', 0.5)} mm
- クーラント: {'使用' if conditions.get('coolant', True) else '不使用'}
- 工具番号: {conditions.get('tool_number', 'T0101')}
- 工具タイプ: {conditions.get('tool_type', 'N/A')}
- ワーク座標系: {conditions.get('coordinate_system', 'G54')}

## 参考サンプルプログラム
{samples}

## 要件
1. FANUC系Gコード準拠
2. プログラム番号は O0001 から開始
3. 安全なアプローチ/リトラクト動作を含める
4. 適切なコメントを日本語で付与
5. G28によるリファレンス点復帰を含める
6. M30でプログラム終了

## 出力
NCプログラムのコードのみを出力してください。説明は不要です。
コードブロック（```nc ... ```）で囲んでください。
"""

    def _parse_analysis_response(self, response_text: str) -> dict:
        """解析レスポンスをパース"""
        import json
        import re

        try:
            # JSONブロックを抽出
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # JSONブロックがない場合は全体をパース試行
                json_str = response_text

            result = json.loads(json_str)

            # 必須フィールドの確認
            return {
                "process_type": result.get("process_type", "roughing"),
                "features": result.get("features", []),
                "dimensions": result.get("dimensions", {}),
                "tolerances": result.get("tolerances"),
                "surface_finish": result.get("surface_finish")
            }

        except Exception as e:
            logger.warning(f"解析レスポンスのパースに失敗: {e}")
            return self._get_fallback_analysis()

    def _extract_nc_code(self, response_text: str) -> str:
        """レスポンスからNCコードを抽出"""
        import re

        # コードブロックを探す
        code_match = re.search(r'```(?:nc)?\s*(.*?)\s*```', response_text, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()

        # コードブロックがない場合はそのまま返す
        return response_text.strip()

    def _get_fallback_analysis(self) -> dict:
        """フォールバック用の解析結果"""
        return {
            "process_type": "roughing",
            "features": ["外径"],
            "dimensions": {
                "diameter_start": 20.0,
                "diameter_end": 20.0,
                "length": 30.0
            },
            "tolerances": None,
            "surface_finish": None
        }

    def _get_fallback_nc_program(self, conditions: dict) -> str:
        """フォールバック用のNCプログラム"""
        tool = conditions.get("tool_number", "T0101")
        speed = conditions.get("spindle_speed", 1000)
        feed = conditions.get("feed_rate", 0.1)

        return f"""O0001
(CINCOM {settings.cincom_model} - 自動生成プログラム)
(Gemini API未接続のためテンプレートを使用)

N10 G28 U0 W0
N20 G50 S3000
N30 {tool}
N40 G96 S{speed} M03
N50 G00 X22.0 Z2.0 M08
N60 G01 Z0 F{feed}
N70 X20.0
N80 Z-30.0
N90 G00 X22.0 Z2.0
N100 G28 U0 W0 M09
N110 M01

M30
"""
