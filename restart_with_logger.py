#!/usr/bin/env python3
"""
Docker restart script with comprehensive logging
"""

import subprocess
import sys
import os
import time

def run_command(cmd, description):
    """Run a shell command and log the result"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd="/Users/kobayashiryuju/posture-analysis-app")
        if result.returncode == 0:
            print(f"✅ {description} 成功")
            if result.stdout.strip():
                print(f"📝 出力: {result.stdout.strip()}")
        else:
            print(f"❌ {description} 失敗")
            if result.stderr.strip():
                print(f"🚨 エラー: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} エラー: {e}")
        return False

def main():
    """メイン実行"""
    print("🚀 Logger統合版 Docker再起動開始")
    
    # Change to project directory
    os.chdir("/Users/kobayashiryuju/posture-analysis-app")
    
    # Stop existing containers
    print("\n📦 既存コンテナの停止...")
    run_command("docker-compose down", "Docker containers stop")
    
    # Remove old images
    print("\n🗑️ 古いイメージの削除...")
    run_command("docker-compose down --rmi all", "Old images removal")
    
    # Build new containers with logger
    print("\n🔨 Logger統合版コンテナビルド...")
    success = run_command("docker-compose build --no-cache", "Docker build with logger")
    
    if not success:
        print("❌ ビルド失敗 - 手動確認が必要です")
        sys.exit(1)
    
    # Start containers
    print("\n🚀 新しいコンテナの起動...")
    success = run_command("docker-compose up -d", "Docker containers start")
    
    if not success:
        print("❌ 起動失敗 - 手動確認が必要です")
        sys.exit(1)
    
    # Wait for services to start
    print("\n⏳ サービス起動待機...")
    time.sleep(10)
    
    # Check container status
    print("\n📊 コンテナ状態確認...")
    run_command("docker-compose ps", "Container status check")
    
    # Test logger functionality
    print("\n🧪 Logger機能テスト...")
    run_command("docker-compose exec backend python test_logger.py", "Logger functionality test")
    
    # Check logs
    print("\n📋 起動ログ確認...")
    run_command("docker-compose logs --tail=20 backend", "Startup logs check")
    
    print("\n✅ Docker再起動完了!")
    print("📱 アクセス:")
    print("   - API: http://127.0.0.1:8000")
    print("   - Fixed Demo: http://127.0.0.1:8000/fixed")
    print("   - Test Demo: http://127.0.0.1:8000/test")
    print("   - Health Check: http://127.0.0.1:8000/health")
    print("\n📂 ログファイル:")
    print("   - Application logs: logs/")
    print("   - Docker logs: docker-compose logs backend")

if __name__ == "__main__":
    main()