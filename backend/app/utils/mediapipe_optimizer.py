"""
MediaPipe最適化ユーティリティ
異なる設定での姿勢検出を試行し、最適な結果を取得
"""

import mediapipe as mp
import cv2
import numpy as np
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
from backend.app.utils.logger import get_logger

logger = get_logger("mediapipe_optimizer")

@dataclass
class MediaPipeConfig:
    """MediaPipe設定クラス"""
    name: str
    static_image_mode: bool = True
    model_complexity: int = 1
    enable_segmentation: bool = False
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'static_image_mode': self.static_image_mode,
            'model_complexity': self.model_complexity,
            'enable_segmentation': self.enable_segmentation,
            'min_detection_confidence': self.min_detection_confidence,
            'min_tracking_confidence': self.min_tracking_confidence
        }

@dataclass
class DetectionResult:
    """検出結果クラス"""
    success: bool
    landmarks: Optional[Any] = None
    confidence: float = 0.0
    landmarks_count: int = 0
    config_name: str = ""
    processing_time: float = 0.0

class MediaPipeOptimizer:
    """MediaPipe最適化クラス"""
    
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        
        # 複数の設定パターンを定義（成功率順）
        self.configs = [
            # 高精度設定（現在の人間の画像向け）
            MediaPipeConfig(
                name="high_precision",
                model_complexity=2,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7
            ),
            
            # 標準設定（バランス重視）
            MediaPipeConfig(
                name="standard",
                model_complexity=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            ),
            
            # 低閾値設定（検出困難な画像向け）
            MediaPipeConfig(
                name="low_threshold",
                model_complexity=1,
                min_detection_confidence=0.3,
                min_tracking_confidence=0.3
            ),
            
            # 最低閾値設定（最後の手段）
            MediaPipeConfig(
                name="minimal_threshold",
                model_complexity=0,
                min_detection_confidence=0.1,
                min_tracking_confidence=0.1
            ),
            
            # シンプル設定（軽量）
            MediaPipeConfig(
                name="simple",
                model_complexity=0,
                min_detection_confidence=0.2,
                min_tracking_confidence=0.2
            )
        ]
        
        logger.info("MediaPipeOptimizer初期化完了", 
                   config_count=len(self.configs),
                   config_names=[c.name for c in self.configs])
    
    def optimize_detection(self, image_rgb: np.ndarray) -> DetectionResult:
        """
        複数の設定で姿勢検出を試行し、最適な結果を返す
        """
        logger.info("最適化検出開始", image_shape=image_rgb.shape)
        
        best_result = DetectionResult(success=False)
        
        for i, config in enumerate(self.configs):
            logger.info(f"設定試行: {config.name}", 
                       attempt=i+1, 
                       total_attempts=len(self.configs),
                       config=config.to_dict())
            
            # 検出実行
            result = self._try_detection(image_rgb, config)
            
            if result.success:
                logger.info(f"検出成功: {config.name}", 
                           landmarks_count=result.landmarks_count,
                           confidence=result.confidence,
                           processing_time=result.processing_time)
                return result
            else:
                logger.warning(f"検出失敗: {config.name}", 
                             processing_time=result.processing_time)
        
        logger.error("全設定で検出失敗", total_attempts=len(self.configs))
        return best_result
    
    def _try_detection(self, image_rgb: np.ndarray, config: MediaPipeConfig) -> DetectionResult:
        """
        指定された設定で姿勢検出を実行
        """
        import time
        start_time = time.time()
        
        try:
            # MediaPipeインスタンス作成
            pose = self.mp_pose.Pose(**config.to_dict())
            
            # 検出実行
            results = pose.process(image_rgb)
            
            processing_time = time.time() - start_time
            
            if results.pose_landmarks:
                # 成功
                landmarks_count = len(results.pose_landmarks.landmark)
                avg_confidence = sum(lm.visibility for lm in results.pose_landmarks.landmark) / landmarks_count
                
                return DetectionResult(
                    success=True,
                    landmarks=results.pose_landmarks,
                    confidence=avg_confidence,
                    landmarks_count=landmarks_count,
                    config_name=config.name,
                    processing_time=processing_time
                )
            else:
                # 失敗
                return DetectionResult(
                    success=False,
                    config_name=config.name,
                    processing_time=processing_time
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"設定 {config.name} でエラー", error=e)
            return DetectionResult(
                success=False,
                config_name=config.name,
                processing_time=processing_time
            )
        finally:
            # リソース解放
            if 'pose' in locals():
                pose.close()

class ImagePreprocessor:
    """画像前処理クラス"""
    
    def __init__(self):
        self.logger = get_logger("image_preprocessor")
    
    def get_preprocessing_strategies(self) -> List[str]:
        """利用可能な前処理戦略一覧"""
        return [
            "original",           # 元画像
            "enhanced",          # 標準強化
            "high_contrast",     # 高コントラスト
            "brightness_boost",  # 明度向上
            "edge_enhanced",     # エッジ強化
            "histogram_eq"       # ヒストグラム平坦化
        ]
    
    def preprocess_image(self, image_bgr: np.ndarray, strategy: str) -> np.ndarray:
        """
        指定された戦略で画像を前処理
        """
        self.logger.debug(f"前処理適用: {strategy}", 
                         input_shape=image_bgr.shape)
        
        if strategy == "original":
            return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        
        elif strategy == "enhanced":
            return self._enhanced_preprocessing(image_bgr)
        
        elif strategy == "high_contrast":
            return self._high_contrast_preprocessing(image_bgr)
        
        elif strategy == "brightness_boost":
            return self._brightness_boost_preprocessing(image_bgr)
        
        elif strategy == "edge_enhanced":
            return self._edge_enhanced_preprocessing(image_bgr)
        
        elif strategy == "histogram_eq":
            return self._histogram_equalization_preprocessing(image_bgr)
        
        else:
            self.logger.warning(f"未知の前処理戦略: {strategy}")
            return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    
    def _enhanced_preprocessing(self, image_bgr: np.ndarray) -> np.ndarray:
        """標準強化前処理"""
        # グレースケール変換
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        
        # CLAHE適用
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced_gray = clahe.apply(gray)
        
        # BGR変換
        enhanced_bgr = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2BGR)
        
        # バイラテラルフィルタ
        filtered = cv2.bilateralFilter(enhanced_bgr, 9, 75, 75)
        
        return cv2.cvtColor(filtered, cv2.COLOR_BGR2RGB)
    
    def _high_contrast_preprocessing(self, image_bgr: np.ndarray) -> np.ndarray:
        """高コントラスト前処理"""
        # LAB色空間変換
        lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Lチャンネルにヒストグラム平坦化
        l = cv2.equalizeHist(l)
        
        # チャンネル結合
        enhanced_lab = cv2.merge([l, a, b])
        enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        return cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)
    
    def _brightness_boost_preprocessing(self, image_bgr: np.ndarray) -> np.ndarray:
        """明度向上前処理"""
        hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        # 明度チャンネルを強化
        v = cv2.add(v, 30)
        v = np.clip(v, 0, 255)
        
        enhanced_hsv = cv2.merge([h, s, v])
        enhanced_bgr = cv2.cvtColor(enhanced_hsv, cv2.COLOR_HSV2BGR)
        
        return cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)
    
    def _edge_enhanced_preprocessing(self, image_bgr: np.ndarray) -> np.ndarray:
        """エッジ強化前処理"""
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        
        # ガウシアンぼかし
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # アンシャープマスク
        unsharp_mask = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)
        unsharp_mask = np.clip(unsharp_mask, 0, 255).astype(np.uint8)
        
        # BGR変換
        enhanced_bgr = cv2.cvtColor(unsharp_mask, cv2.COLOR_GRAY2BGR)
        
        return cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)
    
    def _histogram_equalization_preprocessing(self, image_bgr: np.ndarray) -> np.ndarray:
        """ヒストグラム平坦化前処理"""
        # YUV色空間変換
        yuv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2YUV)
        y, u, v = cv2.split(yuv)
        
        # Yチャンネルにヒストグラム平坦化
        y_eq = cv2.equalizeHist(y)
        
        # チャンネル結合
        yuv_eq = cv2.merge([y_eq, u, v])
        enhanced_bgr = cv2.cvtColor(yuv_eq, cv2.COLOR_YUV2BGR)
        
        return cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)

class ComprehensiveDetector:
    """包括的検出器 - 複数の設定と前処理を組み合わせ"""
    
    def __init__(self):
        self.optimizer = MediaPipeOptimizer()
        self.preprocessor = ImagePreprocessor()
        self.logger = get_logger("comprehensive_detector")
    
    def detect_pose_comprehensive(self, image_bgr: np.ndarray) -> DetectionResult:
        """
        包括的姿勢検出 - 複数の前処理と設定を組み合わせて最適な結果を取得
        """
        self.logger.info("包括的姿勢検出開始", image_shape=image_bgr.shape)
        
        strategies = self.preprocessor.get_preprocessing_strategies()
        best_result = DetectionResult(success=False)
        
        for i, strategy in enumerate(strategies):
            self.logger.info(f"前処理戦略試行: {strategy}", 
                           attempt=i+1, 
                           total_strategies=len(strategies))
            
            # 前処理適用
            preprocessed_image = self.preprocessor.preprocess_image(image_bgr, strategy)
            
            # 最適化検出実行
            result = self.optimizer.optimize_detection(preprocessed_image)
            
            if result.success:
                self.logger.info(f"包括的検出成功", 
                               preprocessing_strategy=strategy,
                               mediapipe_config=result.config_name,
                               confidence=result.confidence,
                               landmarks_count=result.landmarks_count)
                return result
            else:
                self.logger.debug(f"前処理戦略失敗: {strategy}")
        
        self.logger.error("包括的検出失敗 - 全戦略で検出不可", 
                         total_strategies=len(strategies))
        return best_result