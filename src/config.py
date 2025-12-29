"""
アプリケーション設定管理
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    """アプリケーション設定"""

    # Gemini API設定
    gemini_api_key: str = Field(default="", description="Gemini API Key")
    gemini_model: str = Field(default="gemini-2.0-flash", description="使用するGeminiモデル")

    # アプリケーション設定
    app_name: str = Field(default="LatheMind", description="アプリケーション名")
    debug: bool = Field(default=False, description="デバッグモード")

    # CINCOM設定
    cincom_model: str = Field(default="L20", description="対応するCINCOM機種")

    # 知識ベース設定
    knowledge_base_path: str = Field(default="knowledge_base", description="知識ベースのパス")
    max_reference_samples: int = Field(default=3, description="参照する最大サンプル数")

    # ファイルアップロード設定
    max_upload_size: int = Field(default=10 * 1024 * 1024, description="最大アップロードサイズ(bytes)")
    allowed_extensions: list[str] = Field(
        default=["png", "jpg", "jpeg"],
        description="許可する画像拡張子"
    )

    @property
    def knowledge_base_abs_path(self) -> Path:
        """知識ベースの絶対パスを取得"""
        return Path(self.knowledge_base_path).resolve()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """設定のシングルトンインスタンスを取得"""
    return Settings()


settings = get_settings()
