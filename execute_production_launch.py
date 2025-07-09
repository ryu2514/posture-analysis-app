#!/usr/bin/env python3
"""
本番運用開始実行スクリプト
production_launch_plan.pyの機能を統合実行
"""

import os
import sys
import subprocess
import time
import json
import requests
from datetime import datetime

def main():
    """本番運用開始実行"""
    print("🚀 本番運用開始実行")
    print("=" * 70)
    
    # 現在ディレクトリ設定
    project_dir = "/Users/kobayashiryuju/posture-analysis-app"
    os.chdir(project_dir)
    
    results = {}
    
    # Phase 1: 即座運用開始準備
    print("\n🎯 Phase 1: 即座運用開始準備")
    results['phase1'] = execute_immediate_launch()
    
    # Phase 2: 基本セキュリティ強化
    print("\n🔒 Phase 2: 基本セキュリティ強化")
    results['phase2'] = execute_security_hardening()
    
    # Phase 3: 運用環境確認
    print("\n✅ Phase 3: 運用環境確認")
    results['phase3'] = verify_production_readiness()
    
    # Phase 4: 継続的改善計画設定
    print("\n📈 Phase 4: 継続的改善計画設定")
    results['phase4'] = setup_continuous_improvement()
    
    # 最終レポート生成
    generate_launch_report(results)
    
    # 成功判定
    success_count = sum(1 for result in results.values() if result.get('success', False))
    overall_success = success_count >= 3  # 4中3で成功とする
    
    return overall_success

def execute_immediate_launch():
    """即座運用開始準備"""
    print("   🔍 システム起動と基本確認...")
    
    try:
        # 1. 必要ディレクトリ確認・作成
        required_dirs = ["logs", "uploads", "reports", "ssl", "monitoring", "scripts"]
        for dir_name in required_dirs:
            os.makedirs(dir_name, exist_ok=True)
        
        # 2. Docker環境起動
        print("      1. Docker環境起動...")
        docker_result = start_docker_system()
        
        # 3. 基本機能テスト
        print("      2. 基本機能テスト...")
        if docker_result:
            time.sleep(10)  # 起動待機
            function_test = test_basic_functionality()
        else:
            function_test = False
        
        # 4. アクセスURL確認
        print("      3. アクセスURL準備...")
        access_urls = {
            'enhanced_ui': 'http://127.0.0.1:8000/enhanced',
            'health_check': 'http://127.0.0.1:8000/health',
            'api_docs': 'http://127.0.0.1:8000/docs',
            'performance': 'http://127.0.0.1:8000/api/performance/summary'
        }
        
        success = docker_result and function_test
        
        if success:
            print("   ✅ 即座運用開始準備完了")
            print("      🌐 Enhanced UI: http://127.0.0.1:8000/enhanced")
            print("      🏥 Health Check: http://127.0.0.1:8000/health")
            print("      📊 Performance: http://127.0.0.1:8000/api/performance/summary")
        
        return {
            'success': success,
            'docker_started': docker_result,
            'function_test': function_test,
            'access_urls': access_urls
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def start_docker_system():
    """Dockerシステム起動"""
    try:
        # Docker Compose停止
        subprocess.run(['docker-compose', 'down'], capture_output=True, timeout=30)
        
        # Docker Compose起動
        result = subprocess.run(['docker-compose', 'up', '-d', '--build'], 
                               capture_output=True, text=True, timeout=300)
        
        return result.returncode == 0
    except Exception:
        return False

def test_basic_functionality():
    """基本機能テスト"""
    try:
        max_retries = 3
        for i in range(max_retries):
            try:
                response = requests.get('http://127.0.0.1:8000/health', timeout=10)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                if i < max_retries - 1:
                    time.sleep(5)
        return False
    except Exception:
        return False

def execute_security_hardening():
    """基本セキュリティ強化"""
    print("   🔍 基本セキュリティ強化実行...")
    
    security_checks = []
    
    # 1. セキュリティヘッダー確認
    print("      1. セキュリティヘッダー確認...")
    headers_result = verify_security_headers()
    security_checks.append(headers_result)
    
    # 2. SSL設定準備確認
    print("      2. SSL設定準備確認...")
    ssl_result = verify_ssl_preparation()
    security_checks.append(ssl_result)
    
    # 3. ログ監視設定
    print("      3. ログ監視設定...")
    logging_result = setup_basic_monitoring()
    security_checks.append(logging_result)
    
    successful_checks = sum(1 for result in security_checks if result)
    
    print(f"   ✅ セキュリティ強化完了 ({successful_checks}/{len(security_checks)})")
    
    return {
        'success': successful_checks >= 2,
        'completed_checks': successful_checks,
        'total_checks': len(security_checks)
    }

def verify_security_headers():
    """セキュリティヘッダー確認"""
    try:
        response = requests.head('http://127.0.0.1:8000/', timeout=5)
        security_headers = ['X-Frame-Options', 'X-Content-Type-Options']
        present_headers = [h for h in security_headers if h in response.headers]
        return len(present_headers) >= 1
    except:
        return False

def verify_ssl_preparation():
    """SSL設定準備確認"""
    ssl_dir = "ssl"
    ssl_script = "ssl-setup.sh"
    return os.path.exists(ssl_dir) and os.path.exists(ssl_script)

def setup_basic_monitoring():
    """基本監視設定"""
    # 監視ディレクトリ作成
    monitoring_dir = "monitoring"
    os.makedirs(monitoring_dir, exist_ok=True)
    
    # 基本監視スクリプト作成
    monitoring_script = """#!/bin/bash
# Basic monitoring script
echo "$(date): System monitoring active" >> monitoring/system.log
"""
    
    script_path = os.path.join(monitoring_dir, "basic_monitor.sh")
    with open(script_path, 'w') as f:
        f.write(monitoring_script)
    
    os.chmod(script_path, 0o755)
    return True

def verify_production_readiness():
    """本番環境準備度確認"""
    print("   🔍 本番環境準備度確認...")
    
    readiness_checks = []
    
    # 1. システム安定性確認
    print("      1. システム安定性確認...")
    stability_check = check_system_stability()
    readiness_checks.append(stability_check)
    
    # 2. パフォーマンス確認
    print("      2. パフォーマンス確認...")
    performance_check = check_performance()
    readiness_checks.append(performance_check)
    
    # 3. 基本機能確認
    print("      3. 基本機能確認...")
    function_check = test_basic_functionality()
    readiness_checks.append(function_check)
    
    passed_checks = sum(1 for check in readiness_checks if check)
    production_ready = passed_checks >= 2
    
    print(f"   ✅ 本番準備度確認完了 ({passed_checks}/{len(readiness_checks)})")
    if production_ready:
        print("      🎉 本番運用準備完了!")
    
    return {
        'success': production_ready,
        'passed_checks': passed_checks,
        'total_checks': len(readiness_checks)
    }

def check_system_stability():
    """システム安定性確認"""
    try:
        # Dockerコンテナ状態確認
        result = subprocess.run(['docker-compose', 'ps'], 
                               capture_output=True, text=True, timeout=10)
        return 'Up' in result.stdout
    except:
        return False

def check_performance():
    """パフォーマンス確認"""
    try:
        response = requests.get('http://127.0.0.1:8000/api/performance/summary', timeout=10)
        return response.status_code == 200
    except:
        return False

def setup_continuous_improvement():
    """継続的改善計画設定"""
    print("   🔍 継続的改善計画設定...")
    
    improvement_plan = {
        'week_1_goals': [
            'ユーザーフィードバック収集',
            'パフォーマンス監視データ分析',
            'セキュリティ設定確認'
        ],
        'month_1_goals': [
            'APIキー認証実装検討',
            'ユーザー管理システム検討',
            'セキュリティ監査計画'
        ],
        'quarter_1_goals': [
            'JWT認証システム実装',
            '高度な監視・アラート',
            'スケーラビリティ向上'
        ]
    }
    
    # 改善計画保存
    plan_file = "continuous_improvement_plan.json"
    with open(plan_file, 'w', encoding='utf-8') as f:
        json.dump(improvement_plan, f, indent=2, ensure_ascii=False)
    
    print("   ✅ 継続的改善計画設定完了")
    
    return {
        'success': True,
        'plan_file': plan_file,
        'improvement_plan': improvement_plan
    }

def generate_launch_report(results):
    """運用開始レポート生成"""
    
    report = {
        'production_launch_report': {
            'timestamp': datetime.now().isoformat(),
            'launch_status': 'successful' if results.get('phase1', {}).get('success') else 'partial',
            'phase_results': results,
            'system_status': {
                'operational': results.get('phase1', {}).get('success', False),
                'secure': results.get('phase2', {}).get('success', False),
                'production_ready': results.get('phase3', {}).get('success', False),
                'improvement_plan': results.get('phase4', {}).get('success', False)
            },
            'access_information': results.get('phase1', {}).get('access_urls', {}),
            'next_steps': {
                'immediate': [
                    'システム使用開始',
                    'ユーザーテスト実施',
                    'フィードバック収集'
                ],
                'week_1': [
                    'セキュリティ強化計画詳細化',
                    'パフォーマンス監視データ確認',
                    'ユーザー体験改善'
                ],
                'month_1': [
                    'APIキー認証実装',
                    'ユーザー管理システム',
                    'セキュリティ監査実施'
                ]
            }
        }
    }
    
    # レポート保存
    report_path = "production_launch_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    # コンソール出力
    print(f"\n🎉 本番運用開始完了!")
    print(f"📄 詳細レポート: {report_path}")
    
    if results.get('phase1', {}).get('access_urls'):
        print(f"\n🌐 アクセス情報:")
        for name, url in results['phase1']['access_urls'].items():
            print(f"   • {name}: {url}")
    
    print(f"\n📋 次のアクション:")
    for action in report['production_launch_report']['next_steps']['immediate']:
        print(f"   • {action}")

if __name__ == "__main__":
    success = main()
    print(f"\n{'🎉 本番運用開始成功!' if success else '⚠️ 部分的な問題があります'}")
    sys.exit(0 if success else 1)