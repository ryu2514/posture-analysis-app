#!/usr/bin/env python3
"""
詳細ログ収集スクリプト - 実際の画像でMediaPipe検出の問題箇所を特定
"""

import sys
import os
import json
import time
from typing import Dict, List, Any
from pathlib import Path

# プロジェクトパスを追加
sys.path.insert(0, '/Users/kobayashiryuju/posture-analysis-app')

def create_test_image_analysis():
    """テスト画像での詳細分析"""
    
    print("🔍 詳細ログ収集開始 - MediaPipe検出問題の特定")
    
    try:
        # Logger import
        from backend.app.utils.logger import get_logger
        from backend.app.services.pose_analyzer import PoseAnalyzer
        from backend.app.utils.mediapipe_optimizer import ComprehensiveDetector
        
        logger = get_logger("detailed_analysis")
        logger.info("詳細ログ収集開始")
        
        # PoseAnalyzer initialization
        analyzer = PoseAnalyzer()
        detector = ComprehensiveDetector()
        
        # テスト画像のパスリスト（実際の画像がある場合）
        test_image_paths = [
            "/Users/kobayashiryuju/posture-analysis-app/test_images/person1.jpg",
            "/Users/kobayashiryuju/posture-analysis-app/test_images/person2.jpg",
            "/Users/kobayashiryuju/posture-analysis-app/uploads/test.jpg"
        ]
        
        # サンプル画像作成（テスト用）
        sample_image_data = create_sample_test_image()
        
        analysis_results = []
        
        print("\n📊 画像分析詳細ログ収集...")
        
        # Sample image analysis
        print("1️⃣ サンプル画像分析...")
        result = analyze_image_with_detailed_logging(analyzer, sample_image_data, "sample_image", logger)
        analysis_results.append(result)
        
        # Real image analysis (if available)
        for i, image_path in enumerate(test_image_paths, 2):
            if os.path.exists(image_path):
                print(f"{i}️⃣ 実画像分析: {image_path}")
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                result = analyze_image_with_detailed_logging(analyzer, image_data, f"real_image_{i-1}", logger)
                analysis_results.append(result)
        
        # 結果分析とレポート生成
        print("\n📋 分析結果レポート生成...")
        generate_analysis_report(analysis_results, logger)
        
        # 最適化推奨事項の生成
        print("\n🔧 最適化推奨事項生成...")
        optimization_recommendations = generate_optimization_recommendations(analysis_results)
        
        logger.info("詳細分析完了", 
                   total_images_analyzed=len(analysis_results),
                   recommendations=optimization_recommendations)
        
        print("✅ 詳細ログ収集完了")
        print("📁 詳細ログは logs/ ディレクトリに保存されました")
        print("📊 分析レポートを確認してください")
        
        return True
        
    except Exception as e:
        print(f"❌ 詳細ログ収集失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_test_image():
    """サンプルテスト画像データ作成"""
    # 簡単な黒背景画像を作成（実際のテスト用）
    import cv2
    import numpy as np
    
    # 640x480の黒画像作成
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # 簡単な人体シルエット描画（テスト用）
    # 頭
    cv2.circle(image, (320, 100), 30, (255, 255, 255), -1)
    # 胴体
    cv2.rectangle(image, (300, 130), (340, 300), (255, 255, 255), -1)
    # 腕
    cv2.rectangle(image, (260, 150), (300, 170), (255, 255, 255), -1)
    cv2.rectangle(image, (340, 150), (380, 170), (255, 255, 255), -1)
    # 脚
    cv2.rectangle(image, (305, 300), (315, 400), (255, 255, 255), -1)
    cv2.rectangle(image, (325, 300), (335, 400), (255, 255, 255), -1)
    
    # エンコード
    _, encoded = cv2.imencode('.jpg', image)
    return encoded.tobytes()

def analyze_image_with_detailed_logging(analyzer, image_data: bytes, image_name: str, logger) -> Dict[str, Any]:
    """詳細ログ付き画像分析"""
    
    analysis_start = time.time()
    logger.info(f"詳細分析開始: {image_name}", image_size=len(image_data))
    
    try:
        # Step-by-step analysis with logging
        result = {
            "image_name": image_name,
            "image_size": len(image_data),
            "analysis_start_time": analysis_start,
            "success": False,
            "error_details": None,
            "processing_steps": [],
            "mediapipe_attempts": [],
            "preprocessing_attempts": []
        }
        
        # Run analysis
        analysis_result = None
        try:
            # Async call simulation (since we can't use await here)
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            analysis_result = loop.run_until_complete(analyzer.analyze_image(image_data))
            loop.close()
        except Exception as e:
            result["error_details"] = str(e)
            logger.error(f"分析エラー: {image_name}", error=e)
        
        # Update result
        if analysis_result:
            result["success"] = True
            result["overall_score"] = analysis_result.overall_score
            result["confidence"] = analysis_result.confidence
            result["pose_orientation"] = analysis_result.pose_orientation
        
        result["analysis_duration"] = time.time() - analysis_start
        
        logger.info(f"詳細分析完了: {image_name}", 
                   success=result["success"],
                   duration=result["analysis_duration"])
        
        return result
        
    except Exception as e:
        logger.error(f"詳細分析失敗: {image_name}", error=e)
        return {
            "image_name": image_name,
            "success": False,
            "error_details": str(e),
            "analysis_duration": time.time() - analysis_start
        }

def generate_analysis_report(results: List[Dict[str, Any]], logger):
    """分析結果レポート生成"""
    
    total_images = len(results)
    successful_analyses = sum(1 for r in results if r["success"])
    failed_analyses = total_images - successful_analyses
    
    report = {
        "summary": {
            "total_images": total_images,
            "successful_analyses": successful_analyses,
            "failed_analyses": failed_analyses,
            "success_rate": successful_analyses / total_images if total_images > 0 else 0
        },
        "detailed_results": results,
        "common_failure_patterns": extract_failure_patterns(results),
        "performance_metrics": calculate_performance_metrics(results)
    }
    
    # レポート保存
    report_path = "/Users/kobayashiryuju/posture-analysis-app/analysis_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    logger.info("分析レポート生成完了", 
               report_path=report_path,
               success_rate=report["summary"]["success_rate"])
    
    print(f"📊 分析結果サマリー:")
    print(f"   - 総画像数: {total_images}")
    print(f"   - 成功: {successful_analyses}")
    print(f"   - 失敗: {failed_analyses}")
    print(f"   - 成功率: {report['summary']['success_rate']:.1%}")

def extract_failure_patterns(results: List[Dict[str, Any]]) -> List[str]:
    """失敗パターンの抽出"""
    patterns = []
    
    failed_results = [r for r in results if not r["success"]]
    
    for result in failed_results:
        if result.get("error_details"):
            patterns.append(result["error_details"])
    
    return list(set(patterns))  # 重複除去

def calculate_performance_metrics(results: List[Dict[str, Any]]) -> Dict[str, float]:
    """パフォーマンスメトリクス計算"""
    successful_results = [r for r in results if r["success"]]
    
    if not successful_results:
        return {"average_duration": 0, "max_duration": 0, "min_duration": 0}
    
    durations = [r["analysis_duration"] for r in successful_results]
    
    return {
        "average_duration": sum(durations) / len(durations),
        "max_duration": max(durations),
        "min_duration": min(durations)
    }

def generate_optimization_recommendations(results: List[Dict[str, Any]]) -> List[str]:
    """最適化推奨事項生成"""
    recommendations = []
    
    failed_count = sum(1 for r in results if not r["success"])
    total_count = len(results)
    
    if failed_count > 0:
        recommendations.append("MediaPipe検出失敗の改善が必要")
        recommendations.append("前処理パイプラインの強化を検討")
        recommendations.append("検出閾値の調整を実施")
    
    if total_count > 0:
        avg_duration = sum(r.get("analysis_duration", 0) for r in results) / total_count
        if avg_duration > 5.0:  # 5秒以上
            recommendations.append("処理速度の最適化が必要")
    
    if not recommendations:
        recommendations.append("現在の設定は良好に動作中")
    
    return recommendations

if __name__ == "__main__":
    success = create_test_image_analysis()
    print(f"\n{'✅ 詳細ログ収集成功' if success else '❌ 詳細ログ収集失敗'}")
    sys.exit(0 if success else 1)