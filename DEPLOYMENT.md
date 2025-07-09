# 🚀 姿勢分析アプリ デプロイメントガイド

## 📋 概要

MediaPipeベースの高精度姿勢分析アプリケーションのデプロイメント手順です。

## 🛠️ 必要な環境

- Docker & Docker Compose
- OpenSSL
- 本番環境の場合: 独自ドメイン

## 🏠 ローカル開発環境

### 基本デプロイ

```bash
# 基本デプロイ（HTTP）
./deploy.sh

# アクセス
http://localhost:8000/fixed
```

### HTTPS対応（開発用）

```bash
# 自己署名証明書でHTTPS有効化
./ssl-setup.sh dev
docker-compose down
docker-compose up -d

# アクセス
https://localhost/fixed
```

## 🌐 本番環境デプロイ

### 前提条件

1. **独自ドメイン取得済み**
   - 例: `posture-analysis.example.com`
   - DNSでサーバーのIPアドレスに設定済み

2. **サーバー要件**
   - Ubuntu 20.04+ / CentOS 8+
   - RAM: 4GB以上推奨
   - CPU: 2コア以上推奨
   - ストレージ: 20GB以上

### 自動デプロイ

```bash
# 本番環境一括デプロイ
./production-deploy.sh
```

設定項目：
- ドメイン名: `posture-analysis.example.com`
- メールアドレス: Let's Encrypt用
- 環境: `production` または `staging`

### 手動デプロイ

#### 1. SSL証明書セットアップ

```bash
./ssl-setup.sh prod
```

#### 2. 本番用設定

```bash
# 環境変数設定
cp .env.production.example .env.production
# ドメイン名などを編集

# 本番用起動
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 モニタリング

### アクセス先

- **アプリケーション**: `https://your-domain.com/fixed`
- **API仕様書**: `https://your-domain.com/docs`
- **ヘルスチェック**: `https://your-domain.com/health`
- **Prometheus**: `http://your-domain.com:9090`

### ログ確認

```bash
# アプリケーションログ
docker-compose -f docker-compose.prod.yml logs posture-analysis

# Nginxログ
docker-compose -f docker-compose.prod.yml logs nginx

# 全体ログ
docker-compose -f docker-compose.prod.yml logs
```

## 🔧 メンテナンス

### SSL証明書更新

```bash
# 手動更新
docker-compose -f docker-compose.prod.yml exec certbot renew

# 自動更新（Cron設定済み）
crontab -l  # 確認
```

### アプリケーション更新

```bash
# コードを更新後
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### バックアップ

```bash
# データベース・ファイルバックアップ
docker-compose -f docker-compose.prod.yml exec posture-analysis \
  tar -czf /app/backup-$(date +%Y%m%d).tar.gz /app/uploads /app/reports
```

## 🔒 セキュリティ設定

### 実装済みセキュリティ機能

- **HTTPS強制**: HTTP→HTTPS自動リダイレクト
- **セキュリティヘッダー**: HSTS, XSS Protection, CSRF対策
- **レート制限**: API・ファイルアップロード制限
- **CORS設定**: オリジン制限
- **CSP**: Content Security Policy適用

### 追加推奨設定

#### ファイアウォール

```bash
# UFW設定例
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

#### Fail2Ban

```bash
# Fail2Ban設定
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

## 📈 パフォーマンス最適化

### リソース制限

```yaml
# docker-compose.prod.yml内
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
```

### Nginx最適化

- Gzip圧縮有効
- Keep-Alive設定
- 静的ファイルキャッシュ
- レート制限

## 🆘 トラブルシューティング

### よくある問題

#### 1. SSL証明書エラー

```bash
# 証明書の確認
openssl x509 -in ssl/cert.pem -text -noout

# Let's Encrypt証明書の再取得
./ssl-setup.sh prod
```

#### 2. コンテナ起動失敗

```bash
# ログ確認
docker-compose -f docker-compose.prod.yml logs

# リソース確認
docker system df
```

#### 3. 画像アップロードエラー

```bash
# ファイルサイズ制限確認
# nginx.conf: client_max_body_size 20M
# FastAPI: 自動設定
```

### ヘルスチェック

```bash
# API接続テスト
curl -f https://your-domain.com/health

# 分析API テスト
curl -X POST https://your-domain.com/analyze-posture \
  -F "file=@test-image.jpg"
```

## 📞 サポート

### ログファイル場所

- アプリケーション: `/app/logs/`
- Nginx: `/var/log/nginx/`
- SSL: `/etc/letsencrypt/logs/`

### 設定ファイル

- Nginx: `nginx-prod.conf`
- Docker: `docker-compose.prod.yml`
- 環境変数: `.env.production`

### 監視項目

- CPU使用率
- メモリ使用量
- ディスク使用量
- レスポンス時間
- エラー率

---

## 🎯 本番環境チェックリスト

- [ ] ドメイン取得・DNS設定
- [ ] サーバー要件確認
- [ ] SSL証明書設定
- [ ] セキュリティ設定
- [ ] モニタリング設定
- [ ] バックアップ設定
- [ ] ログ設定
- [ ] パフォーマンステスト
- [ ] セキュリティテスト
- [ ] 自動更新設定