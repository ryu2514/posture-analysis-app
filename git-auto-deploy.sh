#!/bin/bash

# 🔄 Git自動デプロイスクリプト
# コード変更 → 自動ビルド → 自動デプロイ

set -e

echo "🔄 Git自動デプロイシステム"
echo "=========================="

# 1. 最新コードの取得
echo "📥 最新コードを取得中..."
git pull origin main

# 2. 自動デプロイの実行
echo "🚀 自動デプロイを実行中..."
./auto-deploy.sh

echo ""
echo "✅ Git自動デプロイ完了！"
echo "📝 変更内容:"
git log --oneline -5
echo "=========================="