#!/usr/bin/env python3
"""
Enhanced UI 動作確認とパフォーマンステスト
"""

import requests
import time
import json
import os
import sys
from typing import Dict, Any, List
import cv2
import numpy as np

# プロジェクトパスを追加
sys.path.insert(0, '/Users/kobayashiryuju/posture-analysis-app')

def main():
    """Enhanced UI とパフォーマンステスト実行"""
    print("🎨 Enhanced UI 動作確認とパフォーマンステスト")
    print("=" * 70)
    
    test_results = {}
    
    # Step 1: UI ファイル確認
    print("\n📄 Step 1: Enhanced UI ファイル確認")
    test_results['ui_files'] = test_ui_files()
    
    # Step 2: API エンドポイント確認
    print("\n🔗 Step 2: API エンドポイント確認")
    test_results['api_endpoints'] = test_api_endpoints()
    
    # Step 3: 画像分析パフォーマンステスト
    print("\n⚡ Step 3: 画像分析パフォーマンステスト")
    test_results['performance_analysis'] = test_performance_analysis()
    
    # Step 4: パフォーマンス監視機能テスト
    print("\n📊 Step 4: パフォーマンス監視機能テスト")
    test_results['performance_monitoring'] = test_performance_monitoring()
    
    # Step 5: ユーザーエクスペリエンステスト
    print("\n👤 Step 5: ユーザーエクスペリエンステスト")
    test_results['user_experience'] = test_user_experience()
    
    # Step 6: エラーハンドリングテスト
    print("\n🚨 Step 6: エラーハンドリングテスト")
    test_results['error_handling'] = test_error_handling()
    
    # 結果の分析と報告
    success_count = sum(1 for result in test_results.values() if result.get('success', False))
    total_tests = len(test_results)
    
    print(f"\n📊 Enhanced UI テスト結果: {success_count}/{total_tests} 成功")
    
    # 詳細レポート生成
    generate_ui_test_report(test_results)
    
    return success_count >= total_tests * 0.8  # 80%以上成功で合格

def test_ui_files():
    """UI ファイル確認テスト"""
    print("   🔍 Enhanced UI ファイル確認中...")
    
    try:
        enhanced_demo_path = "/Users/kobayashiryuju/posture-analysis-app/enhanced_demo.html"
        
        if not os.path.exists(enhanced_demo_path):
            return {'success': False, 'error': 'enhanced_demo.html not found'}
        
        # ファイル内容分析
        with open(enhanced_demo_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 重要な機能の確認
        features = {
            'drag_drop': 'dragover' in content and 'drop' in content,
            'progress_bar': 'progress-bar' in content,
            'error_handling': 'status-error' in content and 'status-success' in content,
            'performance_section': 'performanceSection' in content,
            'api_integration': '/api/performance' in content,
            'pose_visualization': 'poseCanvas' in content,
            'responsive_design': '@media' in content,
            'async_processing': 'async' in content or 'await' in content
        }
        
        # JavaScriptクラス確認
        has_main_class = 'EnhancedPostureAnalyzer' in content
        has_methods = all(method in content for method in [
            'processFile', 'analyzeImage', 'displayResults', 'drawPoseLandmarks'
        ])
        
        print("   ✅ Enhanced UI ファイル確認完了")
        return {
            'success': True,
            'file_size': len(content),
            'features': features,
            'has_main_class': has_main_class,
            'has_essential_methods': has_methods,
            'feature_count': sum(features.values())
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_api_endpoints():
    """API エンドポイント確認テスト"""
    print("   🔍 API エンドポイント確認中...")
    
    api_base = "http://127.0.0.1:8000"
    endpoints_to_test = [
        "/health",
        "/",
        "/enhanced",
        "/metrics/reference",
        "/api/performance/summary",
        "/api/performance/recommendations"
    ]
    
    results = {}
    working_endpoints = 0
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{api_base}{endpoint}", timeout=5)
            success = response.status_code == 200
            results[endpoint] = {
                'status_code': response.status_code,
                'success': success,
                'response_time': response.elapsed.total_seconds()
            }
            if success:
                working_endpoints += 1
                
        except requests.exceptions.RequestException as e:
            results[endpoint] = {'success': False, 'error': str(e)}
    
    overall_success = working_endpoints >= len(endpoints_to_test) * 0.8
    
    print(f"   ✅ API エンドポイント確認完了 ({working_endpoints}/{len(endpoints_to_test)})")
    return {
        'success': overall_success,
        'working_endpoints': working_endpoints,
        'total_endpoints': len(endpoints_to_test),
        'endpoint_results': results
    }

def test_performance_analysis():
    """画像分析パフォーマンステスト"""
    print("   🔍 画像分析パフォーマンステスト実行中...")
    
    try:
        # テスト画像作成
        test_images = create_test_images()
        
        performance_results = []
        
        for i, (image_name, image_data) in enumerate(test_images.items()):
            print(f"      📸 {image_name} 分析中...")
            
            start_time = time.time()
            
            try:
                # API呼び出し
                files = {'file': (f'{image_name}.jpg', image_data, 'image/jpeg')}
                response = requests.post(
                    "http://127.0.0.1:8000/analyze-posture",
                    files=files,
                    timeout=30
                )
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                success = response.status_code == 200
                
                result = {
                    'image_name': image_name,
                    'success': success,
                    'processing_time': processing_time,
                    'status_code': response.status_code,
                    'image_size': len(image_data)
                }
                
                if success:
                    response_data = response.json()
                    result['overall_score'] = response_data.get('overall_score')
                    result['confidence'] = response_data.get('confidence')
                else:
                    result['error'] = response.text
                
                performance_results.append(result)
                
            except requests.exceptions.RequestException as e:
                performance_results.append({
                    'image_name': image_name,
                    'success': False,
                    'error': str(e),
                    'processing_time': time.time() - start_time
                })
        
        # パフォーマンス統計計算
        successful_analyses = [r for r in performance_results if r['success']]
        success_rate = len(successful_analyses) / len(performance_results)
        
        if successful_analyses:
            avg_processing_time = sum(r['processing_time'] for r in successful_analyses) / len(successful_analyses)
            max_processing_time = max(r['processing_time'] for r in successful_analyses)
            min_processing_time = min(r['processing_time'] for r in successful_analyses)
        else:
            avg_processing_time = max_processing_time = min_processing_time = 0
        
        print(f"   ✅ パフォーマンステスト完了 (成功率: {success_rate:.1%})")
        return {
            'success': success_rate >= 0.5,  # 50%以上成功で合格
            'success_rate': success_rate,
            'total_images': len(performance_results),
            'successful_analyses': len(successful_analyses),
            'avg_processing_time': avg_processing_time,
            'max_processing_time': max_processing_time,
            'min_processing_time': min_processing_time,
            'detailed_results': performance_results
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_performance_monitoring():
    """パフォーマンス監視機能テスト"""
    print("   🔍 パフォーマンス監視機能テスト中...")
    
    try:
        # パフォーマンスサマリー取得
        summary_response = requests.get("http://127.0.0.1:8000/api/performance/summary", timeout=10)
        summary_success = summary_response.status_code == 200
        
        summary_data = None
        if summary_success:
            summary_data = summary_response.json()
        
        # 推奨事項取得
        recommendations_response = requests.get("http://127.0.0.1:8000/api/performance/recommendations", timeout=10)
        recommendations_success = recommendations_response.status_code == 200
        
        recommendations_data = None
        if recommendations_success:
            recommendations_data = recommendations_response.json()
        
        # データエクスポート
        export_response = requests.post("http://127.0.0.1:8000/api/performance/export", timeout=10)
        export_success = export_response.status_code == 200
        
        print("   ✅ パフォーマンス監視機能テスト完了")
        return {
            'success': summary_success and recommendations_success,
            'summary_available': summary_success,
            'recommendations_available': recommendations_success,
            'export_available': export_success,
            'summary_data': summary_data,
            'recommendations_data': recommendations_data
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_user_experience():
    """ユーザーエクスペリエンステスト"""
    print("   🔍 ユーザーエクスペリエンステスト中...")
    
    try:
        # Enhanced demo ページ取得
        demo_response = requests.get("http://127.0.0.1:8000/enhanced", timeout=10)
        demo_available = demo_response.status_code == 200
        
        if demo_available:
            demo_content = demo_response.text
            
            # UX要素確認
            ux_features = {
                'responsive_design': '@media' in demo_content,
                'loading_indicators': 'spinner' in demo_content or 'loading' in demo_content,
                'progress_feedback': 'progress' in demo_content,
                'error_messages': 'error' in demo_content,
                'success_feedback': 'success' in demo_content,
                'drag_drop_support': 'dragover' in demo_content,
                'real_time_updates': 'real' in demo_content.lower() or 'live' in demo_content.lower(),
                'visual_feedback': 'animate' in demo_content or 'transition' in demo_content
            }
            
            # 性能関連の確認
            performance_features = {
                'performance_display': 'performance' in demo_content.lower(),
                'metrics_visualization': 'metric' in demo_content,
                'recommendations_display': 'recommendation' in demo_content
            }
        else:
            ux_features = {}
            performance_features = {}
        
        print("   ✅ ユーザーエクスペリエンステスト完了")
        return {
            'success': demo_available,
            'demo_page_available': demo_available,
            'ux_features': ux_features,
            'performance_features': performance_features,
            'ux_score': sum(ux_features.values()) if ux_features else 0,
            'performance_score': sum(performance_features.values()) if performance_features else 0
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_error_handling():
    """エラーハンドリングテスト"""
    print("   🔍 エラーハンドリングテスト中...")
    
    try:
        error_test_results = []
        
        # Test 1: 無効なファイル形式
        invalid_file_data = b"not an image"
        files = {'file': ('test.txt', invalid_file_data, 'text/plain')}
        
        response = requests.post(
            "http://127.0.0.1:8000/analyze-posture",
            files=files,
            timeout=10
        )
        
        error_test_results.append({
            'test': 'invalid_file_type',
            'expected_error': True,
            'got_error': response.status_code != 200,
            'status_code': response.status_code
        })
        
        # Test 2: 空のファイル
        empty_file_data = b""
        files = {'file': ('empty.jpg', empty_file_data, 'image/jpeg')}
        
        response = requests.post(
            "http://127.0.0.1:8000/analyze-posture",
            files=files,
            timeout=10
        )
        
        error_test_results.append({
            'test': 'empty_file',
            'expected_error': True,
            'got_error': response.status_code != 200,
            'status_code': response.status_code
        })
        
        # Test 3: 存在しないエンドポイント
        response = requests.get("http://127.0.0.1:8000/nonexistent", timeout=5)
        
        error_test_results.append({
            'test': 'nonexistent_endpoint',
            'expected_error': True,
            'got_error': response.status_code == 404,
            'status_code': response.status_code
        })
        
        # エラーハンドリング成功率計算
        properly_handled = sum(1 for test in error_test_results if test['got_error'] == test['expected_error'])
        error_handling_success = properly_handled / len(error_test_results)
        
        print("   ✅ エラーハンドリングテスト完了")
        return {
            'success': error_handling_success >= 0.8,
            'error_handling_success_rate': error_handling_success,
            'properly_handled_errors': properly_handled,
            'total_error_tests': len(error_test_results),
            'detailed_results': error_test_results
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def create_test_images() -> Dict[str, bytes]:
    """テスト画像作成"""
    images = {}
    
    # 画像1: 基本的な人体形状
    img1 = np.ones((480, 640, 3), dtype=np.uint8) * 255
    cv2.circle(img1, (320, 100), 30, (0, 0, 0), -1)  # 頭
    cv2.rectangle(img1, (290, 130), (350, 300), (0, 0, 0), -1)  # 胴体
    cv2.rectangle(img1, (250, 150), (290, 170), (0, 0, 0), -1)  # 左腕
    cv2.rectangle(img1, (350, 150), (390, 170), (0, 0, 0), -1)  # 右腕
    cv2.rectangle(img1, (305, 300), (315, 400), (0, 0, 0), -1)  # 左脚
    cv2.rectangle(img1, (325, 300), (335, 400), (0, 0, 0), -1)  # 右脚
    _, encoded1 = cv2.imencode('.jpg', img1)
    images['basic_pose'] = encoded1.tobytes()
    
    # 画像2: より詳細な人体形状
    img2 = np.ones((600, 800, 3), dtype=np.uint8) * 240
    # より詳細な人体描画
    cv2.circle(img2, (400, 120), 40, (50, 50, 50), -1)  # 頭
    cv2.ellipse(img2, (400, 250), (60, 100), 0, 0, 360, (50, 50, 50), -1)  # 胴体
    # 腕
    cv2.line(img2, (340, 200), (280, 250), (50, 50, 50), 8)
    cv2.line(img2, (460, 200), (520, 250), (50, 50, 50), 8)
    # 脚
    cv2.line(img2, (380, 350), (350, 480), (50, 50, 50), 8)
    cv2.line(img2, (420, 350), (450, 480), (50, 50, 50), 8)
    _, encoded2 = cv2.imencode('.jpg', img2)
    images['detailed_pose'] = encoded2.tobytes()
    
    # 画像3: 小さいサイズ
    img3 = np.ones((240, 320, 3), dtype=np.uint8) * 200
    cv2.circle(img3, (160, 50), 15, (0, 0, 0), -1)
    cv2.rectangle(img3, (145, 65), (175, 150), (0, 0, 0), -1)
    _, encoded3 = cv2.imencode('.jpg', img3)
    images['small_pose'] = encoded3.tobytes()
    
    return images

def generate_ui_test_report(test_results: Dict[str, Any]):
    """UI テストレポート生成"""
    
    report = {
        "test_type": "Enhanced UI Performance Test",
        "timestamp": time.time(),
        "test_results": test_results,
        "summary": {
            "total_test_categories": len(test_results),
            "successful_categories": sum(1 for r in test_results.values() if r.get('success', False)),
            "overall_success_rate": sum(1 for r in test_results.values() if r.get('success', False)) / len(test_results)
        },
        "performance_insights": generate_performance_insights(test_results),
        "ui_recommendations": generate_ui_recommendations(test_results),
        "next_steps": generate_next_steps(test_results)
    }
    
    # レポート保存
    report_path = "/Users/kobayashiryuju/posture-analysis-app/enhanced_ui_test_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📄 Enhanced UI テストレポート: {report_path}")
    
    # サマリー表示
    print(f"\n📊 テストサマリー:")
    print(f"   総合成功率: {report['summary']['overall_success_rate']:.1%}")
    print(f"   成功カテゴリ: {report['summary']['successful_categories']}/{report['summary']['total_test_categories']}")
    
    # パフォーマンス洞察
    if report['performance_insights']:
        print(f"\n💡 パフォーマンス洞察:")
        for insight in report['performance_insights']:
            print(f"   • {insight}")

def generate_performance_insights(test_results: Dict[str, Any]) -> List[str]:
    """パフォーマンス洞察生成"""
    insights = []
    
    # 画像分析パフォーマンス
    if 'performance_analysis' in test_results:
        perf_data = test_results['performance_analysis']
        if perf_data.get('success'):
            avg_time = perf_data.get('avg_processing_time', 0)
            if avg_time > 5:
                insights.append(f"画像分析時間が長い ({avg_time:.2f}秒) - 最適化が必要")
            elif avg_time < 2:
                insights.append(f"画像分析時間が良好 ({avg_time:.2f}秒)")
            
            success_rate = perf_data.get('success_rate', 0)
            if success_rate < 0.8:
                insights.append(f"分析成功率が低い ({success_rate:.1%}) - 改善が必要")
    
    # API応答時間
    if 'api_endpoints' in test_results:
        api_data = test_results['api_endpoints']
        if api_data.get('success'):
            endpoint_results = api_data.get('endpoint_results', {})
            slow_endpoints = [
                ep for ep, data in endpoint_results.items() 
                if data.get('response_time', 0) > 1.0
            ]
            if slow_endpoints:
                insights.append(f"応答が遅いエンドポイント: {slow_endpoints}")
    
    return insights

def generate_ui_recommendations(test_results: Dict[str, Any]) -> List[str]:
    """UI推奨事項生成"""
    recommendations = []
    
    # UX機能の改善提案
    if 'user_experience' in test_results:
        ux_data = test_results['user_experience']
        ux_score = ux_data.get('ux_score', 0)
        
        if ux_score < 6:
            recommendations.append("ユーザビリティ機能の追加が推奨されます")
        
        performance_score = ux_data.get('performance_score', 0)
        if performance_score < 3:
            recommendations.append("パフォーマンス表示機能の強化が推奨されます")
    
    # エラーハンドリングの改善
    if 'error_handling' in test_results:
        error_data = test_results['error_handling']
        error_rate = error_data.get('error_handling_success_rate', 0)
        
        if error_rate < 0.9:
            recommendations.append("エラーハンドリングの改善が推奨されます")
    
    return recommendations

def generate_next_steps(test_results: Dict[str, Any]) -> List[str]:
    """次のステップ生成"""
    steps = []
    
    overall_success = sum(1 for r in test_results.values() if r.get('success', False)) / len(test_results)
    
    if overall_success >= 0.9:
        steps.extend([
            "本番環境でのユーザー受け入れテスト実行",
            "パフォーマンス監視の継続実施",
            "ユーザーフィードバック収集"
        ])
    elif overall_success >= 0.7:
        steps.extend([
            "失敗したテストの個別修正",
            "パフォーマンス最適化の実施",
            "段階的な機能改善"
        ])
    else:
        steps.extend([
            "重要な問題の優先修正",
            "UI/UX の全面見直し",
            "基本機能の安定化"
        ])
    
    return steps

if __name__ == "__main__":
    success = main()
    print(f"\n{'🎉 Enhanced UI テスト成功!' if success else '⚠️ 改善が必要です'}")
    sys.exit(0 if success else 1)