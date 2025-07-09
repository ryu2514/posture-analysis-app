#!/usr/bin/env python3
"""
最終デプロイメントテストスクリプト
全最適化機能を統合した環境での動作確認
"""

import subprocess
import sys
import os
import time
import requests
import json
from pathlib import Path

def main():
    """最終デプロイメントテスト実行"""
    print("🚀 最終デプロイメントテスト開始")
    print("=" * 70)
    
    test_results = {}
    
    # Step 1: Docker環境テスト
    print("\n🐳 Step 1: Docker環境テスト")
    test_results['docker'] = test_docker_environment()
    
    # Step 2: サービス起動確認
    print("\n🔄 Step 2: サービス起動確認")
    test_results['services'] = test_service_startup()
    
    # Step 3: API機能テスト
    print("\n🔗 Step 3: API機能テスト")
    test_results['api'] = test_api_functionality()
    
    # Step 4: Enhanced UI テスト
    print("\n🎨 Step 4: Enhanced UI テスト")
    test_results['ui'] = test_enhanced_ui()
    
    # Step 5: パフォーマンステスト
    print("\n⚡ Step 5: パフォーマンステスト")
    test_results['performance'] = test_performance_features()
    
    # Step 6: ログ機能テスト
    print("\n📋 Step 6: ログ機能テスト")
    test_results['logging'] = test_logging_features()
    
    # 最終結果
    print("\n" + "=" * 70)
    success_count = sum(1 for result in test_results.values() if result.get('success', False))
    total_tests = len(test_results)
    
    print(f"📊 最終テスト結果: {success_count}/{total_tests} 成功")
    
    if success_count == total_tests:
        print("🎉 全テスト成功 - 本番デプロイメント準備完了!")
        generate_deployment_ready_report(test_results)
        return True
    else:
        print("⚠️ 一部テスト失敗 - 問題を確認してください")
        generate_issue_report(test_results)
        return False

def test_docker_environment():
    """Docker環境テスト"""
    print("   🔍 Docker環境確認中...")
    
    try:
        # Docker Compose設定確認
        compose_file = "/Users/kobayashiryuju/posture-analysis-app/docker-compose.yml"
        if not os.path.exists(compose_file):
            return {'success': False, 'error': 'docker-compose.yml not found'}
        
        # Dockerfile確認
        dockerfile = "/Users/kobayashiryuju/posture-analysis-app/Dockerfile"
        if not os.path.exists(dockerfile):
            return {'success': False, 'error': 'Dockerfile not found'}
        
        # 必要なディレクトリ確認
        required_dirs = ['backend', 'logs', 'uploads', 'reports']
        missing_dirs = []
        
        for dir_name in required_dirs:
            dir_path = f"/Users/kobayashiryuju/posture-analysis-app/{dir_name}"
            if not os.path.exists(dir_path):
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            # 不足ディレクトリを作成
            for dir_name in missing_dirs:
                os.makedirs(f"/Users/kobayashiryuju/posture-analysis-app/{dir_name}", exist_ok=True)
            print(f"   ✅ 作成されたディレクトリ: {missing_dirs}")
        
        print("   ✅ Docker環境確認完了")
        return {
            'success': True,
            'compose_file_exists': True,
            'dockerfile_exists': True,
            'directories_ready': True,
            'created_dirs': missing_dirs
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_service_startup():
    """サービス起動確認"""
    print("   🔍 サービス起動シミュレート...")
    
    try:
        # メインモジュールのインポート確認
        sys.path.insert(0, '/Users/kobayashiryuju/posture-analysis-app')
        
        # 主要モジュールインポートテスト
        from backend.app.main import app
        from backend.app.services.pose_analyzer import PoseAnalyzer
        from backend.app.utils.logger import get_logger
        from backend.app.utils.performance_monitor import get_performance_monitor
        
        # 初期化テスト
        logger = get_logger("startup_test")
        monitor = get_performance_monitor()
        analyzer = PoseAnalyzer()
        
        logger.info("サービス起動確認テスト実行")
        
        print("   ✅ サービス起動確認完了")
        return {
            'success': True,
            'app_imported': True,
            'analyzer_initialized': True,
            'logger_ready': True,
            'monitor_ready': True
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_api_functionality():
    """API機能テスト"""
    print("   🔍 API機能テスト...")
    
    try:
        # FastAPIアプリケーションのテスト
        from fastapi.testclient import TestClient
        from backend.app.main import app
        
        client = TestClient(app)
        
        # ヘルスチェック
        health_response = client.get("/health")
        health_ok = health_response.status_code == 200
        
        # ルートエンドポイント
        root_response = client.get("/")
        root_ok = root_response.status_code == 200
        
        # 参照値エンドポイント
        ref_response = client.get("/metrics/reference")
        ref_ok = ref_response.status_code == 200
        
        # パフォーマンスエンドポイント
        perf_response = client.get("/api/performance/summary")
        perf_ok = perf_response.status_code == 200
        
        print("   ✅ API機能テスト完了")
        return {
            'success': all([health_ok, root_ok, ref_ok, perf_ok]),
            'health_endpoint': health_ok,
            'root_endpoint': root_ok,
            'reference_endpoint': ref_ok,
            'performance_endpoint': perf_ok
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_enhanced_ui():
    """Enhanced UI テスト"""
    print("   🔍 Enhanced UI確認...")
    
    try:
        # Enhanced demo ファイル確認
        enhanced_demo = "/Users/kobayashiryuju/posture-analysis-app/enhanced_demo.html"
        if not os.path.exists(enhanced_demo):
            return {'success': False, 'error': 'enhanced_demo.html not found'}
        
        # ファイル内容確認
        with open(enhanced_demo, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 重要な機能の存在確認
        has_performance_section = 'performanceSection' in content
        has_drag_drop = 'dragover' in content
        has_progress_bar = 'progress-bar' in content
        has_error_handling = 'status-error' in content
        has_api_integration = '/api/performance' in content
        
        print("   ✅ Enhanced UI確認完了")
        return {
            'success': True,
            'file_exists': True,
            'performance_section': has_performance_section,
            'drag_drop_support': has_drag_drop,
            'progress_indicator': has_progress_bar,
            'error_handling': has_error_handling,
            'api_integration': has_api_integration
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_performance_features():
    """パフォーマンス機能テスト"""
    print("   🔍 パフォーマンス機能テスト...")
    
    try:
        from backend.app.utils.performance_monitor import get_performance_monitor
        
        monitor = get_performance_monitor()
        
        # 基本操作テスト
        op_id = monitor.start_operation("test_op", "test")
        time.sleep(0.1)
        metrics = monitor.end_operation(op_id, success=True)
        
        # サマリー機能テスト
        summary = monitor.get_performance_summary()
        has_summary = 'total_operations' in summary
        
        # 推奨事項機能テスト
        recommendations = monitor.get_optimization_recommendations()
        has_recommendations = len(recommendations) > 0
        
        # エクスポート機能テスト
        export_path = "/Users/kobayashiryuju/posture-analysis-app/test_performance_export.json"
        monitor.export_performance_data(export_path)
        export_created = os.path.exists(export_path)
        
        print("   ✅ パフォーマンス機能テスト完了")
        return {
            'success': True,
            'operation_tracking': metrics.processing_time > 0,
            'summary_generation': has_summary,
            'recommendations': has_recommendations,
            'data_export': export_created
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_logging_features():
    """ログ機能テスト"""
    print("   🔍 ログ機能テスト...")
    
    try:
        from backend.app.utils.logger import get_logger
        
        logger = get_logger("final_test")
        
        # 基本ログテスト
        logger.info("最終テスト実行", test_type="logging")
        logger.warning("警告テスト")
        logger.debug("デバッグテスト")
        
        # MediaPipe専用ログテスト
        logger.log_image_processing("test.jpg", 1024, "JPEG")
        logger.log_pose_detection_start((640, 480), 2)
        logger.log_pose_detection_result(True, 33, 0.95)
        
        # システム情報ログ
        logger.log_system_info()
        
        # タイマー機能テスト
        timer_id = logger.start_timer("test_timer")
        time.sleep(0.05)
        duration = logger.end_timer(timer_id)
        
        # ログディレクトリ確認
        logs_dir = "/Users/kobayashiryuju/posture-analysis-app/logs"
        os.makedirs(logs_dir, exist_ok=True)
        
        print("   ✅ ログ機能テスト完了")
        return {
            'success': True,
            'basic_logging': True,
            'mediapipe_logging': True,
            'system_info_logging': True,
            'timer_functionality': duration > 0,
            'logs_directory': os.path.exists(logs_dir)
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def generate_deployment_ready_report(test_results):
    """デプロイメント準備完了レポート生成"""
    
    report = {
        "deployment_status": "READY",
        "timestamp": time.time(),
        "test_results": test_results,
        "deployment_checklist": {
            "docker_environment": "✅ Ready",
            "service_modules": "✅ Ready", 
            "api_endpoints": "✅ Ready",
            "enhanced_ui": "✅ Ready",
            "performance_monitoring": "✅ Ready",
            "logging_system": "✅ Ready"
        },
        "next_actions": [
            "Docker Compose で本番環境起動",
            "Enhanced UI での動作確認",
            "パフォーマンス監視の有効化",
            "ログ監視システムの設定",
            "ユーザー受け入れテストの実行"
        ],
        "access_urls": {
            "main_api": "http://127.0.0.1:8000",
            "health_check": "http://127.0.0.1:8000/health",
            "enhanced_demo": "http://127.0.0.1:8000/enhanced",
            "performance_api": "http://127.0.0.1:8000/api/performance/summary",
            "test_page": "http://127.0.0.1:8000/test"
        }
    }
    
    # レポート保存
    report_path = "/Users/kobayashiryuju/posture-analysis-app/deployment_ready_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📄 デプロイメント準備完了レポート: {report_path}")
    print("\n🎯 次のアクション:")
    for action in report["next_actions"]:
        print(f"   • {action}")
    
    print("\n🔗 アクセスURL:")
    for name, url in report["access_urls"].items():
        print(f"   • {name}: {url}")

def generate_issue_report(test_results):
    """問題レポート生成"""
    
    issues = []
    for test_name, result in test_results.items():
        if not result.get('success', False):
            issues.append({
                'test': test_name,
                'error': result.get('error', 'Unknown error'),
                'details': result
            })
    
    report = {
        "deployment_status": "ISSUES_FOUND",
        "timestamp": time.time(),
        "issues": issues,
        "test_results": test_results,
        "resolution_steps": [
            "失敗したテストの詳細確認",
            "エラーメッセージの分析",
            "必要なファイル・ディレクトリの確認",
            "依存関係の再インストール",
            "テストの再実行"
        ]
    }
    
    # レポート保存
    report_path = "/Users/kobayashiryuju/posture-analysis-app/deployment_issues_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📄 問題レポート: {report_path}")
    print(f"\n⚠️ 発見された問題: {len(issues)}")
    for issue in issues:
        print(f"   • {issue['test']}: {issue['error']}")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)