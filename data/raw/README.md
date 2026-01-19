# サンプルレシート画像

このフォルダには、デモンストレーション用のサンプル画像が含まれています。

## 📁 ファイル一覧

- `receipt_001_good.jpg` ~ `receipt_012_good.jpg` - きれいな撮影条件
- `receipt_001_difficult.jpg` ~ `receipt_012_difficult.jpg` - 難しい撮影条件

## ⚠️ 注意事項

### 公開ファイル
- `receipt_*_good.jpg` - GitHubで公開されます
- `receipt_*_difficult.jpg` - GitHubで公開されます

### 非公開ファイル（ローカルのみ）
- `blackOut/` フォルダ - 実際のレシート（個人情報含む）
- これらは `.gitignore` で除外されます

## 使用方法

`ash
streamlit run app.py
`

アップロード画面でこれらのサンプル画像を選択してください。
