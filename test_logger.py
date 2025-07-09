#!/usr/bin/env python3
"""
Logger テストスクリプト
強力なLoggerクラスの動作確認用
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from backend.app.utils.logger import get_logger, log_function_call

# ロガー取得
logger = get_logger("test_logger")

@log_function_call
def test_function(param1: str, param2: int):
    """テスト関数"""
    logger.info("テスト関数実行中", param1=param1, param2=param2)
    
    # タイマーテスト
    timer_id = logger.start_timer("calculation")
    
    # 何かの処理をシミュレート
    import time
    time.sleep(0.1)
    
    logger.end_timer(timer_id, {"result": "success"})
    
    return f"Processed {param1} with {param2}"

@log_function_call 
def test_error_function():
    """エラーテスト関数"""
    try:
        raise ValueError("これはテストエラーです")
    except Exception as e:
        logger.error("テストエラーが発生", error=e)
        raise

def main():
    """メインテスト関数"""
    print("🧪 Logger テスト開始")
    
    # システム情報ログ
    logger.log_system_info()
    
    # 各レベルのログテスト
    logger.debug("デバッグメッセージ", test_data="debug_value")
    logger.info("情報メッセージ", test_data="info_value")
    logger.warning("警告メッセージ", test_data="warning_value")
    
    # MediaPipe専用ログテスト
    logger.log_image_processing("test.jpg", 1024*1024, "JPEG")
    logger.log_pose_detection_start((640, 480), 2)
    logger.log_pose_detection_result(True, 33, 0.95)
    
    # メトリクス計算ログテスト
    mock_metrics = {
        "pelvic_tilt": 8.5,
        "thoracic_kyphosis": 35.2,
        "cervical_lordosis": 25.1
    }
    logger.log_metrics_calculation("sagittal", mock_metrics)
    
    # API呼び出しログテスト
    logger.log_api_request("/analyze-posture", "POST", "127.0.0.1", 1024*1024)
    logger.log_api_response("/analyze-posture", 200, 2.5)
    
    # 関数呼び出しテスト
    result = test_function("test_param", 42)
    logger.info("関数呼び出し結果", result=result)
    
    # エラーハンドリングテスト
    try:
        test_error_function()
    except ValueError:
        logger.info("エラーハンドリング正常動作")
    
    # パフォーマンステスト
    timer_id = logger.start_timer("main_test")
    time.sleep(0.2)
    duration = logger.end_timer(timer_id)
    
    logger.info("✅ Loggerテスト完了", total_duration=duration)
    print(f"✅ Loggerテスト完了 - ログは logs/ ディレクトリに保存されました")
    print(f"📊 処理時間: {duration:.3f}秒")

if __name__ == "__main__":
    main()