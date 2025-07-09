#!/usr/bin/env python3
"""
手動テストスクリプト - Logger機能とMediaPipe最適化のテスト
"""

import sys
import os
import traceback

# プロジェクトパスを追加
sys.path.insert(0, '/Users/kobayashiryuju/posture-analysis-app')

def main():
    """メイン実行関数"""
    print("🚀 Logger & MediaPipe最適化 手動テスト開始")
    
    try:
        # Step 1: Logger import test
        print("\n1️⃣ Loggerインポートテスト...")
        from backend.app.utils.logger import get_logger, log_function_call
        logger = get_logger("manual_test")
        logger.info("Logger正常動作確認", test_phase="import")
        print("✅ Loggerインポート成功")
        
        # Step 2: MediaPipe optimizer import test
        print("\n2️⃣ MediaPipe最適化インポートテスト...")
        from backend.app.utils.mediapipe_optimizer import ComprehensiveDetector, MediaPipeOptimizer
        optimizer = MediaPipeOptimizer()
        detector = ComprehensiveDetector()
        logger.info("MediaPipe最適化モジュール初期化完了")
        print("✅ MediaPipe最適化インポート成功")
        
        # Step 3: PoseAnalyzer with new integrations
        print("\n3️⃣ 統合PoseAnalyzerテスト...")
        from backend.app.services.pose_analyzer import PoseAnalyzer
        analyzer = PoseAnalyzer()
        logger.info("統合PoseAnalyzer初期化完了")
        print("✅ 統合PoseAnalyzer成功")
        
        # Step 4: Log system info
        print("\n4️⃣ システム情報ログテスト...")
        logger.log_system_info()
        print("✅ システム情報ログ成功")
        
        # Step 5: Performance monitoring test
        print("\n5️⃣ パフォーマンス監視テスト...")
        timer_id = logger.start_timer("test_operation")
        import time
        time.sleep(0.1)  # Simulate some work
        duration = logger.end_timer(timer_id)
        logger.info("パフォーマンステスト完了", duration=duration)
        print(f"✅ パフォーマンス監視成功 ({duration:.3f}秒)")
        
        # Step 6: Error handling test
        print("\n6️⃣ エラーハンドリングテスト...")
        try:
            raise ValueError("テストエラー")
        except Exception as e:
            logger.error("期待されたテストエラー", error=e)
            print("✅ エラーハンドリング成功")
        
        print("\n🎉 全テスト成功!")
        print("📁 ログファイルは backend/app/logs/ に保存されています")
        
        # Check if logs directory was created
        logs_dir = "/Users/kobayashiryuju/posture-analysis-app/backend/app/logs"
        if os.path.exists(logs_dir):
            print(f"📂 ログディレクトリ確認: {logs_dir}")
            log_files = os.listdir(logs_dir)
            if log_files:
                print(f"📄 作成されたログファイル: {log_files}")
            else:
                print("⚠️ ログファイルが見つかりません")
        else:
            print("⚠️ ログディレクトリが見つかりません")
        
        return True
        
    except Exception as e:
        print(f"\n❌ テスト失敗: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n{'✅ テスト成功' if success else '❌ テスト失敗'}")
    sys.exit(0 if success else 1)