# フォルダ構造修正スクリプト
# C:\Projects\receipt-digitizer-ai で実行

Write-Host "=== フォルダ構造を修正します ===" -ForegroundColor Green

# 1. srcフォルダを作成
Write-Host "`n[1/6] srcフォルダを作成..." -ForegroundColor Yellow
New-Item -Path "src" -ItemType Directory -Force | Out-Null

# 2. preprocessing.pyを移動
Write-Host "[2/6] preprocessing.pyを移動..." -ForegroundColor Yellow
if (Test-Path "preprocessing.py\preprocessing.py.py") {
    Move-Item -Path "preprocessing.py\preprocessing.py.py" -Destination "src\preprocessing.py" -Force
    Remove-Item -Path "preprocessing.py" -Recurse -Force
    Write-Host "  ✓ preprocessing.pyを移動しました" -ForegroundColor Green
}

# 3. test_preprocessing.pyを移動（存在する場合）
if (Test-Path "test_preprocessing.py\test_preprocessing.py.py") {
    Move-Item -Path "test_preprocessing.py\test_preprocessing.py.py" -Destination "src\test_preprocessing.py" -Force
    Remove-Item -Path "test_preprocessing.py" -Recurse -Force
    Write-Host "  ✓ test_preprocessing.pyを移動しました" -ForegroundColor Green
}

# 4. README.mdを修正
Write-Host "[3/6] README.mdを修正..." -ForegroundColor Yellow
if (Test-Path "data\raw\README.md") {
    Remove-Item -Path "data\raw\README.md" -Recurse -Force
}

$readmeContent = @"
# サンプルレシート画像

このフォルダには、デモンストレーション用のサンプル画像が含まれています。

## 📁 ファイル一覧

- ``receipt_001_good.jpg`` ~ ``receipt_012_good.jpg`` - きれいな撮影条件
- ``receipt_001_difficult.jpg`` ~ ``receipt_012_difficult.jpg`` - 難しい撮影条件

## ⚠️ 注意事項

### 公開ファイル
- ``receipt_*_good.jpg`` - GitHubで公開されます
- ``receipt_*_difficult.jpg`` - GitHubで公開されます

### 非公開ファイル（ローカルのみ）
- ``blackOut/`` フォルダ - 実際のレシート（個人情報含む）
- これらは ``.gitignore`` で除外されます

## 使用方法

```bash
streamlit run app.py
```

アップロード画面でこれらのサンプル画像を選択してください。
"@

Set-Content -Path "data\raw\README.md" -Value $readmeContent -Encoding UTF8
Write-Host "  ✓ README.mdを作成しました" -ForegroundColor Green

# 5. receipt_01_good.jpgフォルダから画像を移動
Write-Host "[4/6] good画像を移動..." -ForegroundColor Yellow
if (Test-Path "data\raw\receipt_01_good.jpg") {
    $count = 0
    Get-ChildItem "data\raw\receipt_01_good.jpg" -Filter *.jpg | ForEach-Object {
        $oldPath = $_.FullName
        $newName = $_.Name -replace '\.jpg\.jpg$', '.jpg'
        $newPath = Join-Path "data\raw" $newName
        Move-Item -Path $oldPath -Destination $newPath -Force
        $count++
    }
    Remove-Item -Path "data\raw\receipt_01_good.jpg" -Recurse -Force
    Write-Host "  ✓ $count 個のgood画像を移動しました" -ForegroundColor Green
}

# 6. receipt_01_difficult.jpgフォルダから画像を移動
Write-Host "[5/6] difficult画像を移動..." -ForegroundColor Yellow
if (Test-Path "data\raw\receipt_01_difficult.jpg") {
    $count = 0
    Get-ChildItem "data\raw\receipt_01_difficult.jpg" -Filter *.jpg | ForEach-Object {
        $oldPath = $_.FullName
        $newName = $_.Name -replace '\.jpg\.jpg$', '.jpg'
        $newPath = Join-Path "data\raw" $newName
        Move-Item -Path $oldPath -Destination $newPath -Force
        $count++
    }
    Remove-Item -Path "data\raw\receipt_01_difficult.jpg" -Recurse -Force
    Write-Host "  ✓ $count 個のdifficult画像を移動しました" -ForegroundColor Green
}

# 7. ground_truth.csvフォルダを削除（ファイルは手動で作成する）
Write-Host "[6/6] ground_truth.csvを整理..." -ForegroundColor Yellow
if (Test-Path "data\ground_truth.csv") {
    if (Test-Path "data\ground_truth.csv\ground_truth.csv.csv") {
        Copy-Item -Path "data\ground_truth.csv\ground_truth.csv.csv" -Destination "data\ground_truth_backup.csv" -Force
        Write-Host "  ✓ バックアップを作成しました: data\ground_truth_backup.csv" -ForegroundColor Green
    }
    Remove-Item -Path "data\ground_truth.csv" -Recurse -Force
}

# 完了メッセージ
Write-Host "`n=== 修正完了！ ===" -ForegroundColor Green
Write-Host "`n次のコマンドで確認してください:" -ForegroundColor Cyan
Write-Host "  tree data /F" -ForegroundColor White
Write-Host "  git status" -ForegroundColor White

# 修正後のフォルダ構造を表示
Write-Host "`n修正後のフォルダ構造:" -ForegroundColor Cyan
tree data /F