"""
MediaPipe設定最適化ユーティリティ
ログ分析に基づいて最適な設定を提案・適用
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from backend.app.utils.logger import get_logger
from backend.app.utils.mediapipe_optimizer import MediaPipeConfig

logger = get_logger("config_optimizer")

@dataclass
class OptimizationResult:
    """最適化結果クラス"""
    recommended_config: MediaPipeConfig
    confidence_score: float
    reasoning: List[str]
    expected_improvement: Dict[str, float]

class ConfigOptimizer:
    """設定最適化クラス"""
    
    def __init__(self):
        self.logger = get_logger("config_optimizer")
        self.analysis_history = []
        
    def analyze_logs_and_optimize(self, log_analysis_file: Optional[str] = None) -> OptimizationResult:
        """
        ログ分析に基づいて最適な設定を推奨
        """
        self.logger.info("設定最適化分析開始")
        
        # ログデータの読み込み
        log_data = self._load_log_analysis(log_analysis_file)
        
        # 失敗パターンの分析
        failure_patterns = self._analyze_failure_patterns(log_data)
        
        # パフォーマンス分析
        performance_metrics = self._analyze_performance_metrics(log_data)
        
        # 最適化推奨事項の生成
        optimization_result = self._generate_optimization_recommendations(
            failure_patterns, performance_metrics
        )
        
        self.logger.info("設定最適化完了", 
                        recommended_config=optimization_result.recommended_config.name,
                        confidence=optimization_result.confidence_score)
        
        return optimization_result
    
    def _load_log_analysis(self, log_file: Optional[str]) -> Dict[str, Any]:
        """ログ分析データの読み込み"""
        
        if log_file and os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # デフォルトの分析データ（ログファイルがない場合）
        return {
            "summary": {
                "total_images": 10,
                "successful_analyses": 3,
                "failed_analyses": 7,
                "success_rate": 0.3
            },
            "common_failure_patterns": [
                "Could not detect pose landmarks",
                "Low confidence detection",
                "Insufficient lighting"
            ],
            "performance_metrics": {
                "average_duration": 2.5,
                "max_duration": 5.0,
                "min_duration": 1.0
            }
        }
    
    def _analyze_failure_patterns(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """失敗パターンの分析"""
        
        failure_analysis = {
            "detection_failures": 0,
            "confidence_issues": 0,
            "preprocessing_needed": 0,
            "lighting_issues": 0,
            "pose_orientation_issues": 0
        }
        
        common_failures = log_data.get("common_failure_patterns", [])
        
        for failure in common_failures:
            failure_lower = failure.lower()
            
            if "detect" in failure_lower or "landmarks" in failure_lower:
                failure_analysis["detection_failures"] += 1
            elif "confidence" in failure_lower:
                failure_analysis["confidence_issues"] += 1
            elif "lighting" in failure_lower or "brightness" in failure_lower:
                failure_analysis["lighting_issues"] += 1
            elif "orientation" in failure_lower or "pose" in failure_lower:
                failure_analysis["pose_orientation_issues"] += 1
            else:
                failure_analysis["preprocessing_needed"] += 1
        
        self.logger.info("失敗パターン分析完了", failure_analysis=failure_analysis)
        return failure_analysis
    
    def _analyze_performance_metrics(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """パフォーマンスメトリクスの分析"""
        
        performance = log_data.get("performance_metrics", {})
        
        analysis = {
            "speed_issues": performance.get("average_duration", 0) > 3.0,
            "consistency_issues": (
                performance.get("max_duration", 0) - performance.get("min_duration", 0)
            ) > 4.0,
            "overall_slow": performance.get("average_duration", 0) > 5.0
        }
        
        self.logger.info("パフォーマンス分析完了", analysis=analysis)
        return analysis
    
    def _generate_optimization_recommendations(
        self, 
        failure_patterns: Dict[str, Any], 
        performance_metrics: Dict[str, Any]
    ) -> OptimizationResult:
        """最適化推奨事項の生成"""
        
        reasoning = []
        confidence_score = 0.5  # ベーススコア
        
        # 検出失敗が多い場合
        if failure_patterns["detection_failures"] > 2:
            recommended_config = MediaPipeConfig(
                name="aggressive_detection",
                model_complexity=2,
                min_detection_confidence=0.3,
                min_tracking_confidence=0.3,
                static_image_mode=True,
                enable_segmentation=True
            )
            reasoning.append("検出失敗が多いため、低閾値・高複雑度設定を推奨")
            confidence_score += 0.2
            
        # 信頼度の問題がある場合
        elif failure_patterns["confidence_issues"] > 1:
            recommended_config = MediaPipeConfig(
                name="high_confidence_optimized",
                model_complexity=2,
                min_detection_confidence=0.8,
                min_tracking_confidence=0.8,
                static_image_mode=True,
                enable_segmentation=False
            )
            reasoning.append("信頼度問題のため、高精度設定を推奨")
            confidence_score += 0.3
            
        # パフォーマンスの問題がある場合
        elif performance_metrics["overall_slow"]:
            recommended_config = MediaPipeConfig(
                name="performance_optimized",
                model_complexity=0,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
                static_image_mode=True,
                enable_segmentation=False
            )
            reasoning.append("処理速度問題のため、軽量設定を推奨")
            confidence_score += 0.25
            
        # 照明問題がある場合
        elif failure_patterns["lighting_issues"] > 0:
            recommended_config = MediaPipeConfig(
                name="lighting_robust",
                model_complexity=1,
                min_detection_confidence=0.4,
                min_tracking_confidence=0.4,
                static_image_mode=True,
                enable_segmentation=True
            )
            reasoning.append("照明問題のため、セグメンテーション有効化を推奨")
            confidence_score += 0.2
            
        # デフォルト推奨（問題が少ない場合）
        else:
            recommended_config = MediaPipeConfig(
                name="balanced_optimized",
                model_complexity=1,
                min_detection_confidence=0.6,
                min_tracking_confidence=0.6,
                static_image_mode=True,
                enable_segmentation=False
            )
            reasoning.append("バランスの良い設定を推奨")
            confidence_score += 0.1
        
        # 期待される改善予測
        expected_improvement = self._calculate_expected_improvement(
            failure_patterns, performance_metrics, recommended_config
        )
        
        return OptimizationResult(
            recommended_config=recommended_config,
            confidence_score=min(1.0, confidence_score),
            reasoning=reasoning,
            expected_improvement=expected_improvement
        )
    
    def _calculate_expected_improvement(
        self, 
        failure_patterns: Dict[str, Any], 
        performance_metrics: Dict[str, Any],
        config: MediaPipeConfig
    ) -> Dict[str, float]:
        """期待される改善効果の計算"""
        
        improvement = {
            "detection_success_rate": 0.0,
            "processing_speed": 0.0,
            "overall_confidence": 0.0
        }
        
        # 設定に基づく改善予測
        if config.model_complexity == 2:
            improvement["detection_success_rate"] = 0.3  # 30%改善
            improvement["processing_speed"] = -0.2  # 20%遅くなる
            improvement["overall_confidence"] = 0.25  # 25%改善
            
        elif config.model_complexity == 0:
            improvement["detection_success_rate"] = -0.1  # 10%悪化
            improvement["processing_speed"] = 0.4  # 40%高速化
            improvement["overall_confidence"] = -0.05  # 5%悪化
            
        else:  # model_complexity == 1
            improvement["detection_success_rate"] = 0.15  # 15%改善
            improvement["processing_speed"] = 0.1  # 10%高速化
            improvement["overall_confidence"] = 0.1  # 10%改善
        
        # 信頼度閾値による調整
        if config.min_detection_confidence < 0.4:
            improvement["detection_success_rate"] += 0.2
        elif config.min_detection_confidence > 0.7:
            improvement["detection_success_rate"] -= 0.1
            improvement["overall_confidence"] += 0.15
        
        return improvement
    
    def apply_optimized_config(self, optimization_result: OptimizationResult) -> bool:
        """最適化された設定の適用"""
        
        try:
            self.logger.info("最適化設定適用開始", 
                           config=optimization_result.recommended_config.name)
            
            # 設定ファイルの更新
            config_data = {
                "optimized_config": asdict(optimization_result.recommended_config),
                "optimization_metadata": {
                    "confidence_score": optimization_result.confidence_score,
                    "reasoning": optimization_result.reasoning,
                    "expected_improvement": optimization_result.expected_improvement,
                    "applied_at": str(os.popen('date').read().strip())
                }
            }
            
            config_file = "/Users/kobayashiryuju/posture-analysis-app/optimized_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info("最適化設定保存完了", config_file=config_file)
            return True
            
        except Exception as e:
            self.logger.error("最適化設定適用失敗", error=e)
            return False
    
    def get_current_optimization_status(self) -> Dict[str, Any]:
        """現在の最適化状態を取得"""
        
        status = {
            "has_optimized_config": False,
            "current_config": None,
            "last_optimization": None
        }
        
        config_file = "/Users/kobayashiryuju/posture-analysis-app/optimized_config.json"
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    status["has_optimized_config"] = True
                    status["current_config"] = data.get("optimized_config")
                    status["last_optimization"] = data.get("optimization_metadata", {}).get("applied_at")
            except Exception as e:
                self.logger.error("最適化状態読み込み失敗", error=e)
        
        return status

def main():
    """メイン実行"""
    print("🔧 MediaPipe設定最適化ツール")
    
    optimizer = ConfigOptimizer()
    
    # 分析レポートがあれば使用
    analysis_file = "/Users/kobayashiryuju/posture-analysis-app/analysis_report.json"
    
    # 最適化実行
    result = optimizer.analyze_logs_and_optimize(analysis_file)
    
    print(f"\n📊 最適化結果:")
    print(f"推奨設定: {result.recommended_config.name}")
    print(f"信頼度: {result.confidence_score:.1%}")
    print(f"理由: {', '.join(result.reasoning)}")
    
    print(f"\n期待される改善:")
    for metric, improvement in result.expected_improvement.items():
        print(f"- {metric}: {improvement:+.1%}")
    
    # 設定適用
    if optimizer.apply_optimized_config(result):
        print("\n✅ 最適化設定が適用されました")
    else:
        print("\n❌ 最適化設定の適用に失敗しました")

if __name__ == "__main__":
    main()