#!/bin/bash

# 🎯 ファイル変更監視自動デプロイ
# ファイル変更を検知して自動デプロイ

set -e

echo "👁️  ファイル変更監視デプロイシステム"
echo "=================================="
echo "📁 監視対象: backend/app/, *.html, *.yml, requirements.txt"
echo "🔄 変更検知時に自動デプロイを実行します"
echo "⏹️  停止: Ctrl+C"
echo ""

# macOSでfswatch、Linuxでinotifywaitをチェック
if command -v fswatch >/dev/null 2>&1; then
    echo "🍎 macOS環境でfswatch使用"
    fswatch -o backend/app/ *.html *.yml requirements.txt 2>/dev/null | while read num; do
        echo "📝 ファイル変更を検知 ($(date))"
        echo "🚀 自動デプロイを開始..."
        ./auto-deploy.sh
        echo "✅ 自動デプロイ完了 ($(date))"
        echo "=================================="
    done
elif command -v inotifywait >/dev/null 2>&1; then
    echo "🐧 Linux環境でinotifywait使用"
    inotifywait -mr --format '%w%f %e' -e modify,create,delete backend/app/ *.html *.yml requirements.txt | while read file event; do
        echo "📝 ファイル変更を検知: $file ($event) ($(date))"
        echo "🚀 自動デプロイを開始..."
        ./auto-deploy.sh
        echo "✅ 自動デプロイ完了 ($(date))"
        echo "=================================="
    done
else
    echo "❌ ファイル監視ツールがインストールされていません"
    echo "📦 インストール方法:"
    echo "  macOS: brew install fswatch"
    echo "  Linux: sudo apt-get install inotify-tools"
    echo ""
    echo "🔄 代替: 手動デプロイスクリプトを使用してください"
    echo "  ./auto-deploy.sh"
fi