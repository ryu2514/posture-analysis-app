# 🏥 姿勢分析アプリ

MediaPipeを活用した高精度姿勢分析システム

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-orange)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## 🌟 特徴

- **高精度分析**: MediaPipe による33点ランドマーク検出
- **多方向対応**: 矢状面・前額面・斜め方向の自動判定
- **リアルタイム可視化**: 画像上への骨格線・関節点描画
- **包括的評価**: 8つの姿勢メトリクスによる総合スコア
- **レスポンシブ対応**: PC・タブレット・スマートフォン対応
- **本番運用対応**: Docker・HTTPS・監視機能完備

## 🚀 クイックスタート

### 基本起動

```bash
# リポジトリをクローン
git clone <repository-url>
cd posture-analysis-app

# サーバー起動
./deploy.sh

# ブラウザでアクセス
open http://localhost:8000/fixed
```

### 開発環境（HTTPS対応）

```bash
# SSL証明書生成
./ssl-setup.sh dev

# HTTPS版起動
docker-compose down && docker-compose up -d

# HTTPS アクセス
open https://localhost/fixed
```

## 📊 分析機能

### 対応する姿勢分析

| 項目 | 単位 | 正常範囲 | 説明 |
|------|------|----------|------|
| 骨盤傾斜角 | 度 | 5-15° | 骨盤の前後傾斜 |
| 胸椎後弯角 | 度 | 25-45° | 背中の丸まり具合 |
| 頸椎前弯角 | 度 | 15-35° | 首の前弯カーブ |
| 肩の高さの差 | cm | 0-1.5cm | 左右肩の高低差 |
| 頭部前方偏位 | cm | 0-2.5cm | 頭の前方突出 |
| 腰椎前弯角 | 度 | 30-50° | 腰部のカーブ |
| 肩甲骨前方突出 | cm | 0-2cm | 肩甲骨の前方位置 |
| 体幹側方偏位 | cm | 0-1cm | 体の左右への傾き |

### 検出方向

- **矢状面（Sagittal）**: 横向き - 前後バランス分析
- **前額面（Frontal）**: 正面 - 左右対称性分析  
- **後面（Posterior）**: 後ろ - 背面姿勢分析
- **斜め（Oblique）**: 複合角度分析

## 🎯 使用方法

### 1. 基本操作

1. **画像準備**: 全身が写った画像を用意
2. **アップロード**: ドラッグ&ドロップまたはファイル選択
3. **分析実行**: 自動で姿勢分析が開始
4. **結果確認**: スコアと詳細メトリクスを確認
5. **可視化確認**: 骨格線が描画された画像を確認

### 2. 推奨撮影条件

- **背景**: シンプルで明るい背景
- **照明**: 十分な明るさ、逆光を避ける
- **服装**: 体のラインが分かりやすい服装
- **距離**: 全身が画面に収まる距離
- **角度**: 真横または真正面

### 3. ファイル要件

- **形式**: JPEG, PNG, BMP
- **サイズ**: 最大 10MB
- **解像度**: 推奨 640x480 以上

## 🔧 開発・デプロイ

### 開発環境

```bash
# 依存関係インストール
pip install -r requirements.txt

# 開発サーバー起動
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 本番デプロイ

```bash
# 自動本番デプロイ
./production-deploy.sh

# 手動デプロイ
./ssl-setup.sh prod
docker-compose -f docker-compose.prod.yml up -d
```

### 環境設定

```bash
# 環境変数設定例
MEDIAPIPE_MODEL_COMPLEXITY=2
MEDIAPIPE_MIN_DETECTION_CONFIDENCE=0.7
ALLOWED_ORIGINS=https://your-domain.com
```

## 📱 アクセス先

### 本番環境
- **メインアプリ**: `https://your-domain.com/fixed`
- **ユーザーテスト**: `https://your-domain.com/test`
- **API仕様書**: `https://your-domain.com/docs`
- **ヘルスチェック**: `https://your-domain.com/health`

### 開発環境
- **メインアプリ**: `http://localhost:8000/fixed`
- **デバッグ版**: `http://localhost:8000/debug`
- **ユーザーテスト**: `http://localhost:8000/test`

## 🧪 テスト

### ユーザー受け入れテスト

```bash
# テストページアクセス
open http://localhost:8000/test
```

**テスト項目**:
- ✅ 基本アップロード機能
- ✅ 矢状面・前額面分析
- ✅ 骨格線可視化
- ✅ スコア計算
- ✅ パフォーマンス測定
- ✅ エラーハンドリング

### 自動テスト

```bash
# APIテスト
curl -X POST http://localhost:8000/analyze-posture \
  -F "file=@test-image.jpg"

# ヘルスチェック
curl http://localhost:8000/health
```

## 📈 監視・メンテナンス

### ログ確認

```bash
# アプリケーションログ
docker-compose logs posture-analysis

# Nginxログ  
docker-compose logs nginx

# リアルタイム監視
docker-compose logs -f
```

### メトリクス監視

- **Prometheus**: `http://localhost:9090`
- **処理時間**: 平均5秒以内
- **成功率**: 95%以上
- **メモリ使用量**: 2GB以下

### バックアップ

```bash
# データバックアップ
docker-compose exec posture-analysis \
  tar -czf backup-$(date +%Y%m%d).tar.gz uploads reports
```

## 🔒 セキュリティ

### 実装済み機能

- **HTTPS強制**: SSL/TLS暗号化
- **セキュリティヘッダー**: HSTS, CSP, XSS対策
- **レート制限**: API・アップロード制限
- **CORS設定**: オリジン制限
- **ファイル検証**: ファイル形式・サイズチェック

### 追加推奨設定

```bash
# ファイアウォール設定
sudo ufw allow 22,80,443/tcp

# Fail2Ban設定
sudo apt install fail2ban
```

## 📚 API リファレンス

### 姿勢分析API

```http
POST /analyze-posture
Content-Type: multipart/form-data

file: <image-file>
```

**レスポンス**:
```json
{
  "landmarks": {...},
  "metrics": {
    "pelvic_tilt": 8.5,
    "thoracic_kyphosis": 35.2,
    "cervical_lordosis": 25.1,
    "shoulder_height_difference": 0.8,
    "head_forward_posture": 1.2,
    "lumbar_lordosis": 42.3,
    "scapular_protraction": 1.5,
    "trunk_lateral_deviation": 0.3
  },
  "overall_score": 87.5,
  "pose_orientation": "sagittal",
  "confidence": 0.95
}
```

### ヘルスチェックAPI

```http
GET /health
```

**レスポンス**:
```json
{
  "status": "healthy",
  "mediapipe": "ready"
}
```

## 🤝 貢献

### 開発への参加

1. フォークしてブランチ作成
2. 機能追加・バグ修正
3. テスト実行
4. プルリクエスト作成

### 課題報告

- **バグ報告**: GitHub Issues
- **機能要望**: GitHub Discussions  
- **セキュリティ**: security@example.com

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照

## 🙏 謝辞

- **MediaPipe**: Google AI による姿勢推定技術
- **FastAPI**: 高性能Web APIフレームワーク
- **Docker**: コンテナ化技術
- **Nginx**: 高性能Webサーバー

---

## 📞 サポート

### ドキュメント
- [デプロイメントガイド](DEPLOYMENT.md)
- [ユーザーテストガイド](USER_TESTING.md)
- [トラブルシューティング](TROUBLESHOOTING.md)

### 連絡先
- **技術サポート**: tech-support@example.com
- **一般問い合わせ**: info@example.com

**開発チーム**: AI/ML Engineer × MediaPipe Expert