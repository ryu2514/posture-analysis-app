import logging
import json
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
import sys
import os

class PostureAnalysisLogger:
    """
    強力なロギングクラス - 姿勢分析アプリ専用
    デバッグ、エラートラッキング、パフォーマンス監視を統合
    """
    
    def __init__(self, name: str = "posture_analysis", log_level: str = "INFO"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.performance_data = {}
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.setup_logger(log_level)
        
    def setup_logger(self, log_level: str):
        """ロガーの詳細設定"""
        # ログレベル設定
        level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # 既存のハンドラをクリア
        self.logger.handlers.clear()
        
        # ログディレクトリ作成
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 詳細フォーマッター
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # コンソールハンドラ（色付き）
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(DetailedColorFormatter())
        console_handler.setLevel(level)
        
        # ファイルハンドラ（全ログ）
        file_handler = logging.FileHandler(
            log_dir / f"posture_analysis_{self.session_id}.log",
            encoding='utf-8'
        )
        file_handler.setFormatter(detailed_formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # エラー専用ハンドラ
        error_handler = logging.FileHandler(
            log_dir / f"errors_{self.session_id}.log",
            encoding='utf-8'
        )
        error_handler.setFormatter(detailed_formatter)
        error_handler.setLevel(logging.ERROR)
        
        # JSON構造化ログハンドラ
        json_handler = logging.FileHandler(
            log_dir / f"structured_{self.session_id}.jsonl",
            encoding='utf-8'
        )
        json_handler.setFormatter(JSONFormatter())
        json_handler.setLevel(logging.INFO)
        
        # ハンドラを追加
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(json_handler)
        
    def debug(self, message: str, **kwargs):
        """デバッグログ"""
        self._log(logging.DEBUG, message, **kwargs)
        
    def info(self, message: str, **kwargs):
        """情報ログ"""
        self._log(logging.INFO, message, **kwargs)
        
    def warning(self, message: str, **kwargs):
        """警告ログ"""
        self._log(logging.WARNING, message, **kwargs)
        
    def error(self, message: str, error: Exception = None, **kwargs):
        """エラーログ"""
        extra_data = kwargs.copy()
        if error:
            extra_data.update({
                'error_type': type(error).__name__,
                'error_message': str(error),
                'traceback': traceback.format_exc()
            })
        self._log(logging.ERROR, message, **extra_data)
        
    def critical(self, message: str, **kwargs):
        """重大エラーログ"""
        self._log(logging.CRITICAL, message, **kwargs)
        
    def _log(self, level: int, message: str, **kwargs):
        """内部ログメソッド"""
        extra_data = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        
        # ログレコード作成
        record = self.logger.makeRecord(
            name=self.logger.name,
            level=level,
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=None,
            extra=extra_data
        )
        
        self.logger.handle(record)
    
    # === MediaPipe専用ログメソッド ===
    
    def log_image_processing(self, filename: str, size: int, format: str):
        """画像処理開始ログ"""
        self.info(
            "画像処理開始",
            component="image_processor",
            image_filename=filename,
            file_size=size,
            file_format=format
        )
        
    def log_pose_detection_start(self, image_size: tuple, model_complexity: int):
        """姿勢検出開始ログ"""
        self.info(
            "MediaPipe姿勢検出開始",
            component="pose_detector",
            image_width=image_size[0],
            image_height=image_size[1],
            model_complexity=model_complexity
        )
        
    def log_pose_detection_result(self, success: bool, landmarks_count: int = 0, confidence: float = 0.0):
        """姿勢検出結果ログ"""
        level = logging.INFO if success else logging.WARNING
        self._log(
            level,
            f"姿勢検出{'成功' if success else '失敗'}",
            component="pose_detector",
            success=success,
            landmarks_detected=landmarks_count,
            average_confidence=confidence
        )
        
    def log_preprocessing_step(self, step_name: str, input_shape: tuple, output_shape: tuple):
        """前処理ステップログ"""
        self.debug(
            f"前処理ステップ: {step_name}",
            component="image_preprocessor",
            step=step_name,
            input_shape=input_shape,
            output_shape=output_shape
        )
        
    def log_metrics_calculation(self, orientation: str, metrics: Dict[str, float]):
        """メトリクス計算ログ"""
        self.info(
            "姿勢メトリクス計算完了",
            component="metrics_calculator",
            pose_orientation=orientation,
            calculated_metrics=list(metrics.keys()),
            metrics_values=metrics
        )
        
    # === パフォーマンス監視 ===
    
    def start_timer(self, operation_name: str) -> str:
        """タイマー開始"""
        timer_id = f"{operation_name}_{datetime.now().timestamp()}"
        self.performance_data[timer_id] = {
            'operation': operation_name,
            'start_time': datetime.now(),
            'start_timestamp': datetime.now().timestamp()
        }
        return timer_id
        
    def end_timer(self, timer_id: str, additional_data: Dict = None):
        """タイマー終了とログ出力"""
        if timer_id not in self.performance_data:
            self.warning(f"タイマーID {timer_id} が見つかりません")
            return
            
        timer_data = self.performance_data[timer_id]
        end_time = datetime.now()
        duration = (end_time - timer_data['start_time']).total_seconds()
        
        log_data = {
            'component': 'performance',
            'operation': timer_data['operation'],
            'duration_seconds': duration,
            'start_time': timer_data['start_time'].isoformat(),
            'end_time': end_time.isoformat()
        }
        
        if additional_data:
            log_data.update(additional_data)
            
        self.info(
            f"パフォーマンス: {timer_data['operation']} 完了 ({duration:.3f}秒)",
            **log_data
        )
        
        # クリーンアップ
        del self.performance_data[timer_id]
        return duration
        
    # === API呼び出しログ ===
    
    def log_api_request(self, endpoint: str, method: str, client_ip: str, file_size: int = None):
        """API リクエストログ"""
        self.info(
            f"API リクエスト: {method} {endpoint}",
            component="api",
            endpoint=endpoint,
            method=method,
            client_ip=client_ip,
            file_size=file_size
        )
        
    def log_api_response(self, endpoint: str, status_code: int, response_time: float, error: str = None):
        """API レスポンスログ"""
        level = logging.INFO if status_code < 400 else logging.ERROR
        self._log(
            level,
            f"API レスポンス: {endpoint} - {status_code}",
            component="api",
            endpoint=endpoint,
            status_code=status_code,
            response_time=response_time,
            error=error
        )
        
    # === システム情報ログ ===
    
    def log_system_info(self):
        """システム情報ログ"""
        import platform
        import psutil
        
        self.info(
            "システム情報",
            component="system",
            platform=platform.platform(),
            python_version=platform.python_version(),
            cpu_count=psutil.cpu_count(),
            memory_total=psutil.virtual_memory().total,
            memory_available=psutil.virtual_memory().available
        )
        
    def log_mediapipe_config(self, config: Dict):
        """MediaPipe設定ログ"""
        self.info(
            "MediaPipe設定",
            component="mediapipe",
            **config
        )


class DetailedColorFormatter(logging.Formatter):
    """色付きコンソール出力フォーマッター"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # シアン
        'INFO': '\033[32m',     # 緑
        'WARNING': '\033[33m',  # 黄
        'ERROR': '\033[31m',    # 赤
        'CRITICAL': '\033[35m', # マゼンタ
        'RESET': '\033[0m'      # リセット
    }
    
    def format(self, record):
        # カラーコード追加
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # タイムスタンプ
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S.%f')[:-3]
        
        # メッセージフォーマット
        message = f"{color}[{record.levelname:8}]{reset} {timestamp} | {record.name} | {record.funcName}:{record.lineno} | {record.getMessage()}"
        
        # 追加データがある場合
        if hasattr(record, 'component'):
            message += f" | 📦 {record.component}"
            
        return message


class JSONFormatter(logging.Formatter):
    """JSON構造化ログフォーマッター"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage()
        }
        
        # 追加属性を含める
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 'stack_info']:
                log_entry[key] = value
                
        return json.dumps(log_entry, ensure_ascii=False, default=str)


# グローバルロガーインスタンス
logger = PostureAnalysisLogger()

# 便利関数
def get_logger(name: str = None) -> PostureAnalysisLogger:
    """ロガーインスタンス取得"""
    if name:
        return PostureAnalysisLogger(name)
    return logger

def log_function_call(func):
    """関数呼び出しをログ出力するデコレータ"""
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.debug(f"関数呼び出し: {func_name}", function=func_name, args_count=len(args), kwargs_keys=list(kwargs.keys()))
        
        timer_id = logger.start_timer(f"function_{func_name}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"関数完了: {func_name}", function=func_name, success=True)
            return result
        except Exception as e:
            logger.error(f"関数エラー: {func_name}", error=e, function=func_name)
            raise
        finally:
            logger.end_timer(timer_id)
            
    return wrapper