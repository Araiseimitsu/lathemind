# LatheMind

CINCOM L20 NC旋盤の自動プログラミングツール

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.13+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal)

## 概要

**LatheMind** は、Gemini API を活用して図面画像から CINCOM L20 NC旋盤用のプログラムを自動生成する Web アプリケーションです。知識ベース機能により、過去のサンプルを参照しながら高精度なプログラム生成を実現します。

### 主な機能

- 📷 **図面解析**: 図面画像をアップロードして自動解析
- 🤖 **AI プログラム生成**: Gemini API による NC プログラム自動生成
- 📚 **知識ベース管理**: サンプルプログラムの登録・検索・参照
- 🎨 **モダン UI**: HTMX + Tailwind CSS によるレスポンシブな Web インターフェース
- ⚡ **高速処理**: FastAPI による非同期処理

## 対応機種

- **CINCOM L20** (Citizen製 NC旋盤)

## 技術スタック

- **バックエンド**: FastAPI 0.115+
- **AI/ML**: Google Gemini API (gemini-2.0-flash)
- **フロントエンド**: HTMX, Tailwind CSS
- **テンプレートエンジン**: Jinja2
- **Python**: 3.13+

## セットアップ

### 前提条件

- Python 3.13 以上
- Google Gemini API キー

### インストール手順

1. **リポジトリのクローン**

```bash
git clone <repository-url>
cd lathemind
```

1. **仮想環境の作成と有効化**

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

1. **依存パッケージのインストール**

```bash
pip install -r requirements.txt
```

1. **環境変数の設定**

`.env.example` をコピーして `.env` を作成し、必要な情報を入力します。

```bash
copy .env.example .env
```

`.env` ファイルの内容:

```env
# Gemini API設定
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

# アプリケーション設定
APP_NAME=LatheMind
DEBUG=False

# CINCOM設定
CINCOM_MODEL=L20

# 知識ベース設定
KNOWLEDGE_BASE_PATH=knowledge_base
MAX_REFERENCE_SAMPLES=3

# ファイルアップロード設定
MAX_UPLOAD_SIZE=10485760
```

1. **知識ベースディレクトリの作成**

```bash
mkdir knowledge_base
```3.13

## 使用方法

### アプリケーションの起動

```bash
py -3.13 run.py
```

アプリケーションは `http://127.0.0.1:8000` で起動します。

### Web インターフェース

ブラウザで `http://127.0.0.1:8000` にアクセスします。

#### 1. NC プログラム生成

1. メインページで図面画像をアップロード (PNG, JPG, JPEG)
2. 加工条件を入力:
   - 材質 (例: SUS304, S45C)
   - 回転数 (rpm)
   - 送り速度 (mm/min)
   - 加工タイプ (外径、内径、ねじ切り等)
3. 「プログラム生成」ボタンをクリック
4. 生成された NC プログラムを確認・ダウンロード

#### 2. 知識ベース管理

`/knowledge` ページで過去のサンプルを管理できます。

- **サンプル登録**: NC コード、図面、メタデータを登録
- **サンプル検索**: 加工タイプ、材質、タグで検索
- **サンプル削除**: 不要なサンプルを削除

## API 仕様

### エンドポイント一覧

#### NC プログラム生成

```http
POST /api/generate
Content-Type: multipart/form-data

Parameters:
- drawing: 図面画像ファイル (required)
- material: 材質 (required)
- rpm: 回転数 (required)
- feed_rate: 送り速度 (required)
- machining_type: 加工タイプ (required)

Response: 生成された NC プログラム
```

#### 図面解析

```http
POST /api/analyze-drawing
Content-Type: multipart/form-data

Parameters:
- drawing: 図面画像ファイル (required)

Response: 図面解析結果 (寸法、形状等)
```

#### 知識ベース管理

```http
GET /api/knowledge
Response: 全サンプルのリスト

POST /api/knowledge
Content-Type: multipart/form-data
Parameters:
- nc_code: NC プログラム (required)
- drawing: 図面画像 (optional)
- metadata: メタデータ JSON (required)

DELETE /api/knowledge/{sample_id}
Response: 削除結果
```

## プロジェクト構造

```
lathemind/
├── .docs/                      # ドキュメント
│   └── update.md              # 変更履歴
├── .env                       # 環境変数 (gitignore)
├── .env.example               # 環境変数のサンプル
├── knowledge_base/            # 知識ベースデータ
├── requirements.txt           # Python依存パッケージ
├── run.py                     # アプリケーション起動スクリプト
└── src/                       # ソースコード
    ├── __init__.py
    ├── main.py               # FastAPI エントリポイント
    ├── config.py             # 設定管理
    ├── api/                  # API エンドポイント
    │   ├── __init__.py
    │   ├── router.py         # API ルーター
    │   ├── endpoints/        # エンドポイント実装
    │   └── schemas/          # Pydantic スキーマ
    ├── models/               # データモデル
    │   ├── __init__.py
    │   ├── machining.py      # 加工条件モデル
    │   └── nc_program.py     # NC プログラムモデル
    ├── services/             # ビジネスロジック
    │   ├── __init__.py
    │   ├── gemini_service.py # Gemini API 連携
    │   ├── knowledge_service.py # 知識ベース管理
    │   └── nc_generator.py   # NC プログラム生成
    ├── static/               # 静的ファイル
    │   ├── css/             # スタイルシート
    │   ├── js/              # JavaScript
    │   └── images/          # 画像
    ├── templates/            # HTML テンプレート
    │   ├── base.html        # ベーステンプレート
    │   ├── index.html       # メインページ
    │   ├── knowledge.html   # 知識ベース管理ページ
    │   ├── components/      # 再利用可能コンポーネント
    │   └── partials/        # HTMX パーシャル
    └── utils/                # ユーティリティ
        └── __init__.py
```

## 開発ガイドライン

### コード品質

- **1ファイル 1000行以内**: 機能単位でモジュール分割
- **単一責任原則**: 各モジュールは明確な責任を持つ
- **重複コード禁止**: 共通処理は別ファイルに分離

### フロントエンド

- HTML / CSS / JavaScript は必ず別ファイルに分離
- インラインスタイル・スクリプトは禁止

### データベース操作

- 削除・初期化処理は必ず事前にユーザー承認を得る
- 影響範囲を明示する

## トラブルシューティング

### Gemini API エラー

```
Error: API key not found
```

→ `.env` ファイルに正しい `GEMINI_API_KEY` が設定されているか確認してください。

### 知識ベースディレクトリが見つからない

```
Warning: 知識ベースディレクトリが存在しません
```

→ プロジェクトルートに `knowledge_base` ディレクトリを作成してください。

### ポートが使用中

```
Error: Address already in use
```

→ `run.py` の `port` 設定を変更するか、既存のプロセスを終了してください。

## ライセンス

このプロジェクトは社内ツールとして開発されています。

## 変更履歴

詳細な変更履歴は [.docs/update.md](.docs/update.md) を参照してください。

## お問い合わせ

プロジェクトに関する質問や問題は、開発チームまでお問い合わせください。

---

**LatheMind** - CINCOM L20 NC旋盤自動プログラミングツール  
Version 1.0.0 | 2025-01-01
