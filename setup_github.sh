#!/bin/bash

# GitHub連携セットアップスクリプト
# 使用方法: ./setup_github.sh <your-github-username>

if [ -z "$1" ]; then
    echo "Usage: ./setup_github.sh <your-github-username>"
    echo "Example: ./setup_github.sh kobayashiryuju"
    exit 1
fi

USERNAME=$1
REPO_NAME="posture-analysis-app"

echo "🔗 Setting up GitHub remote for user: $USERNAME"
echo "📦 Repository: $REPO_NAME"

# リモートリポジトリを追加
git remote add origin https://github.com/$USERNAME/$REPO_NAME.git

# デフォルトブランチをmainに設定
git branch -M main

# 初回プッシュ
echo "🚀 Pushing to GitHub..."
git push -u origin main

echo "✅ GitHub連携完了！"
echo "📍 Repository URL: https://github.com/$USERNAME/$REPO_NAME"