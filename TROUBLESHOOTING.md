# 🔧 ローカルサーバー接続トラブルシューティング

## 🚀 サーバー起動確認

### 1. サーバーが起動しているか確認

```bash
# プロセス確認
ps aux | grep uvicorn

# ポート使用状況確認
lsof -i :8000
# または
netstat -an | grep 8000
```

### 2. 手動サーバー起動

```bash
cd /Users/kobayashiryuju/posture-analysis-app
export PYTHONPATH=$(pwd):$PYTHONPATH
python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. ブラウザアクセス

**正しいURL:**
- ✅ http://127.0.0.1:8000/demo
- ✅ http://localhost:8000/demo
- ❌ https://127.0.0.1:8000/demo (HTTPSは不要)
- ❌ http://127.0.0.1:8000 (デモページではない)

## 🔍 接続問題の診断

### A. ファイアウォール確認

```bash
# macOS ファイアウォール確認
sudo pfctl -sr | grep 8000

# 一時的に無効化（注意：セキュリティリスク）
sudo pfctl -d
```

### B. ブラウザキャッシュクリア

1. **Chrome/Safari**: Cmd+Shift+R (強制リロード)
2. **Firefox**: Cmd+Shift+Delete (履歴削除)
3. **プライベートモード**で試す

### C. 別ポートで試す

```bash
# ポート8080で起動
python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8080 --reload

# アクセス: http://127.0.0.1:8080/demo
```

### D. 詳細ログ確認

```bash
# デバッグモードで起動
python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload --log-level debug
```

## 🚨 よくあるエラーと解決法

### エラー1: "Address already in use"
```bash
# ポート8000を使用しているプロセスを終了
lsof -ti:8000 | xargs kill -9
```

### エラー2: "Module not found"
```bash
# Python パス設定
cd /Users/kobayashiryuju/posture-analysis-app
export PYTHONPATH=$(pwd):$PYTHONPATH
```

### エラー3: "Permission denied"
```bash
# 権限修正
chmod +x start_server.sh
```

### エラー4: ブラウザに "接続できません"
1. サーバーが実際に起動しているか確認
2. URLが正しいか確認 (http://127.0.0.1:8000/demo)
3. 別のブラウザで試す
4. プライベートモードで試す

## 📱 クイック接続テスト

### ターミナルテスト
```bash
# API接続テスト
curl http://127.0.0.1:8000/health

# 期待される応答:
# {"status":"healthy","mediapipe":"ready"}
```

### ブラウザテスト手順
1. サーバー起動: `./start_server.sh`
2. ターミナルに "Uvicorn running on http://127.0.0.1:8000" 表示確認
3. ブラウザで http://127.0.0.1:8000/demo 開く
4. "姿勢分析デモ" ページが表示されることを確認

## 🆘 それでも繋がらない場合

### 代替アクセス方法

1. **API仕様書**: http://127.0.0.1:8000/docs
2. **ヘルスチェック**: http://127.0.0.1:8000/health
3. **JSON API**: http://127.0.0.1:8000/

### 環境固有の設定

```bash
# macOS Big Sur以降でセキュリティ設定確認
spctl --assess --verbose /usr/local/bin/python3

# Homebrewの場合
which python3
/opt/homebrew/bin/python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

## 💡 推奨解決策

**最も確実な方法:**

1. 新しいターミナルウィンドウを開く
2. 以下を順番に実行:

```bash
cd /Users/kobayashiryuju/posture-analysis-app
export PYTHONPATH=$(pwd):$PYTHONPATH
python3 -c "
from backend.app.main import app
from fastapi.testclient import TestClient
client = TestClient(app)
print('API Test:', client.get('/health').json())
"
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

3. ブラウザで http://localhost:8000/demo を開く

これで接続できない場合は、具体的なエラーメッセージをお知らせください。