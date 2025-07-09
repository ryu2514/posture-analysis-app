# 🔧 Flutter Web環境セットアップガイド

## 📋 概要

このガイドでは、姿勢分析アプリのFlutter Webフロントエンドを起動する方法を説明します。

## ⚡ クイックスタート（推奨）

### 1. Flutter SDK インストール

```bash
# macOS の場合
curl -O https://storage.googleapis.com/flutter_infra_release/releases/stable/macos/flutter_macos_arm64_3.19.0-stable.tar.xz
tar xf flutter_macos_arm64_3.19.0-stable.tar.xz
export PATH="$PWD/flutter/bin:$PATH"

# パスを永続化
echo 'export PATH="$HOME/flutter/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 2. 環境確認

```bash
flutter doctor
flutter config --enable-web
```

### 3. プロジェクト起動

```bash
cd /Users/kobayashiryuju/posture-analysis-app/frontend
flutter pub get
flutter run -d web --web-port 3000
```

## 🌐 代替案：シンプルHTMLデモ

Flutter環境構築が困難な場合、基本的なHTML/JavaScriptデモを提供します：

### HTMLテストページ作成

```bash
# プロジェクトルートで実行
python3 create_demo_page.py
```

### アクセス方法

1. バックエンドサーバー起動: `./start_server.sh`
2. ブラウザで開く: `http://localhost:8000/demo`

## 📊 機能確認項目

### ✅ 確認すべき機能

- [ ] カメラアクセス（ブラウザ権限）
- [ ] 画像アップロード
- [ ] 姿勢分析結果表示
- [ ] PDFレポート生成
- [ ] レスポンシブデザイン

### 🔧 トラブルシューティング

#### カメラアクセスエラー
```
原因: HTTPSが必要（Chrome/Safari）
解決: ローカル開発時は http://localhost で問題なし
```

#### CORS エラー
```
原因: オリジン設定ミス
解決: backend/app/main.py のCORS設定確認
```

#### API接続エラー
```
原因: バックエンドサーバー未起動
解決: ./start_server.sh でサーバー起動
```

## 🎯 次のステップ

1. **ローカル環境確認**: Flutter Web または HTMLデモ
2. **実画像テスト**: 実際の人物画像で姿勢分析
3. **クラウドデプロイ**: Vercel/Netlify (フロント) + Railway/Render (バック)

## 📞 サポート

問題が発生した場合：
1. `./start_server.sh` でバックエンド確認
2. `http://localhost:8000/docs` でAPI動作確認
3. ブラウザ開発者ツールでエラーログ確認