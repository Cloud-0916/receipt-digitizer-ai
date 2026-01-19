# 📋 プロジェクト振り返り：レシートデジタル化AI

## 【プロジェクト概要】

| 項目 | 内容 |
|------|------|
| 期間 | 約1ヶ月（週10〜15時間） |
| 成果物 | Webブラウザ上で動作するレシートデジタル化アプリ |
| URL | https://cloud-0916-receipt-digitizer-ai-app-ikvtjm.streamlit.app |
| GitHub | https://github.com/Cloud-0916/receipt-digitizer-ai |

---

## 【環境構築・画像前処理】

### 開発環境の構築

**やったこと：**
- GitHubリポジトリ作成
- Python仮想環境（venv）の構築
- `.gitignore` の設定（APIキーの漏洩防止）

### テストデータの準備

**やったこと：**
- スマホでレシートを5〜10枚撮影
- 意図的に「影付き」「暗い画像」も含めた

### 画像前処理の実装（preprocessing.py）

**最初の実装：大津の二値化**
```python
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
```

**発生した問題：**
- 影付き画像で影の部分が黒く塗りつぶされた

**解決策：適応的二値化に変更**
```python
binary = cv2.adaptiveThreshold(
    denoised, 255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY, 11, 2
)
```

## 【OCR・LLM実装】

### OCRエンジンの実装（ocr_engine.py）

**最初の選択：Tesseract**

**発生した問題：**
- 日本語レシートの認識精度が非常に低い
- 文字化けが多発

**解決策：EasyOCRに変更**
```python
import easyocr
reader = easyocr.Reader(['ja', 'en'])
```

**比較結果：**
| エンジン | 日本語精度 | 処理速度 |
|---------|-----------|---------|
| Tesseract | △ 低い | ○ 速い |
| EasyOCR | ○ 高い | △ やや遅い |


### LLMによる構造化（llm_parser.py）

**API選定の経緯：**

| API | 状況 |
|-----|------|
| OpenAI API | 有料のため見送り |
| Google Gemini API | 無料枠の上限に達した |
| Groq API（Llama 3.3） | 無料で高速、採用 |

**プロンプト設計のポイント：**
```python
prompt = """以下のテキストはレシートをOCRした結果です。
誤字脱字が含まれる可能性があります。
このテキストから情報を抽出し、以下のJSON形式のみを出力してください。
余計な解説は不要です。不明な場合はnullを入れてください。
..."""
```

**ハルシネーション対策：**
- 「不明な場合はnullを返す」と明示的に指示
- 余計な解説を出力しないよう制約

## 【Streamlitアプリ化】

### UIの構築（app.py）

**実装した機能：**
1. ファイルアップローダー（ドラッグ＆ドロップ対応）
2. 元画像と処理済み画像の並列表示
3. OCR結果のテキスト表示
4. 構造化データ（JSON）の表示
5. テーブル形式での表示
6. CSVダウンロードボタン


### パイプラインの結合

**処理フロー：**
```
画像アップロード
    ↓
前処理（preprocessing.py）
    ↓
OCR（ocr_engine.py）
    ↓
LLM構造化（llm_parser.py）
    ↓
CSV出力
```

## 【ドキュメント・デプロイ】

### README.mdの作成

**含めた内容：**
- プロジェクト概要
- システムアーキテクチャ図
- 技術スタック（選定理由付き）
- 技術的なハイライト（課題と解決策）
- セットアップ手順
- 今後の改善計画

### デプロイ

**発生した問題：**
- `requirements.txt` の依存関係エラー
- pandas/numpyのバージョン競合

**解決策：**
- バージョン指定を外したシンプルな `requirements.txt` に変更

```
streamlit
opencv-python-headless
easyocr
groq
python-dotenv
pandas
numpy
pillow
```

## 【技術スタック一覧】

| カテゴリ | 技術 | 選定理由 |
|---------|------|----------|
| 言語 | Python 3.12 | AI/ML領域での豊富なライブラリ |
| 画像処理 | OpenCV | 高速な画像処理、豊富な前処理機能 |
| OCR | EasyOCR | 日本語対応、Tesseractより高精度 |
| LLM | Groq API (Llama 3.3) | 無料枠あり、高速推論 |
| UI | Streamlit | Pythonのみで完結、迅速なプロトタイピング |
| デプロイ | Streamlit Cloud | 無料、GitHub連携が簡単 |

---


---

**作成日：2026年1月**
