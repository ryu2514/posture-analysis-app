#!/bin/bash

# 姿勢分析アプリ - サーバー起動スクリプト
# 使用方法: ./start_server.sh

echo "🚀 姿勢分析APIサーバー起動中..."
echo "=================================="

# プロジェクトディレクトリに移動
cd "$(dirname "$0")"
PROJECT_DIR=$(pwd)

echo "📁 プロジェクトディレクトリ: $PROJECT_DIR"

# Python パスを設定
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# 依存関係確認
echo "🔍 依存関係確認中..."
python3 -c "
try:
    import mediapipe
    import fastapi
    import uvicorn
    print('✅ 全依存関係OK')
except ImportError as e:
    print(f'❌ 依存関係エラー: {e}')
    print('実行: pip3 install -r backend/requirements.txt')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "依存関係のインストールが必要です"
    exit 1
fi

# ヘルスチェック
echo "🏥 システムヘルスチェック..."
python3 -c "
from backend.app.main import app
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.get('/health')
if response.status_code == 200:
    print('✅ システム正常')
else:
    print(f'❌ システムエラー: {response.status_code}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "システムヘルスチェック失敗"
    exit 1
fi

echo ""
echo "🌐 サーバーアクセス情報:"
echo "   📡 API Root:     http://localhost:8000/"
echo "   🏥 Health:       http://localhost:8000/health"  
echo "   📖 API Docs:     http://localhost:8000/docs"
echo "   📷 Pose API:     http://localhost:8000/analyze-posture"
echo ""
echo "⚠️  サーバーを停止するには Ctrl+C を押してください"
echo "=================================="

# サーバー起動
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload