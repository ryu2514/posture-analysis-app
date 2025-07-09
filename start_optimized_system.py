#!/usr/bin/env python3
"""
最適化済みシステム起動スクリプト
"""

import subprocess
import sys
import os
import time
import json

def main():
    """最適化済みシステムの起動"""
    print("🚀 最適化済み姿勢分析システム起動")
    print("=" * 60)
    
    project_dir = "/Users/kobayashiryuju/posture-analysis-app"
    os.chdir(project_dir)
    
    # Step 1: システム状態確認
    print("\n📋 Step 1: システム状態確認")
    system_check = check_system_status()
    
    if not system_check['ready']:
        print("⚠️ システム準備が不完全です")
        fix_system_issues(system_check)
    
    # Step 2: Docker環境確認・起動
    print("\n🐳 Step 2: Docker環境起動")
    docker_result = start_docker_environment()
    
    # Step 3: サービス確認
    print("\n🔍 Step 3: サービス確認")
    service_check = verify_services()
    
    # Step 4: アクセス情報表示
    print("\n🌐 Step 4: アクセス情報")
    display_access_info()
    
    # Step 5: 最終ステータス
    print("\n📊 Step 5: 最終ステータス")
    final_status = {
        'system_ready': system_check['ready'],
        'docker_running': docker_result,
        'services_available': service_check,
        'timestamp': time.time()
    }
    
    # ステータス保存
    status_file = os.path.join(project_dir, "system_status.json")
    with open(status_file, 'w') as f:
        json.dump(final_status, f, indent=2, default=str)
    
    if all([system_check['ready'], docker_result, service_check]):
        print("✅ システム起動完了 - 全機能利用可能!")
        return True
    else:
        print("⚠️ 一部機能に問題があります")
        return False

def check_system_status():
    """システム状態確認"""
    print("   🔍 必要ファイル・ディレクトリ確認...")
    
    project_dir = "/Users/kobayashiryuju/posture-analysis-app"
    
    # 必須ファイル確認
    required_files = [
        "backend/app/main.py",
        "backend/app/utils/logger.py", 
        "backend/app/utils/performance_monitor.py",
        "backend/app/utils/mediapipe_optimizer.py",
        "enhanced_demo.html",
        "requirements.txt",
        "Dockerfile"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(project_dir, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
    
    # 必要ディレクトリ確認・作成
    required_dirs = ["logs", "uploads", "reports"]
    for dir_name in required_dirs:
        dir_path = os.path.join(project_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)
    
    ready = len(missing_files) == 0
    
    if ready:
        print("   ✅ システム状態良好")
    else:
        print(f"   ⚠️ 不足ファイル: {missing_files}")
    
    return {
        'ready': ready,
        'missing_files': missing_files,
        'directories_created': required_dirs
    }

def fix_system_issues(system_check):
    """システム問題の修正"""
    print("   🔧 システム問題の修正中...")
    
    # requirements.txtが不足している場合
    if "requirements.txt" in system_check['missing_files']:
        create_requirements_file()
    
    # docker-compose.ymlが不足している場合  
    if not os.path.exists("docker-compose.yml"):
        create_docker_compose_file()
    
    print("   ✅ 修正完了")

def create_requirements_file():
    """requirements.txt作成"""
    requirements_content = """fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
mediapipe==0.10.8
opencv-python-headless==4.8.1.78
opencv-contrib-python==4.11.0.86
numpy==1.24.3
pillow==10.1.0
reportlab==4.0.7
requests==2.31.0
psutil==5.9.6
matplotlib==3.9.4
sounddevice==0.5.2"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements_content)
    print("   📝 requirements.txt作成完了")

def create_docker_compose_file():
    """docker-compose.yml作成"""
    compose_content = """version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
      - ./reports:/app/reports
      - ./logs:/app/logs
    environment:
      - PYTHONPATH=/app
      - UVICORN_HOST=0.0.0.0
      - UVICORN_PORT=8000
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
"""
    
    with open("docker-compose.yml", "w") as f:
        f.write(compose_content)
    print("   📝 docker-compose.yml作成完了")

def start_docker_environment():
    """Docker環境起動"""
    try:
        print("   🔄 Docker Composeでサービス起動中...")
        
        # 既存コンテナ停止
        subprocess.run(["docker-compose", "down"], 
                      capture_output=True, timeout=30)
        
        # 新しいコンテナ起動
        result = subprocess.run(["docker-compose", "up", "-d", "--build"], 
                               capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("   ✅ Docker環境起動成功")
            
            # 起動待機
            print("   ⏳ サービス起動待機中...")
            time.sleep(15)
            
            return True
        else:
            print(f"   ❌ Docker起動失敗: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⏰ Docker起動タイムアウト")
        return False
    except Exception as e:
        print(f"   ❌ Docker起動エラー: {e}")
        return False

def verify_services():
    """サービス確認"""
    try:
        import requests
        
        # ヘルスチェック
        print("   🏥 ヘルスチェック実行中...")
        
        max_retries = 5
        for i in range(max_retries):
            try:
                response = requests.get("http://127.0.0.1:8000/health", timeout=5)
                if response.status_code == 200:
                    print("   ✅ APIサービス正常動作")
                    return True
            except requests.exceptions.RequestException:
                if i < max_retries - 1:
                    print(f"   ⏳ 再試行 {i+1}/{max_retries}...")
                    time.sleep(5)
                else:
                    print("   ❌ APIサービス応答なし")
                    return False
        
        return False
        
    except ImportError:
        print("   ⚠️ requestsライブラリがインストールされていません")
        return False

def display_access_info():
    """アクセス情報表示"""
    print("\n🔗 システムアクセス情報:")
    print("   📡 API サーバー: http://127.0.0.1:8000")
    print("   🏥 ヘルスチェック: http://127.0.0.1:8000/health")
    print("   🎨 Enhanced Demo: http://127.0.0.1:8000/enhanced")
    print("   🧪 テストページ: http://127.0.0.1:8000/test")
    print("   📊 パフォーマンス監視: http://127.0.0.1:8000/api/performance/summary")
    print("   📋 API ドキュメント: http://127.0.0.1:8000/docs")
    
    print("\n📁 ログ・データファイル:")
    print("   📝 アプリケーションログ: logs/")
    print("   📊 パフォーマンスデータ: performance_export.json")
    print("   🔧 最適化設定: optimized_config.json")
    print("   📈 分析レポート: analysis_report.json")
    
    print("\n🐳 Docker 管理コマンド:")
    print("   停止: docker-compose down")
    print("   再起動: docker-compose restart")
    print("   ログ確認: docker-compose logs backend")
    print("   状態確認: docker-compose ps")

if __name__ == "__main__":
    success = main()
    print(f"\n{'🎉 システム起動成功!' if success else '⚠️ 問題があります'}")
    sys.exit(0 if success else 1)