#!/usr/bin/env python3
"""
包括的最適化実行スクリプト
Logger統合、詳細ログ収集、MediaPipe最適化を一括実行
"""

import sys
import os
import time
import json
from pathlib import Path

# プロジェクトパスを追加
sys.path.insert(0, '/Users/kobayashiryuju/posture-analysis-app')

def main():
    """メイン最適化プロセス"""
    print("🚀 包括的MediaPipe最適化プロセス開始")
    print("=" * 60)
    
    success_count = 0
    total_steps = 5
    
    # Step 1: Logger統合確認
    print(f"\n📋 Step 1/{total_steps}: Logger統合確認...")
    if verify_logger_integration():
        print("✅ Logger統合確認完了")
        success_count += 1
    else:
        print("❌ Logger統合確認失敗")
    
    # Step 2: 詳細ログ収集
    print(f"\n📊 Step 2/{total_steps}: 詳細ログ収集...")
    if collect_detailed_logs():
        print("✅ 詳細ログ収集完了")
        success_count += 1
    else:
        print("❌ 詳細ログ収集失敗")
    
    # Step 3: MediaPipe設定最適化
    print(f"\n🔧 Step 3/{total_steps}: MediaPipe設定最適化...")
    if optimize_mediapipe_config():
        print("✅ MediaPipe設定最適化完了")
        success_count += 1
    else:
        print("❌ MediaPipe設定最適化失敗")
    
    # Step 4: 前処理パイプライン改善
    print(f"\n🖼️ Step 4/{total_steps}: 前処理パイプライン改善...")
    if improve_preprocessing_pipeline():
        print("✅ 前処理パイプライン改善完了")
        success_count += 1
    else:
        print("❌ 前処理パイプライン改善失敗")
    
    # Step 5: 統合テスト実行
    print(f"\n🧪 Step 5/{total_steps}: 統合テスト実行...")
    if run_integration_tests():
        print("✅ 統合テスト完了")
        success_count += 1
    else:
        print("❌ 統合テスト失敗")
    
    # 最終結果
    print("\n" + "=" * 60)
    print(f"📊 最適化結果: {success_count}/{total_steps} ステップ成功")
    
    if success_count == total_steps:
        print("🎉 包括的最適化完了 - 全ステップ成功!")
        generate_success_report()
    elif success_count >= 3:
        print("✅ 最適化部分的成功 - 主要機能は動作")
        generate_partial_success_report(success_count, total_steps)
    else:
        print("⚠️ 最適化問題あり - 手動確認が必要")
        generate_failure_report(success_count, total_steps)
    
    return success_count >= 3

def verify_logger_integration():
    """Logger統合確認"""
    try:
        # Logger import test
        from backend.app.utils.logger import get_logger, log_function_call
        logger = get_logger("integration_test")
        
        # 基本ログテスト
        logger.info("Logger統合テスト実行")
        
        # システム情報ログ
        logger.log_system_info()
        
        # パフォーマンステスト
        timer_id = logger.start_timer("integration_test")
        time.sleep(0.1)
        logger.end_timer(timer_id)
        
        return True
        
    except Exception as e:
        print(f"Logger統合エラー: {e}")
        return False

def collect_detailed_logs():
    """詳細ログ収集"""
    try:
        from backend.app.utils.logger import get_logger
        from backend.app.services.pose_analyzer import PoseAnalyzer
        
        logger = get_logger("log_collection")
        analyzer = PoseAnalyzer()
        
        # サンプル画像でのテスト
        sample_data = create_test_image_data()
        
        # 分析実行（非同期実行のシミュレーション）
        logger.info("詳細ログ収集テスト開始")
        
        # MediaPipeテスト用の画像分析
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(analyzer.analyze_image(sample_data))
            success = result is not None
        except Exception as e:
            logger.error("画像分析テストエラー", error=e)
            success = False
        finally:
            loop.close()
        
        # 分析結果のログ記録
        analysis_result = {
            "test_timestamp": time.time(),
            "analysis_success": success,
            "sample_image_size": len(sample_data)
        }
        
        # 分析レポート保存
        report_path = "/Users/kobayashiryuju/posture-analysis-app/test_analysis_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2)
        
        logger.info("詳細ログ収集完了", report_path=report_path)
        return True
        
    except Exception as e:
        print(f"詳細ログ収集エラー: {e}")
        return False

def optimize_mediapipe_config():
    """MediaPipe設定最適化"""
    try:
        from backend.app.utils.config_optimizer import ConfigOptimizer
        
        optimizer = ConfigOptimizer()
        
        # 最適化実行
        analysis_file = "/Users/kobayashiryuju/posture-analysis-app/test_analysis_report.json"
        result = optimizer.analyze_logs_and_optimize(analysis_file)
        
        # 最適化設定適用
        applied = optimizer.apply_optimized_config(result)
        
        if applied:
            print(f"   推奨設定: {result.recommended_config.name}")
            print(f"   信頼度: {result.confidence_score:.1%}")
            print(f"   理由: {', '.join(result.reasoning)}")
        
        return applied
        
    except Exception as e:
        print(f"MediaPipe最適化エラー: {e}")
        return False

def improve_preprocessing_pipeline():
    """前処理パイプライン改善"""
    try:
        from backend.app.utils.mediapipe_optimizer import ImagePreprocessor
        
        preprocessor = ImagePreprocessor()
        
        # 前処理戦略テスト
        strategies = preprocessor.get_preprocessing_strategies()
        
        # テスト画像での前処理確認
        test_image = create_test_opencv_image()
        
        successful_strategies = 0
        for strategy in strategies:
            try:
                processed = preprocessor.preprocess_image(test_image, strategy)
                if processed is not None:
                    successful_strategies += 1
            except Exception as e:
                print(f"   前処理戦略 {strategy} エラー: {e}")
        
        print(f"   成功した前処理戦略: {successful_strategies}/{len(strategies)}")
        return successful_strategies >= len(strategies) // 2
        
    except Exception as e:
        print(f"前処理パイプライン改善エラー: {e}")
        return False

def run_integration_tests():
    """統合テスト実行"""
    try:
        from backend.app.services.pose_analyzer import PoseAnalyzer
        from backend.app.utils.logger import get_logger
        
        logger = get_logger("integration_test")
        analyzer = PoseAnalyzer()
        
        # 複数の画像でテスト
        test_results = []
        
        for i in range(3):
            test_data = create_test_image_data()
            
            # 分析実行
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(analyzer.analyze_image(test_data))
                test_results.append(result is not None)
            except Exception as e:
                logger.error(f"統合テスト{i+1}失敗", error=e)
                test_results.append(False)
            finally:
                loop.close()
        
        success_rate = sum(test_results) / len(test_results)
        print(f"   統合テスト成功率: {success_rate:.1%}")
        
        return success_rate >= 0.5  # 50%以上成功で合格
        
    except Exception as e:
        print(f"統合テストエラー: {e}")
        return False

def create_test_image_data():
    """テスト用画像データ作成"""
    import cv2
    import numpy as np
    
    # 640x480の白背景画像作成
    image = np.ones((480, 640, 3), dtype=np.uint8) * 255
    
    # 簡単な人体形状描画
    # 頭
    cv2.circle(image, (320, 100), 40, (0, 0, 0), -1)
    # 胴体
    cv2.rectangle(image, (280, 140), (360, 320), (0, 0, 0), -1)
    # 腕
    cv2.rectangle(image, (230, 160), (280, 180), (0, 0, 0), -1)
    cv2.rectangle(image, (360, 160), (410, 180), (0, 0, 0), -1)
    # 脚
    cv2.rectangle(image, (295, 320), (315, 420), (0, 0, 0), -1)
    cv2.rectangle(image, (325, 320), (345, 420), (0, 0, 0), -1)
    
    # エンコード
    _, encoded = cv2.imencode('.jpg', image)
    return encoded.tobytes()

def create_test_opencv_image():
    """OpenCV用テスト画像作成"""
    import cv2
    import numpy as np
    
    image = np.ones((480, 640, 3), dtype=np.uint8) * 128
    cv2.circle(image, (320, 240), 100, (255, 255, 255), -1)
    
    return image

def generate_success_report():
    """成功レポート生成"""
    report = {
        "optimization_status": "完全成功",
        "timestamp": time.time(),
        "next_steps": [
            "Dockerコンテナ再起動でテスト",
            "実際の画像での動作確認",
            "パフォーマンス監視開始"
        ]
    }
    
    with open("/Users/kobayashiryuju/posture-analysis-app/optimization_success_report.json", 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print("\n📄 成功レポートが生成されました")

def generate_partial_success_report(success_count, total_steps):
    """部分成功レポート生成"""
    report = {
        "optimization_status": "部分成功",
        "success_count": success_count,
        "total_steps": total_steps,
        "timestamp": time.time(),
        "recommendations": [
            "成功した機能のみでテスト開始",
            "失敗した機能の個別デバッグ",
            "段階的な機能展開"
        ]
    }
    
    with open("/Users/kobayashiryuju/posture-analysis-app/optimization_partial_report.json", 'w') as f:
        json.dump(report, f, indent=2, default=str)

def generate_failure_report(success_count, total_steps):
    """失敗レポート生成"""
    report = {
        "optimization_status": "要調査",
        "success_count": success_count,
        "total_steps": total_steps,
        "timestamp": time.time(),
        "action_required": [
            "ログファイルの詳細確認",
            "依存関係の確認",
            "手動設定の見直し"
        ]
    }
    
    with open("/Users/kobayashiryuju/posture-analysis-app/optimization_failure_report.json", 'w') as f:
        json.dump(report, f, indent=2, default=str)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)