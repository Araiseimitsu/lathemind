# LatheMind 変更履歴

## v1.0.0 (2025-01-01)

### 初期リリース

- CINCOM L20 NC旋盤自動プログラミングツール
- Gemini API連携による図面解析・プログラム生成機能
- 知識ベース管理機能（サンプル登録・検索）
- HTMX + Tailwind CSS によるWebUI

### 実装機能

1. **NCプログラム生成**
   - 図面画像アップロード
   - 加工条件入力（材質、回転数、送り等）
   - Gemini APIによる図面解析
   - 知識ベースからの類似サンプル検索
   - NCプログラム自動生成

2. **知識ベース**
   - サンプル登録（NCコード + 図面 + メタデータ）
   - サンプル検索（加工タイプ、材質、タグ）
   - インデックス自動管理

3. **API**
   - POST /api/generate - NCプログラム生成
   - POST /api/analyze-drawing - 図面解析
   - GET/POST/DELETE /api/knowledge - 知識ベース管理
