#!/bin/bash

# 🚀 完全自動デプロイスクリプト
# GitHub Actions不要、完全ローカル実行

set -e

echo "🚀 MediaPipe姿勢分析システム - 自動デプロイ開始"
echo "================================================"

# 1. 既存コンテナの停止・削除
echo "📦 既存コンテナのクリーンアップ..."
docker stop posture-analysis 2>/dev/null || true
docker rm posture-analysis 2>/dev/null || true
docker rmi posture-analysis:latest 2>/dev/null || true

# 2. Dockerイメージのビルド
echo "🔨 Dockerイメージをビルド中..."
docker build -t posture-analysis:latest . --no-cache

# 3. コンテナの起動
echo "🏃 コンテナを起動中..."
docker run -d \
  --name posture-analysis \
  -p 8000:8000 \
  -e PYTHONPATH=/app \
  -e UVICORN_HOST=0.0.0.0 \
  -e UVICORN_PORT=8000 \
  --restart unless-stopped \
  posture-analysis:latest

# 4. 起動待機
echo "⏳ サービス起動を待機中..."
sleep 15

# 5. ヘルスチェック
echo "🔍 ヘルスチェック実行中..."
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

if [ "$HEALTH_CHECK" = "200" ]; then
    echo "✅ デプロイ成功！"
    echo ""
    echo "📱 アクセス先:"
    echo "  • メインアプリ: http://localhost:8000/fixed"
    echo "  • API仕様書:   http://localhost:8000/docs"
    echo "  • ヘルスチェック: http://localhost:8000/health"
    echo ""
    echo "🎉 新機能v2.0が利用可能です："
    echo "  • カラー判定（緑/黄/赤）"
    echo "  • 姿勢タイプ分類"
    echo "  • 座位姿勢分析"
    echo "  • 膝外反/内反・踵骨傾斜測定"
    echo "  • 改善提案システム"
    echo ""
    echo "🔧 管理コマンド:"
    echo "  • 停止: docker stop posture-analysis"
    echo "  • 再起動: docker restart posture-analysis"
    echo "  • ログ確認: docker logs posture-analysis"
else
    echo "❌ デプロイ失敗 (HTTP: $HEALTH_CHECK)"
    echo "📝 ログを確認してください:"
    docker logs posture-analysis
    exit 1
fi

# 6. システム情報表示
echo ""
echo "📊 システム情報:"
docker ps | grep posture-analysis
echo ""
echo "💾 イメージサイズ:"
docker images | grep posture-analysis
echo ""
echo "🎯 デプロイ完了時刻: $(date)"
echo "================================================"