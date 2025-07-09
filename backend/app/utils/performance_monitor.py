"""
パフォーマンス監視システム
リアルタイムパフォーマンス追跡と最適化提案
"""

import time
import psutil
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import deque
import json
import os
from backend.app.utils.logger import get_logger

logger = get_logger("performance_monitor")

@dataclass
class PerformanceMetrics:
    """パフォーマンス指標クラス"""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    memory_available: float
    processing_time: float
    operation_type: str
    success: bool
    error_message: Optional[str] = None

@dataclass
class SystemResources:
    """システムリソース情報"""
    cpu_count: int
    total_memory_gb: float
    available_memory_gb: float
    cpu_frequency_mhz: float
    load_average: List[float]

class PerformanceMonitor:
    """パフォーマンス監視クラス"""
    
    def __init__(self, max_history_size: int = 1000):
        self.max_history_size = max_history_size
        self.metrics_history = deque(maxlen=max_history_size)
        self.active_operations = {}
        self.monitoring_enabled = True
        self.lock = threading.Lock()
        
        # システム情報取得
        self.system_info = self._get_system_info()
        
        logger.info("パフォーマンス監視開始", 
                   system_info=asdict(self.system_info),
                   max_history=max_history_size)
    
    def _get_system_info(self) -> SystemResources:
        """システムリソース情報取得"""
        try:
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            
            # CPU周波数
            try:
                cpu_freq = psutil.cpu_freq()
                frequency = cpu_freq.current if cpu_freq else 0
            except:
                frequency = 0
            
            # 負荷平均（Unix系のみ）
            try:
                load_avg = list(os.getloadavg())
            except:
                load_avg = [0, 0, 0]
            
            return SystemResources(
                cpu_count=cpu_count,
                total_memory_gb=memory.total / (1024**3),
                available_memory_gb=memory.available / (1024**3),
                cpu_frequency_mhz=frequency,
                load_average=load_avg
            )
        except Exception as e:
            logger.error("システム情報取得失敗", error=e)
            return SystemResources(0, 0, 0, 0, [0, 0, 0])
    
    def start_operation(self, operation_id: str, operation_type: str) -> str:
        """操作開始の記録"""
        if not self.monitoring_enabled:
            return operation_id
        
        start_time = time.time()
        
        with self.lock:
            self.active_operations[operation_id] = {
                'operation_type': operation_type,
                'start_time': start_time,
                'start_cpu': psutil.cpu_percent(),
                'start_memory': psutil.virtual_memory().percent
            }
        
        logger.debug("操作開始記録", 
                    operation_id=operation_id,
                    operation_type=operation_type)
        
        return operation_id
    
    def end_operation(self, operation_id: str, success: bool = True, error_message: Optional[str] = None) -> PerformanceMetrics:
        """操作終了の記録"""
        if not self.monitoring_enabled or operation_id not in self.active_operations:
            # ダミーのメトリクスを返す
            return PerformanceMetrics(
                timestamp=time.time(),
                cpu_usage=0,
                memory_usage=0,
                memory_available=0,
                processing_time=0,
                operation_type="unknown",
                success=success,
                error_message=error_message
            )
        
        end_time = time.time()
        
        with self.lock:
            operation_data = self.active_operations.pop(operation_id)
        
        # パフォーマンス指標計算
        processing_time = end_time - operation_data['start_time']
        current_cpu = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        
        metrics = PerformanceMetrics(
            timestamp=end_time,
            cpu_usage=current_cpu,
            memory_usage=memory_info.percent,
            memory_available=memory_info.available / (1024**3),
            processing_time=processing_time,
            operation_type=operation_data['operation_type'],
            success=success,
            error_message=error_message
        )
        
        # 履歴に追加
        self.metrics_history.append(metrics)
        
        # パフォーマンス警告チェック
        self._check_performance_warnings(metrics)
        
        logger.info("操作完了記録", 
                   operation_id=operation_id,
                   processing_time=processing_time,
                   success=success,
                   cpu_usage=current_cpu,
                   memory_usage=memory_info.percent)
        
        return metrics
    
    def _check_performance_warnings(self, metrics: PerformanceMetrics):
        """パフォーマンス警告チェック"""
        warnings = []
        
        # 処理時間警告
        if metrics.processing_time > 10.0:  # 10秒以上
            warnings.append(f"処理時間が長すぎます: {metrics.processing_time:.2f}秒")
        
        # CPU使用率警告
        if metrics.cpu_usage > 90.0:
            warnings.append(f"CPU使用率が高すぎます: {metrics.cpu_usage:.1f}%")
        
        # メモリ使用率警告
        if metrics.memory_usage > 85.0:
            warnings.append(f"メモリ使用率が高すぎます: {metrics.memory_usage:.1f}%")
        
        # 利用可能メモリ警告
        if metrics.memory_available < 1.0:  # 1GB未満
            warnings.append(f"利用可能メモリが少なすぎます: {metrics.memory_available:.2f}GB")
        
        # 警告ログ出力
        if warnings:
            logger.warning("パフォーマンス警告", 
                          operation_type=metrics.operation_type,
                          warnings=warnings)
    
    def get_performance_summary(self, last_n_operations: int = 100) -> Dict[str, Any]:
        """パフォーマンスサマリー取得"""
        if not self.metrics_history:
            return {"summary": "データなし"}
        
        # 最新のN件を取得
        recent_metrics = list(self.metrics_history)[-last_n_operations:]
        
        # 成功した操作のみでの統計
        successful_metrics = [m for m in recent_metrics if m.success]
        
        if not successful_metrics:
            return {"summary": "成功した操作がありません"}
        
        # 統計計算
        processing_times = [m.processing_time for m in successful_metrics]
        cpu_usages = [m.cpu_usage for m in successful_metrics]
        memory_usages = [m.memory_usage for m in successful_metrics]
        
        # 操作タイプ別統計
        operation_stats = {}
        for metrics in successful_metrics:
            op_type = metrics.operation_type
            if op_type not in operation_stats:
                operation_stats[op_type] = []
            operation_stats[op_type].append(metrics.processing_time)
        
        # 操作タイプ別平均時間
        operation_averages = {
            op_type: sum(times) / len(times)
            for op_type, times in operation_stats.items()
        }
        
        summary = {
            "total_operations": len(recent_metrics),
            "successful_operations": len(successful_metrics),
            "success_rate": len(successful_metrics) / len(recent_metrics),
            "performance_metrics": {
                "avg_processing_time": sum(processing_times) / len(processing_times),
                "max_processing_time": max(processing_times),
                "min_processing_time": min(processing_times),
                "avg_cpu_usage": sum(cpu_usages) / len(cpu_usages),
                "avg_memory_usage": sum(memory_usages) / len(memory_usages)
            },
            "operation_type_averages": operation_averages,
            "system_resources": asdict(self.system_info)
        }
        
        return summary
    
    def get_optimization_recommendations(self) -> List[str]:
        """最適化推奨事項取得"""
        recommendations = []
        
        if not self.metrics_history:
            return ["データ不足 - より多くの操作を実行してください"]
        
        summary = self.get_performance_summary()
        metrics = summary.get("performance_metrics", {})
        
        # 処理時間に基づく推奨事項
        avg_time = metrics.get("avg_processing_time", 0)
        if avg_time > 5.0:
            recommendations.append("処理時間が長いため、アルゴリズムの最適化を検討")
        
        # CPU使用率に基づく推奨事項
        avg_cpu = metrics.get("avg_cpu_usage", 0)
        if avg_cpu > 80.0:
            recommendations.append("CPU使用率が高いため、並列処理や軽量化を検討")
        
        # メモリ使用率に基づく推奨事項
        avg_memory = metrics.get("avg_memory_usage", 0)
        if avg_memory > 75.0:
            recommendations.append("メモリ使用率が高いため、メモリ効率化を検討")
        
        # 成功率に基づく推奨事項
        success_rate = summary.get("success_rate", 1.0)
        if success_rate < 0.8:
            recommendations.append("成功率が低いため、エラーハンドリングの改善を検討")
        
        # 操作タイプ別推奨事項
        op_averages = summary.get("operation_type_averages", {})
        for op_type, avg_time in op_averages.items():
            if avg_time > 8.0:
                recommendations.append(f"{op_type}操作の最適化が必要")
        
        if not recommendations:
            recommendations.append("パフォーマンスは良好です")
        
        return recommendations
    
    def export_performance_data(self, filepath: str):
        """パフォーマンスデータのエクスポート"""
        try:
            data = {
                "system_info": asdict(self.system_info),
                "summary": self.get_performance_summary(),
                "recommendations": self.get_optimization_recommendations(),
                "raw_metrics": [asdict(m) for m in self.metrics_history],
                "export_timestamp": time.time()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info("パフォーマンスデータエクスポート完了", 
                       filepath=filepath,
                       metrics_count=len(self.metrics_history))
            
        except Exception as e:
            logger.error("パフォーマンスデータエクスポート失敗", 
                        filepath=filepath, error=e)
    
    def clear_history(self):
        """履歴データのクリア"""
        with self.lock:
            self.metrics_history.clear()
        logger.info("パフォーマンス履歴クリア完了")
    
    def disable_monitoring(self):
        """監視の無効化"""
        self.monitoring_enabled = False
        logger.info("パフォーマンス監視無効化")
    
    def enable_monitoring(self):
        """監視の有効化"""
        self.monitoring_enabled = True
        logger.info("パフォーマンス監視有効化")

# グローバルモニターインスタンス
_global_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """グローバルパフォーマンスモニター取得"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor

def monitor_performance(operation_type: str):
    """パフォーマンス監視デコレータ"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            operation_id = f"{func.__name__}_{int(time.time() * 1000)}"
            
            monitor.start_operation(operation_id, operation_type)
            
            try:
                result = func(*args, **kwargs)
                monitor.end_operation(operation_id, success=True)
                return result
            except Exception as e:
                monitor.end_operation(operation_id, success=False, error_message=str(e))
                raise
        
        return wrapper
    return decorator

def main():
    """テスト実行"""
    print("🚀 パフォーマンス監視テスト")
    
    monitor = PerformanceMonitor()
    
    # テスト操作
    for i in range(5):
        op_id = monitor.start_operation(f"test_op_{i}", "test_operation")
        time.sleep(0.1)  # 処理シミュレート
        monitor.end_operation(op_id, success=True)
    
    # サマリー出力
    summary = monitor.get_performance_summary()
    print(f"📊 パフォーマンスサマリー:")
    print(f"   成功操作: {summary['successful_operations']}")
    print(f"   平均処理時間: {summary['performance_metrics']['avg_processing_time']:.3f}秒")
    
    # 推奨事項
    recommendations = monitor.get_optimization_recommendations()
    print(f"🔧 推奨事項: {recommendations}")
    
    # データエクスポート
    export_path = "/Users/kobayashiryuju/posture-analysis-app/performance_test_report.json"
    monitor.export_performance_data(export_path)
    print(f"📄 レポート保存: {export_path}")

if __name__ == "__main__":
    main()