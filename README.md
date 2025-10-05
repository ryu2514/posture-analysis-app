# 姿勢分析アプリ (Shisei Navi)

AIを活用した姿勢評価システム - 理学療法士向けの専門ツール

## 特徴

- 📸 写真アップロードによる姿勢分析
- 🎯 頭部前方位（CVA）の定量評価
- ⚖️ 肩の高さ左右差の測定
- 📊 脊柱アライメントの簡易評価
- 📱 レスポンシブデザイン（モバイル/PC対応）

## 技術スタック

- **フレームワーク**: Next.js 14 (App Router)
- **言語**: TypeScript
- **スタイリング**: Tailwind CSS
- **フォーム管理**: React Hook Form
- **画像処理**: React Dropzone
- **姿勢推定**: MediaPipe Pose (ブラウザ内リアルタイム)
- **AI API (オプション)**: OpenAI Vision API
- **テスト**: Jest + React Testing Library

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd shisei-navi
```

### 2. 依存関係のインストール

```bash
npm install
```

### 3. 環境変数の設定

```bash
cp .env.example .env.local
```

`.env.local`ファイルを編集して、解析バックエンドを設定してください（デフォルトは MediaPipe でサーバー鍵不要）：

```env
ANALYSIS_BACKEND=mediapipe
```

### 4. 開発サーバーの起動

```bash
npm run dev
```

ブラウザで [http://localhost:3000](http://localhost:3000) にアクセスしてください。

## 利用可能なコマンド

```bash
npm run dev          # 開発サーバー起動
npm run build        # プロダクションビルド
npm run start        # プロダクションサーバー起動
npm run lint         # ESLintチェック
npm run type-check   # TypeScriptタイプチェック
npm run test         # テスト実行
npm run test:watch   # テスト監視モード
npm run test:coverage # カバレッジ付きテスト
```

## API設定（任意）

サーバー側でOpenAIを使った解析を有効化したい場合のみ設定します。

### OpenAI Vision API を使う場合（任意）

1. [OpenAI Platform](https://platform.openai.com)でAPIキーを生成
2. `.env.local`に以下を設定
   - `ANALYSIS_BACKEND=openai`
   - `OPENAI_API_KEY=sk-...`

### Google Cloud Vision API（代替・サンプル、未使用）
`.env.local` の `GOOGLE_CLOUD_VISION_API_KEY` を設定可能ですが、既定の実装は MediaPipe ベースです。

## デプロイ

### Vercel（推奨）

```bash
npm install -g vercel
vercel
```

MediaPipe利用のみの場合はサーバー側の機密鍵は不要です（`ANALYSIS_BACKEND=mediapipe`）。OpenAIを使う場合のみ `OPENAI_API_KEY` を本番環境に設定してください。

### 本番は MediaPipe のみで運用する場合

- 環境変数（VercelのProject Settings → Environment Variables）
  - `ANALYSIS_BACKEND=mediapipe`（Production/Preview/Development 全てに設定）
  - `OPENAI_API_KEY` などサーバー鍵は未設定でOK（不要）
- ビルド/実行
  - Build Command: `npm run build`（自動検出）
  - Output: `.next`（自動検出）
  - Node: 18+（推奨、VercelデフォルトでOK）
- ネットワーク要件
  - MediaPipeのモデルは `cdn.jsdelivr.net` から取得（外部CDNアクセス許可が必要）
- セキュリティ/ブラウザ要件
  - カメラを使用する機能はHTTPS環境が必須（本番Vercelは既定でHTTPS）
- サーバーAPIについて
  - `app/api/analyze` は OpenAI バックエンド時のみ利用されます。
  - `ANALYSIS_BACKEND=mediapipe` の場合はこのAPIはエラーレスポンス（無効）を返します（クライアント側でMediaPipe解析を使用）。

デプロイ後チェックリスト（MediaPipe版）

- [ ] トップ画面から「MediaPipe 解析」を開き、カメラアクセスが許可されること
- [ ] ランドマーク描画とフィードバックが表示されること
- [ ] 画像アップロードベースの静的解析が動作すること（必要に応じて）
- [ ] OpenAI 関連のUI/エンドポイントにアクセスしてもサーバー鍵不要で安全に動作（または無効）であること

## セキュリティ設定

- 画像ファイルサイズ上限: 10MB
- 対応ファイル形式: JPG, PNG
- HTTPS必須
- 処理後の画像は即座に削除

## ライセンス

ISC License
