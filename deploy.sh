#!/bin/bash

echo "🚀 姿勢分析アプリ デプロイメント開始"

# 環境チェック
if ! command -v docker &> /dev/null; then
    echo "❌ Dockerがインストールされていません"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Composeがインストールされていません"
    exit 1
fi

# 必要なディレクトリを作成
echo "📁 ディレクトリ作成中..."
mkdir -p uploads reports ssl

# .gitkeepファイルを作成
touch uploads/.gitkeep reports/.gitkeep

# 既存のコンテナを停止・削除
echo "🛑 既存のコンテナを停止中..."
docker-compose down

# イメージをビルド
echo "🔨 Dockerイメージをビルド中..."
docker-compose build --no-cache

# コンテナを起動
echo "🚀 コンテナを起動中..."
docker-compose up -d

# ヘルスチェック
echo "🏥 ヘルスチェック実行中..."
sleep 10

max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -f -s http://localhost:8000/health > /dev/null; then
        echo "✅ アプリケーションが正常に起動しました！"
        echo ""
        echo "📱 アクセス方法:"
        echo "   - デモページ: http://localhost:8000/fixed"
        echo "   - API仕様書: http://localhost:8000/docs"
        echo "   - ヘルスチェック: http://localhost:8000/health"
        echo ""
        echo "🎉 デプロイメント完了！"
        exit 0
    fi
    
    echo "⏳ 起動待機中... (${attempt}/${max_attempts})"
    sleep 2
    attempt=$((attempt + 1))
done

echo "❌ アプリケーションの起動に失敗しました"
echo "📋 ログを確認してください:"
echo "   docker-compose logs posture-analysis"
exit 1