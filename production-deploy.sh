#!/bin/bash

echo "🚀 姿勢分析アプリ 本番デプロイメント"

# 設定確認
echo "📋 デプロイメント設定確認"
echo "================================"

read -p "ドメイン名 (例: posture-analysis.example.com): " DOMAIN
read -p "メールアドレス (Let's Encrypt用): " EMAIL
read -p "環境 (production/staging): " ENVIRONMENT

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo "❌ ドメイン名とメールアドレスは必須です"
    exit 1
fi

ENVIRONMENT=${ENVIRONMENT:-production}

echo ""
echo "🔧 設定内容:"
echo "  ドメイン: $DOMAIN"
echo "  メール: $EMAIL"
echo "  環境: $ENVIRONMENT"
echo ""

read -p "この設定で続行しますか？ (y/N): " CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "❌ デプロイメントをキャンセルしました"
    exit 1
fi

# 環境変数ファイル作成
echo "📝 環境設定ファイル作成中..."

cat > .env.production << EOF
# 本番環境設定
DOMAIN=${DOMAIN}
EMAIL=${EMAIL}
ENVIRONMENT=${ENVIRONMENT}

# FastAPI設定
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8000
PYTHONPATH=/app

# MediaPipe設定（本番用最適化）
MEDIAPIPE_MODEL_COMPLEXITY=2
MEDIAPIPE_MIN_DETECTION_CONFIDENCE=0.7
MEDIAPIPE_MIN_TRACKING_CONFIDENCE=0.7

# セキュリティ設定
ALLOWED_ORIGINS=https://${DOMAIN},https://www.${DOMAIN}
SECRET_KEY=$(openssl rand -hex 32)

# ログ設定
LOG_LEVEL=INFO
LOG_FORMAT=json

# パフォーマンス設定
MAX_WORKERS=4
WORKER_CLASS=uvicorn.workers.UvicornWorker
EOF

# 本番用Docker Compose設定
echo "🐳 本番用Docker Compose設定作成中..."

cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  posture-analysis:
    build: 
      context: .
      dockerfile: Dockerfile.prod
    restart: unless-stopped
    environment:
      - ENVIRONMENT=${ENVIRONMENT}
    env_file:
      - .env.production
    volumes:
      - uploads:/app/uploads
      - reports:/app/reports
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx-prod.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - certbot-www:/var/www/certbot:ro
      - certbot-conf:/etc/letsencrypt:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - posture-analysis
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'

  certbot:
    image: certbot/certbot
    volumes:
      - certbot-www:/var/www/certbot
      - certbot-conf:/etc/letsencrypt
    command: renew --quiet
    depends_on:
      - nginx

  # モニタリング（オプション）
  prometheus:
    image: prom/prometheus:latest
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'

volumes:
  uploads:
  reports:
  certbot-www:
  certbot-conf:
  prometheus-data:

networks:
  default:
    driver: bridge
EOF

# 本番用Dockerfile
echo "📦 本番用Dockerfile作成中..."

cat > Dockerfile.prod << EOF
FROM python:3.9-slim

# システムパッケージのインストール
RUN apt-get update && apt-get install -y \\
    libgl1-mesa-glx \\
    libglib2.0-0 \\
    libsm6 \\
    libxext6 \\
    libxrender-dev \\
    libgomp1 \\
    wget \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# セキュリティ用の非rootユーザー作成
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 作業ディレクトリ設定
WORKDIR /app

# 依存関係ファイルをコピー
COPY requirements.txt .

# Python依存関係のインストール（本番用最適化）
RUN pip install --no-cache-dir --upgrade pip \\
    && pip install --no-cache-dir -r requirements.txt \\
    && pip install gunicorn

# アプリケーションコードをコピー
COPY . .

# ディレクトリ作成と権限設定
RUN mkdir -p uploads reports logs \\
    && chown -R appuser:appuser /app

# 非rootユーザーに切り替え
USER appuser

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# 本番用サーバー起動
CMD ["gunicorn", "backend.app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--access-logfile", "/app/logs/access.log", "--error-logfile", "/app/logs/error.log"]
EOF

# 本番用nginx設定生成
echo "🌐 本番用nginx設定生成中..."
sed "s/posture-analysis.local/${DOMAIN}/g" nginx.conf > nginx-prod.conf

# SSL証明書セットアップ
echo "🔐 SSL証明書セットアップ..."
./ssl-setup.sh prod

# 必要なディレクトリ作成
mkdir -p logs/nginx monitoring

# Prometheus設定（基本的なもの）
cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'posture-analysis'
    static_configs:
      - targets: ['posture-analysis:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
EOF

# 本番環境デプロイ
echo "🚀 本番環境デプロイ開始..."

# 既存のコンテナを停止
docker-compose -f docker-compose.prod.yml down

# イメージをビルド
docker-compose -f docker-compose.prod.yml build --no-cache

# コンテナを起動
docker-compose -f docker-compose.prod.yml up -d

# ヘルスチェック
echo "🏥 ヘルスチェック実行中..."
sleep 30

max_attempts=60
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -f -s https://${DOMAIN}/health > /dev/null; then
        echo "✅ 本番環境が正常に起動しました！"
        echo ""
        echo "🌐 アクセス方法:"
        echo "   - メインサイト: https://${DOMAIN}/"
        echo "   - デモページ: https://${DOMAIN}/fixed"
        echo "   - API仕様書: https://${DOMAIN}/docs"
        echo "   - ヘルスチェック: https://${DOMAIN}/health"
        echo "   - モニタリング: http://${DOMAIN}:9090 (Prometheus)"
        echo ""
        echo "🎉 本番デプロイメント完了！"
        
        # SSL証明書の自動更新設定
        echo "⏰ SSL証明書自動更新のCronジョブ設定..."
        (crontab -l 2>/dev/null; echo "0 12 * * * cd $(pwd) && docker-compose -f docker-compose.prod.yml exec certbot renew --quiet") | crontab -
        
        exit 0
    fi
    
    echo "⏳ 起動待機中... (${attempt}/${max_attempts})"
    sleep 5
    attempt=$((attempt + 1))
done

echo "❌ 本番環境の起動に失敗しました"
echo "📋 ログを確認してください:"
echo "   docker-compose -f docker-compose.prod.yml logs"
exit 1