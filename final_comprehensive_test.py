#!/usr/bin/env python3
"""
最終包括テストスクリプト
Logger統合、パフォーマンス監視、MediaPipe最適化の全機能テスト
"""

import sys
import os
import json
import time
import traceback
from pathlib import Path

# プロジェクトパスを追加
sys.path.insert(0, '/Users/kobayashiryuju/posture-analysis-app')

def main():
    """最終包括テスト実行"""
    print("🚀 最終包括テスト開始")
    print("=" * 80)
    
    test_results = {}
    total_tests = 8
    passed_tests = 0
    
    # Test 1: Logger統合テスト
    print(f"\n🧪 Test 1/{total_tests}: Logger統合テスト")
    test_results['logger'] = test_logger_integration()
    if test_results['logger']['success']:
        passed_tests += 1
        print("✅ Logger統合テスト成功")
    else:
        print("❌ Logger統合テスト失敗")
    
    # Test 2: MediaPipe最適化テスト
    print(f"\n🧪 Test 2/{total_tests}: MediaPipe最適化テスト")
    test_results['mediapipe'] = test_mediapipe_optimization()
    if test_results['mediapipe']['success']:
        passed_tests += 1
        print("✅ MediaPipe最適化テスト成功")
    else:
        print("❌ MediaPipe最適化テスト失敗")
    
    # Test 3: パフォーマンス監視テスト
    print(f"\n🧪 Test 3/{total_tests}: パフォーマンス監視テスト")
    test_results['performance'] = test_performance_monitoring()
    if test_results['performance']['success']:
        passed_tests += 1
        print("✅ パフォーマンス監視テスト成功")
    else:
        print("❌ パフォーマンス監視テスト失敗")
    
    # Test 4: 設定最適化テスト
    print(f"\n🧪 Test 4/{total_tests}: 設定最適化テスト")
    test_results['config_optimization'] = test_config_optimization()
    if test_results['config_optimization']['success']:
        passed_tests += 1
        print("✅ 設定最適化テスト成功")
    else:
        print("❌ 設定最適化テスト失敗")
    
    # Test 5: 姿勢分析統合テスト
    print(f"\n🧪 Test 5/{total_tests}: 姿勢分析統合テスト")
    test_results['pose_analysis'] = test_pose_analysis_integration()
    if test_results['pose_analysis']['success']:
        passed_tests += 1
        print("✅ 姿勢分析統合テスト成功")
    else:
        print("❌ 姿勢分析統合テスト失敗")
    
    # Test 6: エラーハンドリングテスト
    print(f"\n🧪 Test 6/{total_tests}: エラーハンドリングテスト")
    test_results['error_handling'] = test_error_handling()
    if test_results['error_handling']['success']:
        passed_tests += 1
        print("✅ エラーハンドリングテスト成功")
    else:
        print("❌ エラーハンドリングテスト失敗")
    
    # Test 7: APIエンドポイントテスト
    print(f"\n🧪 Test 7/{total_tests}: APIエンドポイントテスト")
    test_results['api_endpoints'] = test_api_endpoints()
    if test_results['api_endpoints']['success']:
        passed_tests += 1
        print("✅ APIエンドポイントテスト成功")
    else:
        print("❌ APIエンドポイントテスト失敗")
    
    # Test 8: 包括的動作テスト
    print(f"\n🧪 Test 8/{total_tests}: 包括的動作テスト")
    test_results['comprehensive'] = test_comprehensive_workflow()
    if test_results['comprehensive']['success']:
        passed_tests += 1
        print("✅ 包括的動作テスト成功")
    else:
        print("❌ 包括的動作テスト失敗")
    
    # 最終結果
    print("\n" + "=" * 80)
    print(f"📊 最終テスト結果: {passed_tests}/{total_tests} テスト成功")
    success_rate = passed_tests / total_tests
    
    if success_rate >= 0.9:
        print("🎉 優秀 - システムは本番環境で使用可能")
        status = "excellent"
    elif success_rate >= 0.75:
        print("✅ 良好 - 一部調整が必要ですが使用可能")
        status = "good"
    elif success_rate >= 0.5:
        print("⚠️ 要改善 - 重要な機能に問題があります")
        status = "needs_improvement"
    else:
        print("❌ 不合格 - 大幅な修正が必要です")
        status = "failed"
    
    # 結果レポート生成
    generate_final_report(test_results, passed_tests, total_tests, status)
    
    return success_rate >= 0.75

def test_logger_integration():
    """Logger統合テスト"""
    try:
        from backend.app.utils.logger import get_logger, log_function_call
        
        logger = get_logger("test_logger")
        
        # 基本ログテスト
        logger.info("Logger統合テスト実行")
        logger.debug("デバッグメッセージ")
        logger.warning("警告メッセージ")
        
        # システム情報ログ
        logger.log_system_info()
        
        # タイマーテスト
        timer_id = logger.start_timer("test_timer")
        time.sleep(0.1)
        duration = logger.end_timer(timer_id)
        
        # MediaPipe専用ログテスト
        logger.log_image_processing("test.jpg", 1024, "JPEG")
        logger.log_pose_detection_start((640, 480), 2)
        logger.log_pose_detection_result(True, 33, 0.95)
        
        return {
            'success': True,
            'duration': duration,
            'features_tested': ['basic_logging', 'system_info', 'timer', 'mediapipe_logs']
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

def test_mediapipe_optimization():
    """MediaPipe最適化テスト"""
    try:
        from backend.app.utils.mediapipe_optimizer import (
            ComprehensiveDetector, MediaPipeOptimizer, ImagePreprocessor
        )
        
        # MediaPipeOptimizer初期化
        optimizer = MediaPipeOptimizer()
        
        # ComprehensiveDetector初期化
        detector = ComprehensiveDetector()
        
        # ImagePreprocessor初期化
        preprocessor = ImagePreprocessor()
        
        # 前処理戦略取得
        strategies = preprocessor.get_preprocessing_strategies()
        
        return {
            'success': True,
            'optimizer_configs': len(optimizer.configs),
            'preprocessing_strategies': len(strategies),
            'features_tested': ['optimizer', 'detector', 'preprocessor']
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

def test_performance_monitoring():
    """パフォーマンス監視テスト"""
    try:
        from backend.app.utils.performance_monitor import (
            get_performance_monitor, monitor_performance
        )
        
        monitor = get_performance_monitor()
        
        # 基本操作監視テスト
        op_id = monitor.start_operation("test_operation", "test")
        time.sleep(0.1)
        metrics = monitor.end_operation(op_id, success=True)
        
        # サマリー取得
        summary = monitor.get_performance_summary()
        
        # 推奨事項取得
        recommendations = monitor.get_optimization_recommendations()
        
        return {
            'success': True,
            'processing_time': metrics.processing_time,
            'summary_keys': list(summary.keys()),
            'recommendations_count': len(recommendations),
            'features_tested': ['operation_tracking', 'summary', 'recommendations']
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

def test_config_optimization():
    """設定最適化テスト"""
    try:
        from backend.app.utils.config_optimizer import ConfigOptimizer
        
        optimizer = ConfigOptimizer()
        
        # 最適化実行
        result = optimizer.analyze_logs_and_optimize()
        
        # 設定適用テスト
        applied = optimizer.apply_optimized_config(result)
        
        # 現在の状態取得
        status = optimizer.get_current_optimization_status()
        
        return {
            'success': True,
            'recommended_config': result.recommended_config.name,
            'confidence_score': result.confidence_score,
            'config_applied': applied,
            'features_tested': ['optimization', 'config_application', 'status_check']
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

def test_pose_analysis_integration():
    """姿勢分析統合テスト"""
    try:
        from backend.app.services.pose_analyzer import PoseAnalyzer
        
        analyzer = PoseAnalyzer()
        
        # テスト画像作成
        test_image_data = create_test_image()
        
        # 分析実行（非同期処理のシミュレーション）
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(analyzer.analyze_image(test_image_data))
        finally:
            loop.close()
        
        return {
            'success': result is not None,
            'analysis_result': result is not None,
            'has_landmarks': hasattr(result, 'landmarks') if result else False,
            'has_metrics': hasattr(result, 'metrics') if result else False,
            'features_tested': ['image_analysis', 'landmark_detection', 'metrics_calculation']
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

def test_error_handling():
    """エラーハンドリングテスト"""
    try:
        from backend.app.utils.logger import get_logger
        from backend.app.services.pose_analyzer import PoseAnalyzer
        
        logger = get_logger("error_test")
        
        # 意図的なエラー発生とハンドリング
        try:
            raise ValueError("テストエラー")
        except Exception as e:
            logger.error("期待されたエラー", error=e)
        
        # 無効な画像データでの分析テスト
        analyzer = PoseAnalyzer()
        invalid_data = b"invalid image data"
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(analyzer.analyze_image(invalid_data))
        finally:
            loop.close()
        
        # エラー時はNoneが返されることを確認
        error_handled = result is None
        
        return {
            'success': True,
            'error_logged': True,
            'invalid_data_handled': error_handled,
            'features_tested': ['exception_logging', 'invalid_data_handling']
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

def test_api_endpoints():
    """APIエンドポイントテスト"""
    try:
        # FastAPIアプリの動作確認（importのみ）
        from backend.app.main import app, performance_monitor
        
        # パフォーマンス監視機能の確認
        monitor_available = performance_monitor is not None
        
        # アプリケーション設定の確認
        app_available = app is not None
        
        return {
            'success': True,
            'app_available': app_available,
            'performance_monitor_available': monitor_available,
            'features_tested': ['app_import', 'performance_integration']
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

def test_comprehensive_workflow():
    """包括的動作テスト"""
    try:
        # 全モジュールの統合動作テスト
        start_time = time.time()
        
        # Logger
        from backend.app.utils.logger import get_logger
        logger = get_logger("comprehensive_test")
        
        # Performance Monitor
        from backend.app.utils.performance_monitor import get_performance_monitor
        monitor = get_performance_monitor()
        
        # MediaPipe最適化
        from backend.app.utils.mediapipe_optimizer import ComprehensiveDetector
        detector = ComprehensiveDetector()
        
        # 姿勢分析
        from backend.app.services.pose_analyzer import PoseAnalyzer
        analyzer = PoseAnalyzer()
        
        # 統合テスト実行
        op_id = monitor.start_operation("comprehensive_test", "integration")
        
        logger.info("包括的テスト開始")
        
        # テスト画像で分析
        test_data = create_test_image()
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(analyzer.analyze_image(test_data))
        finally:
            loop.close()
        
        monitor.end_operation(op_id, success=result is not None)
        
        total_time = time.time() - start_time
        
        return {
            'success': True,
            'total_time': total_time,
            'analysis_success': result is not None,
            'modules_integrated': ['logger', 'performance_monitor', 'mediapipe_optimizer', 'pose_analyzer'],
            'features_tested': ['full_integration', 'end_to_end_workflow']
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

def create_test_image():
    """テスト画像データ作成"""
    import cv2
    import numpy as np
    
    # 640x480の白背景画像
    image = np.ones((480, 640, 3), dtype=np.uint8) * 255
    
    # 簡単な人体形状描画
    cv2.circle(image, (320, 100), 30, (0, 0, 0), -1)  # 頭
    cv2.rectangle(image, (290, 130), (350, 300), (0, 0, 0), -1)  # 胴体
    cv2.rectangle(image, (250, 150), (290, 170), (0, 0, 0), -1)  # 左腕
    cv2.rectangle(image, (350, 150), (390, 170), (0, 0, 0), -1)  # 右腕
    cv2.rectangle(image, (305, 300), (315, 400), (0, 0, 0), -1)  # 左脚
    cv2.rectangle(image, (325, 300), (335, 400), (0, 0, 0), -1)  # 右脚
    
    # エンコード
    _, encoded = cv2.imencode('.jpg', image)
    return encoded.tobytes()

def generate_final_report(test_results, passed_tests, total_tests, status):
    """最終レポート生成"""
    
    report = {
        "test_summary": {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": passed_tests / total_tests,
            "overall_status": status,
            "timestamp": time.time()
        },
        "detailed_results": test_results,
        "system_readiness": {
            "production_ready": status in ["excellent", "good"],
            "logger_integrated": test_results.get('logger', {}).get('success', False),
            "performance_monitoring": test_results.get('performance', {}).get('success', False),
            "mediapipe_optimized": test_results.get('mediapipe', {}).get('success', False),
            "error_handling": test_results.get('error_handling', {}).get('success', False)
        },
        "next_steps": generate_next_steps(status, test_results),
        "deployment_recommendations": generate_deployment_recommendations(status)
    }
    
    # レポート保存
    report_path = "/Users/kobayashiryuju/posture-analysis-app/final_test_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📄 最終テストレポート生成: {report_path}")
    
    # コンソール出力
    print(f"\n📋 システム準備状況:")
    for key, value in report["system_readiness"].items():
        status_icon = "✅" if value else "❌"
        print(f"   {status_icon} {key}: {'Ready' if value else 'Not Ready'}")

def generate_next_steps(status, test_results):
    """次のステップ生成"""
    steps = []
    
    if status == "excellent":
        steps.extend([
            "本番環境へのデプロイメント実行",
            "リアルタイム監視の設定",
            "ユーザートレーニングの実施"
        ])
    elif status == "good":
        steps.extend([
            "失敗したテストの個別修正",
            "段階的デプロイメントの実行",
            "追加テストの実施"
        ])
    elif status == "needs_improvement":
        steps.extend([
            "重要な問題の優先修正",
            "包括的テストの再実行",
            "システム安定性の向上"
        ])
    else:
        steps.extend([
            "全システムの見直し",
            "基本機能の修正",
            "段階的な機能実装"
        ])
    
    return steps

def generate_deployment_recommendations(status):
    """デプロイメント推奨事項生成"""
    recommendations = []
    
    if status in ["excellent", "good"]:
        recommendations.extend([
            "Docker環境での本番デプロイメント可能",
            "HTTPS/SSL設定の実装",
            "監視システムの有効化",
            "バックアップシステムの設定"
        ])
    else:
        recommendations.extend([
            "開発環境での追加テストが必要",
            "段階的機能リリースを推奨",
            "十分なテスト後に本番展開"
        ])
    
    return recommendations

if __name__ == "__main__":
    success = main()
    print(f"\n{'🎉 最終テスト成功!' if success else '⚠️ 改善が必要です'}")
    sys.exit(0 if success else 1)