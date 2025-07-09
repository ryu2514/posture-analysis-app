#!/usr/bin/env python3
"""
Logger統合検証スクリプト
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def verify_logger_integration():
    """Logger統合を検証"""
    print("🔍 Logger統合検証開始")
    
    try:
        # Import test
        print("1. モジュールインポートテスト...")
        from backend.app.utils.logger import get_logger, log_function_call
        from backend.app.utils.mediapipe_optimizer import ComprehensiveDetector
        from backend.app.services.pose_analyzer import PoseAnalyzer
        print("✅ 全モジュールインポート成功")
        
        # Logger initialization test
        print("2. Logger初期化テスト...")
        logger = get_logger("test_verification")
        logger.info("Logger初期化確認", test="success")
        print("✅ Logger初期化成功")
        
        # Comprehensive detector test
        print("3. ComprehensiveDetector初期化テスト...")
        detector = ComprehensiveDetector()
        print("✅ ComprehensiveDetector初期化成功")
        
        # PoseAnalyzer test
        print("4. PoseAnalyzer初期化テスト...")
        analyzer = PoseAnalyzer()
        print("✅ PoseAnalyzer初期化成功")
        
        # System info logging test
        print("5. システム情報ログテスト...")
        logger.log_system_info()
        print("✅ システム情報ログ成功")
        
        print("\n🎉 Logger統合検証完了 - 全テスト成功!")
        print("📁 ログファイルは logs/ ディレクトリに保存されています")
        return True
        
    except Exception as e:
        print(f"❌ 検証失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_logger_integration()
    sys.exit(0 if success else 1)