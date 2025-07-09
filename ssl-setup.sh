#!/bin/bash

echo "🔐 SSL証明書セットアップ開始"

# SSL ディレクトリ作成
mkdir -p ssl

# 自己署名証明書の生成（開発用）
if [ "$1" = "dev" ] || [ "$1" = "development" ]; then
    echo "📝 開発用の自己署名証明書を生成中..."
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/key.pem \
        -out ssl/cert.pem \
        -subj "/C=JP/ST=Tokyo/L=Tokyo/O=PostureAnalysis/OU=Development/CN=localhost" \
        -addext "subjectAltName=DNS:localhost,DNS:posture-analysis.local,IP:127.0.0.1"
    
    echo "✅ 開発用SSL証明書が生成されました"
    echo "⚠️  この証明書は開発用です。ブラウザで「安全でない」警告が表示されますが、'詳細設定' → '安全でないサイトに進む' で続行できます。"
    
elif [ "$1" = "prod" ] || [ "$1" = "production" ]; then
    echo "🌐 本番用のLet's Encrypt証明書セットアップ"
    
    # ドメイン名の入力
    read -p "ドメイン名を入力してください (例: posture-analysis.example.com): " DOMAIN
    read -p "メールアドレスを入力してください: " EMAIL
    
    if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
        echo "❌ ドメイン名とメールアドレスは必須です"
        exit 1
    fi
    
    echo "🔧 Certbot用のDocker Composeファイルを更新中..."
    
    # docker-compose.override.yml を作成
    cat > docker-compose.override.yml << EOF
version: '3.8'

services:
  nginx:
    volumes:
      - ./ssl:/etc/nginx/ssl
      - ./nginx-prod.conf:/etc/nginx/nginx.conf
      - certbot-www:/var/www/certbot
      - certbot-conf:/etc/letsencrypt
    environment:
      - DOMAIN=${DOMAIN}
      
  certbot:
    image: certbot/certbot
    volumes:
      - certbot-www:/var/www/certbot
      - certbot-conf:/etc/letsencrypt
    command: certonly --webroot --webroot-path=/var/www/certbot --email ${EMAIL} --agree-tos --no-eff-email -d ${DOMAIN}

volumes:
  certbot-www:
  certbot-conf:
EOF
    
    # 本番用nginx設定を作成
    sed "s/posture-analysis.local/${DOMAIN}/g" nginx.conf > nginx-prod.conf
    
    echo "🚀 Let's Encrypt証明書を取得中..."
    docker-compose up certbot
    
    # 証明書をコピー
    docker cp $(docker-compose ps -q certbot):/etc/letsencrypt/live/${DOMAIN}/fullchain.pem ssl/cert.pem
    docker cp $(docker-compose ps -q certbot):/etc/letsencrypt/live/${DOMAIN}/privkey.pem ssl/key.pem
    
    echo "✅ 本番用SSL証明書が設定されました"
    
else
    echo "❓ 使用方法:"
    echo "  開発環境: ./ssl-setup.sh dev"
    echo "  本番環境: ./ssl-setup.sh prod"
    exit 1
fi

# 証明書の権限設定
chmod 600 ssl/key.pem
chmod 644 ssl/cert.pem

echo "🔒 SSL証明書のセットアップが完了しました"
echo ""
echo "📋 次のステップ:"
echo "  1. docker-compose down"
echo "  2. docker-compose up -d"
echo "  3. https://localhost/fixed にアクセス"
echo ""

if [ "$1" = "dev" ]; then
    echo "⚠️  ブラウザで自己署名証明書の警告が表示された場合："
    echo "  - Chrome: '詳細設定' → 'localhost にアクセスする（安全ではありません）'"
    echo "  - Firefox: '詳細情報' → 'リスクを受け入れて続行'"
    echo "  - Safari: '詳細を表示' → 'Webサイトを訪問'"
fi