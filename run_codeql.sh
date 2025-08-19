#!/bin/bash
set -e

# 1. 設定基本路徑
CODEQL_HOME=/opt/codeql               # CodeQL CLI 安裝路徑
CODEQL_REPO=~/codeql-repo          # CodeQL 官方查詢庫
PROJECT_DIR=/opt/projects/cdcsso    # 你的 Python 專案目錄
DB_NAME=my-db                      # CodeQL database 名稱

# 2. 檢查 CodeQL CLI 是否存在
if ! command -v codeql &> /dev/null; then
    echo "❌ CodeQL CLI 未安裝，請先下載並加到 PATH"
    exit 1
fi

# 3. 下載官方 CodeQL 查詢庫（如果不存在）
if [ ! -d "$CODEQL_REPO" ]; then
    echo "⬇️  下載 CodeQL 查詢庫..."
    git clone https://github.com/github/codeql.git "$CODEQL_REPO"
else
    echo "🔄 更新 CodeQL 查詢庫..."
    cd "$CODEQL_REPO" && git pull && cd -
fi

# 4. 建立 CodeQL Database
echo "🗂️ 建立 CodeQL database..."
rm -rf "$DB_NAME"
codeql database create "$DB_NAME" \
    --language=python \
    --source-root="$PROJECT_DIR"

# 5. 執行分析
echo "🔍 執行 CodeQL 分析..."
codeql database analyze "$DB_NAME" \
    "$CODEQL_REPO/python/ql/src/codeql-suites/python-code-scanning.qls" \
    --format=sarifv2.1.0 \
    --output=results.sarif

# 6. 完成
echo "✅ 分析完成，結果輸出到 results.sarif"
echo "👉 你可以用 VS Code + SARIF Viewer 打開，或上傳到 GitHub Security tab"
