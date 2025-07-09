import mediapipe as mp
import cv2
import numpy as np
import time
from typing import Optional, Dict, List, Tuple
from io import BytesIO
from PIL import Image

from backend.app.models.posture_result import PostureAnalysisResult, PostureMetrics
from backend.app.core.config import settings
from backend.app.utils.angle_calculator import AngleCalculator
from backend.app.utils.pose_detector import PoseDetector
from backend.app.utils.logger import get_logger, log_function_call
from backend.app.utils.mediapipe_optimizer import ComprehensiveDetector
from backend.app.utils.performance_monitor import get_performance_monitor, monitor_performance
from backend.app.utils.posture_classifier import PostureClassifier

logger = get_logger("pose_analyzer")
performance_monitor = get_performance_monitor()

class PoseAnalyzer:
    def __init__(self):
        # 新しい包括的検出器を使用
        self.comprehensive_detector = ComprehensiveDetector()
        self.mp_drawing = mp.solutions.drawing_utils
        self.angle_calc = AngleCalculator()
        self.pose_detector = PoseDetector()
        self.posture_classifier = PostureClassifier()
        
        # 最適化設定の読み込み
        self._load_optimized_config()
        
        logger.info("PoseAnalyzer初期化完了 - 包括的検出器使用", 
                   component="pose_analyzer",
                   has_optimized_config=hasattr(self, 'optimized_config'))
    
    def _load_optimized_config(self):
        """最適化設定の読み込み"""
        import json
        import os
        
        config_file = "/Users/kobayashiryuju/posture-analysis-app/optimized_config.json"
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.optimized_config = data.get("optimized_config")
                    logger.info("最適化設定読み込み完了", 
                               config_name=self.optimized_config.get("name") if self.optimized_config else None)
            except Exception as e:
                logger.warning("最適化設定読み込み失敗", error=e)
                self.optimized_config = None
        else:
            logger.info("最適化設定ファイルなし - デフォルト設定使用")
            self.optimized_config = None
        
    @log_function_call
    @monitor_performance("image_analysis")
    async def analyze_image(self, image_data: bytes) -> Optional[PostureAnalysisResult]:
        # 全体処理タイマー開始
        total_timer = logger.start_timer("total_analysis")
        
        # パフォーマンス監視開始
        perf_operation_id = performance_monitor.start_operation(
            f"analysis_{int(time.time() * 1000)}", 
            "pose_analysis"
        )
        
        try:
            # 画像変換
            conversion_timer = logger.start_timer("image_conversion")
            image = Image.open(BytesIO(image_data))
            image_rgb = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            logger.end_timer(conversion_timer)
            
            # 画像情報をログ
            logger.log_image_processing(
                filename="uploaded_image",
                size=len(image_data),
                format=image.format or "unknown"
            )
            logger.log_pose_detection_start(
                image_size=image_rgb.shape[:2],
                model_complexity=2
            )
            
            # 前処理
            preprocessing_timer = logger.start_timer("image_preprocessing")
            enhanced_image = self._enhance_image_for_pose_detection(image_rgb)
            logger.end_timer(preprocessing_timer)
            
            # 包括的姿勢検出（複数の設定と前処理を自動で試行）
            detection_timer = logger.start_timer("comprehensive_pose_detection")
            logger.info("包括的姿勢検出開始")
            
            detection_result = self.comprehensive_detector.detect_pose_comprehensive(image_rgb)
            
            logger.end_timer(detection_timer)
            
            # 検出結果の評価
            if not detection_result.success:
                logger.log_pose_detection_result(success=False)
                logger.error("包括的姿勢検出失敗", 
                           image_size=image_rgb.shape,
                           file_size=len(image_data))
                # デバッグ用画像保存
                debug_path = "/tmp/debug_image.jpg"
                cv2.imwrite(debug_path, image_rgb)
                logger.info(f"デバッグ画像保存: {debug_path}")
                return None
            
            # 検出成功
            results = type('Results', (), {'pose_landmarks': detection_result.landmarks})()
            logger.log_pose_detection_result(
                success=True, 
                landmarks_count=detection_result.landmarks_count,
                confidence=detection_result.confidence
            )
            logger.info("包括的検出成功", 
                       config_used=detection_result.config_name,
                       processing_time=detection_result.processing_time)
            
            # ランドマーク抽出
            landmarks_timer = logger.start_timer("landmarks_extraction")
            landmarks = self._extract_landmarks(results.pose_landmarks)
            logger.end_timer(landmarks_timer)
            
            # 姿勢方向検出
            orientation_timer = logger.start_timer("orientation_detection")
            orientation = self.pose_detector.detect_pose_orientation(landmarks)
            logger.end_timer(orientation_timer)
            logger.info("姿勢方向検出完了", pose_orientation=orientation)
            
            # ランドマーク検証
            validation_timer = logger.start_timer("landmark_validation")
            validation_results = self.pose_detector.validate_landmark_consistency(landmarks)
            logger.end_timer(validation_timer)
            logger.info("ランドマーク検証完了", validation_results=validation_results)
            
            # 姿勢品質スコア計算
            quality_timer = logger.start_timer("quality_calculation")
            pose_quality = self.pose_detector.calculate_pose_quality_score(landmarks)
            logger.end_timer(quality_timer)
            
            # 左右対称性計算
            symmetry_timer = logger.start_timer("symmetry_calculation")
            symmetry_scores = self.pose_detector.calculate_bilateral_symmetry(landmarks)
            logger.end_timer(symmetry_timer)
            
            # 姿勢メトリクス計算
            metrics_timer = logger.start_timer("metrics_calculation")
            metrics = self._calculate_enhanced_posture_metrics(landmarks, image.size, orientation)
            logger.end_timer(metrics_timer)
            
            # 追加メトリクス計算
            additional_metrics = self._calculate_additional_metrics(landmarks)
            
            # 座位姿勢判定
            is_seated = self._detect_seated_posture(landmarks)
            
            # 姿勢分類
            posture_type = self.posture_classifier.classify_posture_type(
                metrics, orientation, additional_metrics if is_seated else None
            )
            
            # カラー判定
            color_judgments = self.posture_classifier.calculate_color_judgment(
                metrics, additional_metrics
            )
            overall_color_judgment = self.posture_classifier.get_overall_color_judgment(color_judgments)
            
            # 改善提案
            improvement_suggestions = self.posture_classifier.generate_improvement_suggestions(
                posture_type['primary_type'], color_judgments
            )
            
            # メトリクス計算ログ
            logger.log_metrics_calculation(orientation, metrics.dict())
            
            # 総合スコア計算
            score_timer = logger.start_timer("overall_score_calculation")
            overall_score = self._calculate_enhanced_overall_score(metrics, pose_quality, symmetry_scores)
            logger.end_timer(score_timer)
            
            # 結果作成
            result_timer = logger.start_timer("result_creation")
            
            # メトリクスにadditional_metricsを統合
            if additional_metrics:
                metrics.knee_valgus_varus = additional_metrics.get('knee_valgus_varus')
                metrics.heel_inclination = additional_metrics.get('heel_inclination')
                metrics.seated_metrics = additional_metrics.get('seated_metrics')
            
            result = PostureAnalysisResult(
                landmarks=landmarks,
                metrics=metrics,
                overall_score=overall_score,
                image_width=image.size[0],
                image_height=image.size[1],
                confidence=pose_quality,
                pose_orientation=orientation,
                symmetry_scores=symmetry_scores,
                validation_results=validation_results,
                posture_type=posture_type,
                color_judgments=color_judgments,
                overall_color_judgment=overall_color_judgment,
                improvement_suggestions=improvement_suggestions,
                is_seated_posture=is_seated
            )
            logger.end_timer(result_timer)
            
            # 全体処理完了
            total_duration = logger.end_timer(total_timer)
            logger.info("姿勢分析完了", 
                       total_duration=total_duration,
                       overall_score=overall_score,
                       pose_orientation=orientation,
                       confidence=pose_quality)
            
            # パフォーマンス監視終了
            performance_monitor.end_operation(perf_operation_id, success=True)
            
            return result
            
        except Exception as e:
            logger.error("姿勢分析中にエラーが発生", error=e)
            # タイマーのクリーンアップ
            if 'total_timer' in locals():
                logger.end_timer(total_timer)
            # パフォーマンス監視終了（エラー）
            if 'perf_operation_id' in locals():
                performance_monitor.end_operation(perf_operation_id, success=False, error_message=str(e))
            return None
    
    def _extract_landmarks(self, pose_landmarks) -> Dict[str, Dict[str, float]]:
        landmarks = {}
        
        landmark_names = [
            'nose', 'left_eye_inner', 'left_eye', 'left_eye_outer',
            'right_eye_inner', 'right_eye', 'right_eye_outer',
            'left_ear', 'right_ear', 'mouth_left', 'mouth_right',
            'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
            'left_wrist', 'right_wrist', 'left_pinky', 'right_pinky',
            'left_index', 'right_index', 'left_thumb', 'right_thumb',
            'left_hip', 'right_hip', 'left_knee', 'right_knee',
            'left_ankle', 'right_ankle', 'left_heel', 'right_heel',
            'left_foot_index', 'right_foot_index'
        ]
        
        for i, landmark in enumerate(pose_landmarks.landmark):
            if i < len(landmark_names):
                landmarks[landmark_names[i]] = {
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'visibility': landmark.visibility
                }
        
        return landmarks
    
    def _enhance_image_for_pose_detection(self, image):
        """Enhance image quality for better pose detection"""
        # Convert to grayscale for processing
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced_gray = clahe.apply(gray)
        
        # Convert back to BGR for MediaPipe
        enhanced_bgr = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2BGR)
        
        # Apply bilateral filter to reduce noise while preserving edges
        filtered = cv2.bilateralFilter(enhanced_bgr, 9, 75, 75)
        
        # Convert to RGB for MediaPipe
        enhanced_rgb = cv2.cvtColor(filtered, cv2.COLOR_BGR2RGB)
        
        return enhanced_rgb
    
    def _apply_aggressive_preprocessing(self, image):
        """Apply aggressive preprocessing for difficult images"""
        # Resize image if too large
        height, width = image.shape[:2]
        if width > 1024 or height > 1024:
            scale_factor = min(1024/width, 1024/height)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            image = cv2.resize(image, (new_width, new_height))
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Increase contrast dramatically
        alpha = 2.5  # Contrast control
        beta = 30    # Brightness control
        enhanced = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        # Convert back to RGB for MediaPipe
        enhanced_rgb = cv2.cvtColor(blurred, cv2.COLOR_GRAY2RGB)
        
        return enhanced_rgb
    
    def _calculate_enhanced_posture_metrics(self, landmarks: Dict, image_size: Tuple[int, int], orientation: str) -> PostureMetrics:
        """Calculate enhanced posture metrics with orientation-specific analysis"""
        
        if orientation == 'sagittal':
            return self._calculate_sagittal_metrics(landmarks, image_size)
        elif orientation in ['frontal', 'posterior']:
            return self._calculate_frontal_metrics(landmarks, image_size)
        else:
            # Oblique or unknown - use combined analysis
            return self._calculate_combined_metrics(landmarks, image_size)
    
    def _calculate_sagittal_metrics(self, landmarks: Dict, image_size: Tuple[int, int]) -> PostureMetrics:
        """Calculate metrics optimized for sagittal (side) view"""
        
        # Enhanced pelvic tilt calculation
        pelvic_tilt = self.angle_calc.calculate_pelvic_tilt(
            landmarks['left_hip'], landmarks['right_hip']
        )
        
        # Enhanced thoracic kyphosis with better landmark selection
        thoracic_kyphosis = self._calculate_enhanced_thoracic_kyphosis(landmarks)
        
        # Enhanced cervical lordosis with ear position
        cervical_lordosis = self._calculate_enhanced_cervical_lordosis(landmarks)
        
        # Shoulder height difference (more accurate in sagittal view)
        shoulder_height_diff = self.angle_calc.calculate_shoulder_height_difference(
            landmarks['left_shoulder'], landmarks['right_shoulder'], image_size
        )
        
        # Enhanced head forward posture
        head_forward = self._calculate_enhanced_head_forward_posture(landmarks)
        
        # Enhanced lumbar lordosis
        lumbar_lordosis = self._calculate_enhanced_lumbar_lordosis(landmarks)
        
        # Scapular protraction
        scapular_protraction = self.angle_calc.calculate_scapular_protraction(
            landmarks['left_shoulder'], landmarks['right_shoulder'],
            landmarks['left_elbow'], landmarks['right_elbow']
        )
        
        # Trunk lateral deviation
        trunk_deviation = self.angle_calc.calculate_trunk_lateral_deviation(
            landmarks['nose'], landmarks['left_hip'], landmarks['right_hip']
        )
        
        return PostureMetrics(
            pelvic_tilt=pelvic_tilt,
            thoracic_kyphosis=thoracic_kyphosis,
            cervical_lordosis=cervical_lordosis,
            shoulder_height_difference=shoulder_height_diff,
            head_forward_posture=head_forward,
            lumbar_lordosis=lumbar_lordosis,
            scapular_protraction=scapular_protraction,
            trunk_lateral_deviation=trunk_deviation
        )
    
    def _calculate_frontal_metrics(self, landmarks: Dict, image_size: Tuple[int, int]) -> PostureMetrics:
        """Calculate metrics optimized for frontal/posterior view"""
        
        # In frontal view, focus on bilateral symmetry and alignment
        
        # Pelvic alignment (frontal view)
        pelvic_tilt = self._calculate_frontal_pelvic_alignment(landmarks)
        
        # Shoulder symmetry and elevation
        shoulder_metrics = self._calculate_frontal_shoulder_metrics(landmarks, image_size)
        
        # Spinal alignment in frontal plane
        spinal_alignment = self._calculate_frontal_spinal_alignment(landmarks)
        
        # Knee alignment (valgus/varus)
        knee_alignment = self._calculate_knee_alignment(landmarks)
        
        # Head tilt and neck alignment
        head_alignment = self._calculate_frontal_head_alignment(landmarks)
        
        return PostureMetrics(
            pelvic_tilt=pelvic_tilt,
            thoracic_kyphosis=spinal_alignment,
            cervical_lordosis=head_alignment,
            shoulder_height_difference=shoulder_metrics['height_diff'],
            head_forward_posture=head_alignment,
            lumbar_lordosis=spinal_alignment,
            scapular_protraction=shoulder_metrics['protraction'],
            trunk_lateral_deviation=spinal_alignment
        )
    
    def _calculate_combined_metrics(self, landmarks: Dict, image_size: Tuple[int, int]) -> PostureMetrics:
        """Calculate metrics for oblique or uncertain orientations"""
        
        # Use a combination of sagittal and frontal analyses
        sagittal_metrics = self._calculate_sagittal_metrics(landmarks, image_size)
        frontal_metrics = self._calculate_frontal_metrics(landmarks, image_size)
        
        # Weight the metrics based on confidence
        return PostureMetrics(
            pelvic_tilt=(sagittal_metrics.pelvic_tilt + frontal_metrics.pelvic_tilt) / 2,
            thoracic_kyphosis=sagittal_metrics.thoracic_kyphosis,
            cervical_lordosis=sagittal_metrics.cervical_lordosis,
            shoulder_height_difference=frontal_metrics.shoulder_height_difference,
            head_forward_posture=sagittal_metrics.head_forward_posture,
            lumbar_lordosis=sagittal_metrics.lumbar_lordosis,
            scapular_protraction=sagittal_metrics.scapular_protraction,
            trunk_lateral_deviation=frontal_metrics.trunk_lateral_deviation
        )
    
    def _calculate_enhanced_thoracic_kyphosis(self, landmarks: Dict) -> float:
        """Enhanced thoracic kyphosis calculation"""
        try:
            # Use more landmarks for better accuracy
            nose = landmarks.get('nose')
            left_shoulder = landmarks.get('left_shoulder')
            right_shoulder = landmarks.get('right_shoulder')
            left_hip = landmarks.get('left_hip')
            right_hip = landmarks.get('right_hip')
            
            if not all([nose, left_shoulder, right_shoulder, left_hip, right_hip]):
                return 35.0  # Default value
            
            # Calculate shoulder midpoint
            shoulder_mid = self.angle_calc.calculate_midpoint(left_shoulder, right_shoulder)
            hip_mid = self.angle_calc.calculate_midpoint(left_hip, right_hip)
            
            # Calculate the angle of the spine curve
            spine_angle = self.angle_calc.calculate_angle(
                hip_mid, shoulder_mid, nose
            )
            
            # Convert to thoracic kyphosis angle (0-60 degrees normal range)
            kyphosis = max(0, min(60, 180 - spine_angle))
            
            return kyphosis
            
        except Exception as e:
            logger.error(f"Error calculating enhanced thoracic kyphosis: {str(e)}")
            return 35.0
    
    def _calculate_enhanced_cervical_lordosis(self, landmarks: Dict) -> float:
        """Enhanced cervical lordosis calculation"""
        try:
            nose = landmarks.get('nose')
            left_ear = landmarks.get('left_ear')
            right_ear = landmarks.get('right_ear')
            left_shoulder = landmarks.get('left_shoulder')
            right_shoulder = landmarks.get('right_shoulder')
            
            if not all([nose, left_ear, right_ear, left_shoulder, right_shoulder]):
                return 25.0  # Default value
            
            ear_mid = self.angle_calc.calculate_midpoint(left_ear, right_ear)
            shoulder_mid = self.angle_calc.calculate_midpoint(left_shoulder, right_shoulder)
            
            # Calculate cervical angle
            cervical_angle = self.angle_calc.calculate_angle(
                shoulder_mid, ear_mid, nose
            )
            
            # Normal cervical lordosis is 15-35 degrees
            lordosis = max(0, min(50, cervical_angle))
            
            return lordosis
            
        except Exception as e:
            logger.error(f"Error calculating enhanced cervical lordosis: {str(e)}")
            return 25.0
    
    def _calculate_enhanced_head_forward_posture(self, landmarks: Dict) -> float:
        """Enhanced head forward posture calculation"""
        try:
            nose = landmarks.get('nose')
            left_ear = landmarks.get('left_ear')
            right_ear = landmarks.get('right_ear')
            left_shoulder = landmarks.get('left_shoulder')
            right_shoulder = landmarks.get('right_shoulder')
            
            if not all([nose, left_ear, right_ear, left_shoulder, right_shoulder]):
                return 2.0  # Default value
            
            ear_mid = self.angle_calc.calculate_midpoint(left_ear, right_ear)
            shoulder_mid = self.angle_calc.calculate_midpoint(left_shoulder, right_shoulder)
            
            # Calculate horizontal distance from ear to shoulder vertical line
            horizontal_offset = abs(ear_mid['x'] - shoulder_mid['x'])
            
            # Convert to centimeters (rough estimation)
            forward_distance = horizontal_offset * 50  # Adjusted scale factor
            
            return min(15.0, forward_distance)  # Cap at 15cm
            
        except Exception as e:
            logger.error(f"Error calculating enhanced head forward posture: {str(e)}")
            return 2.0
    
    def _calculate_enhanced_lumbar_lordosis(self, landmarks: Dict) -> float:
        """Enhanced lumbar lordosis calculation"""
        try:
            left_shoulder = landmarks.get('left_shoulder')
            right_shoulder = landmarks.get('right_shoulder')
            left_hip = landmarks.get('left_hip')
            right_hip = landmarks.get('right_hip')
            left_knee = landmarks.get('left_knee')
            right_knee = landmarks.get('right_knee')
            
            if not all([left_shoulder, right_shoulder, left_hip, right_hip]):
                return 40.0  # Default value
            
            shoulder_mid = self.angle_calc.calculate_midpoint(left_shoulder, right_shoulder)
            hip_mid = self.angle_calc.calculate_midpoint(left_hip, right_hip)
            
            # If knees are available, use them for better calculation
            if left_knee and right_knee:
                knee_mid = self.angle_calc.calculate_midpoint(left_knee, right_knee)
                lumbar_angle = self.angle_calc.calculate_angle(
                    knee_mid, hip_mid, shoulder_mid
                )
            else:
                # Fallback calculation
                lumbar_angle = 40.0
            
            # Normal lumbar lordosis is 30-50 degrees
            lordosis = max(20, min(60, lumbar_angle))
            
            return lordosis
            
        except Exception as e:
            logger.error(f"Error calculating enhanced lumbar lordosis: {str(e)}")
            return 40.0
    
    def _calculate_frontal_pelvic_alignment(self, landmarks: Dict) -> float:
        """Calculate pelvic alignment in frontal view"""
        left_hip = landmarks.get('left_hip')
        right_hip = landmarks.get('right_hip')
        
        if not all([left_hip, right_hip]):
            return 5.0
        
        # Calculate pelvic tilt in frontal plane
        height_difference = abs(left_hip['y'] - right_hip['y'])
        tilt_angle = np.arctan(height_difference / abs(left_hip['x'] - right_hip['x'])) * 180 / np.pi
        
        return min(15.0, tilt_angle)
    
    def _calculate_frontal_shoulder_metrics(self, landmarks: Dict, image_size: Tuple[int, int]) -> Dict[str, float]:
        """Calculate shoulder metrics in frontal view"""
        left_shoulder = landmarks.get('left_shoulder')
        right_shoulder = landmarks.get('right_shoulder')
        
        if not all([left_shoulder, right_shoulder]):
            return {'height_diff': 1.0, 'protraction': 2.0}
        
        # Height difference
        height_diff = self.angle_calc.calculate_shoulder_height_difference(
            left_shoulder, right_shoulder, image_size
        )
        
        # Protraction (simplified for frontal view)
        shoulder_width = abs(left_shoulder['x'] - right_shoulder['x'])
        protraction = max(0, (0.3 - shoulder_width) * 10)  # Inverse relationship
        
        return {
            'height_diff': height_diff,
            'protraction': protraction
        }
    
    def _calculate_frontal_spinal_alignment(self, landmarks: Dict) -> float:
        """Calculate spinal alignment in frontal view"""
        nose = landmarks.get('nose')
        left_shoulder = landmarks.get('left_shoulder')
        right_shoulder = landmarks.get('right_shoulder')
        left_hip = landmarks.get('left_hip')
        right_hip = landmarks.get('right_hip')
        
        if not all([nose, left_shoulder, right_shoulder, left_hip, right_hip]):
            return 2.0
        
        # Calculate midpoints
        shoulder_mid = self.angle_calc.calculate_midpoint(left_shoulder, right_shoulder)
        hip_mid = self.angle_calc.calculate_midpoint(left_hip, right_hip)
        
        # Calculate spinal deviation
        head_deviation = abs(nose['x'] - shoulder_mid['x'])
        trunk_deviation = abs(shoulder_mid['x'] - hip_mid['x'])
        
        total_deviation = (head_deviation + trunk_deviation) * 50  # Scale factor
        
        return min(10.0, total_deviation)
    
    def _calculate_knee_alignment(self, landmarks: Dict) -> float:
        """Calculate knee alignment (valgus/varus)"""
        left_hip = landmarks.get('left_hip')
        left_knee = landmarks.get('left_knee')
        left_ankle = landmarks.get('left_ankle')
        right_hip = landmarks.get('right_hip')
        right_knee = landmarks.get('right_knee')
        right_ankle = landmarks.get('right_ankle')
        
        if not all([left_hip, left_knee, left_ankle, right_hip, right_knee, right_ankle]):
            return 5.0
        
        # Calculate knee angles
        left_angle = self.angle_calc.calculate_angle(left_hip, left_knee, left_ankle)
        right_angle = self.angle_calc.calculate_angle(right_hip, right_knee, right_ankle)
        
        # Calculate deviation from straight (180 degrees)
        left_deviation = abs(180 - left_angle)
        right_deviation = abs(180 - right_angle)
        
        average_deviation = (left_deviation + right_deviation) / 2
        
        return min(20.0, average_deviation)
    
    def _calculate_frontal_head_alignment(self, landmarks: Dict) -> float:
        """Calculate head alignment in frontal view"""
        nose = landmarks.get('nose')
        left_ear = landmarks.get('left_ear')
        right_ear = landmarks.get('right_ear')
        left_shoulder = landmarks.get('left_shoulder')
        right_shoulder = landmarks.get('right_shoulder')
        
        if not all([nose, left_shoulder, right_shoulder]):
            return 2.0
        
        shoulder_mid = self.angle_calc.calculate_midpoint(left_shoulder, right_shoulder)
        
        # Calculate head tilt
        head_deviation = abs(nose['x'] - shoulder_mid['x'])
        
        # If ears are visible, use them for better calculation
        if left_ear and right_ear:
            ear_mid = self.angle_calc.calculate_midpoint(left_ear, right_ear)
            ear_deviation = abs(ear_mid['x'] - shoulder_mid['x'])
            head_deviation = (head_deviation + ear_deviation) / 2
        
        return min(8.0, head_deviation * 30)  # Scale factor
    
    def _calculate_enhanced_overall_score(self, metrics: PostureMetrics, pose_quality: float, symmetry_scores: Dict) -> float:
        """Calculate enhanced overall score with quality and symmetry weighting"""
        scores = []
        
        # Score each metric based on deviation from normal ranges
        ref_values = settings.REFERENCE_VALUES
        
        # Pelvic tilt score
        pelvic_score = self._score_metric(
            metrics.pelvic_tilt, ref_values['pelvic_tilt']['normal']
        )
        scores.append(pelvic_score * 0.15)  # 15% weight
        
        # Thoracic kyphosis score
        thoracic_score = self._score_metric(
            metrics.thoracic_kyphosis, ref_values['thoracic_kyphosis']['normal']
        )
        scores.append(thoracic_score * 0.20)  # 20% weight
        
        # Cervical lordosis score
        cervical_score = self._score_metric(
            metrics.cervical_lordosis, ref_values['cervical_lordosis']['normal']
        )
        scores.append(cervical_score * 0.15)  # 15% weight
        
        # Shoulder height score
        shoulder_score = self._score_metric(
            metrics.shoulder_height_difference, ref_values['shoulder_height_diff']['normal']
        )
        scores.append(shoulder_score * 0.15)  # 15% weight
        
        # Head forward posture score
        head_score = self._score_metric(
            metrics.head_forward_posture, ref_values['head_forward_posture']['normal']
        )
        scores.append(head_score * 0.20)  # 20% weight
        
        # Lumbar lordosis score
        lumbar_score = self._score_metric(
            metrics.lumbar_lordosis, ref_values['lumbar_lordosis']['normal']
        )
        scores.append(lumbar_score * 0.15)  # 15% weight
        
        base_score = sum(scores)
        
        # Apply pose quality weighting
        quality_weighted_score = base_score * pose_quality
        
        # Apply symmetry bonus
        symmetry_bonus = 0
        if symmetry_scores:
            avg_symmetry = sum(symmetry_scores.values()) / len(symmetry_scores)
            symmetry_bonus = avg_symmetry * 5  # Up to 5 point bonus
        
        final_score = min(100.0, max(0.0, quality_weighted_score + symmetry_bonus))
        
        logger.info(f"Score breakdown - Base: {base_score:.1f}, Quality: {pose_quality:.3f}, "
                   f"Symmetry bonus: {symmetry_bonus:.1f}, Final: {final_score:.1f}")
        
        return final_score
    
    def _calculate_posture_metrics(self, landmarks: Dict, image_size: Tuple[int, int]) -> PostureMetrics:
        """Calculate comprehensive posture metrics"""
        
        # Pelvic tilt angle
        pelvic_tilt = self.angle_calc.calculate_pelvic_tilt(
            landmarks['left_hip'], landmarks['right_hip']
        )
        
        # Thoracic kyphosis 
        thoracic_kyphosis = self.angle_calc.calculate_thoracic_kyphosis(
            landmarks['left_shoulder'], landmarks['right_shoulder'],
            landmarks['left_hip'], landmarks['right_hip']
        )
        
        # Cervical lordosis (head-neck angle)
        cervical_lordosis = self.angle_calc.calculate_cervical_lordosis(
            landmarks['nose'], landmarks['left_ear'], landmarks['right_ear'],
            landmarks['left_shoulder'], landmarks['right_shoulder']
        )
        
        # Shoulder height difference
        shoulder_height_diff = self.angle_calc.calculate_shoulder_height_difference(
            landmarks['left_shoulder'], landmarks['right_shoulder'], image_size
        )
        
        # Head forward posture
        head_forward = self.angle_calc.calculate_head_forward_posture(
            landmarks['nose'], landmarks['left_ear'], landmarks['right_ear'],
            landmarks['left_shoulder'], landmarks['right_shoulder']
        )
        
        # Lumbar lordosis
        lumbar_lordosis = self.angle_calc.calculate_lumbar_lordosis(
            landmarks['left_shoulder'], landmarks['right_shoulder'],
            landmarks['left_hip'], landmarks['right_hip']
        )
        
        # Scapular protraction
        scapular_protraction = self.angle_calc.calculate_scapular_protraction(
            landmarks['left_shoulder'], landmarks['right_shoulder'],
            landmarks['left_elbow'], landmarks['right_elbow']
        )
        
        # Trunk lateral deviation
        trunk_deviation = self.angle_calc.calculate_trunk_lateral_deviation(
            landmarks['nose'], landmarks['left_hip'], landmarks['right_hip']
        )
        
        return PostureMetrics(
            pelvic_tilt=pelvic_tilt,
            thoracic_kyphosis=thoracic_kyphosis,
            cervical_lordosis=cervical_lordosis,
            shoulder_height_difference=shoulder_height_diff,
            head_forward_posture=head_forward,
            lumbar_lordosis=lumbar_lordosis,
            scapular_protraction=scapular_protraction,
            trunk_lateral_deviation=trunk_deviation
        )
    
    def _calculate_overall_score(self, metrics: PostureMetrics) -> float:
        """Calculate overall posture score (0-100)"""
        scores = []
        
        # Score each metric based on deviation from normal ranges
        ref_values = settings.REFERENCE_VALUES
        
        # Pelvic tilt score
        pelvic_score = self._score_metric(
            metrics.pelvic_tilt, ref_values['pelvic_tilt']['normal']
        )
        scores.append(pelvic_score * 0.15)  # 15% weight
        
        # Thoracic kyphosis score
        thoracic_score = self._score_metric(
            metrics.thoracic_kyphosis, ref_values['thoracic_kyphosis']['normal']
        )
        scores.append(thoracic_score * 0.20)  # 20% weight
        
        # Cervical lordosis score
        cervical_score = self._score_metric(
            metrics.cervical_lordosis, ref_values['cervical_lordosis']['normal']
        )
        scores.append(cervical_score * 0.15)  # 15% weight
        
        # Shoulder height score
        shoulder_score = self._score_metric(
            metrics.shoulder_height_difference, ref_values['shoulder_height_diff']['normal']
        )
        scores.append(shoulder_score * 0.15)  # 15% weight
        
        # Head forward posture score
        head_score = self._score_metric(
            metrics.head_forward_posture, ref_values['head_forward_posture']['normal']
        )
        scores.append(head_score * 0.20)  # 20% weight
        
        # Lumbar lordosis score
        lumbar_score = self._score_metric(
            metrics.lumbar_lordosis, ref_values['lumbar_lordosis']['normal']
        )
        scores.append(lumbar_score * 0.15)  # 15% weight
        
        return min(100.0, max(0.0, sum(scores)))
    
    def _score_metric(self, value: float, normal_range: List[float]) -> float:
        """Score a single metric based on normal range (0-100)"""
        min_normal, max_normal = normal_range
        
        if min_normal <= value <= max_normal:
            return 100.0
        
        # Calculate deviation penalty
        if value < min_normal:
            deviation = min_normal - value
        else:
            deviation = value - max_normal
        
        # Apply exponential penalty for larger deviations
        penalty = min(100, deviation * 5)  # 5 points per degree deviation
        return max(0.0, 100.0 - penalty)
    
    def _calculate_confidence(self, pose_landmarks) -> float:
        """Calculate average visibility confidence of key landmarks"""
        key_landmarks = [11, 12, 23, 24]  # shoulders and hips
        confidences = []
        
        for idx in key_landmarks:
            if idx < len(pose_landmarks.landmark):
                confidences.append(pose_landmarks.landmark[idx].visibility)
        
        return sum(confidences) / len(confidences) if confidences else 0.0
    
    def _calculate_additional_metrics(self, landmarks: Dict) -> Dict:
        """Calculate additional metrics including knee valgus/varus and heel inclination"""
        additional_metrics = {}
        
        # 膝外反/内反角度
        if all(key in landmarks for key in ['left_hip', 'left_knee', 'left_ankle', 'right_hip', 'right_knee', 'right_ankle']):
            knee_metrics = self.angle_calc.calculate_knee_valgus_varus_enhanced(
                landmarks['left_hip'], landmarks['left_knee'], landmarks['left_ankle'],
                landmarks['right_hip'], landmarks['right_knee'], landmarks['right_ankle']
            )
            additional_metrics['knee_valgus_varus'] = knee_metrics
        
        # 踵骨傾斜
        if all(key in landmarks for key in ['left_heel', 'left_ankle', 'left_foot_index', 'right_heel', 'right_ankle', 'right_foot_index']):
            heel_metrics = self.angle_calc.calculate_heel_inclination(
                landmarks['left_heel'], landmarks['left_ankle'], landmarks['left_foot_index'],
                landmarks['right_heel'], landmarks['right_ankle'], landmarks['right_foot_index']
            )
            additional_metrics['heel_inclination'] = heel_metrics
        
        # 座位姿勢メトリクス
        seated_metrics = self.angle_calc.calculate_seated_posture_metrics(landmarks)
        if seated_metrics:
            additional_metrics['seated_metrics'] = seated_metrics
        
        return additional_metrics
    
    def _detect_seated_posture(self, landmarks: Dict) -> bool:
        """Detect if the posture is seated based on landmark positions"""
        
        # 膝と足首の可視性をチェック
        knee_visible = (
            landmarks.get('left_knee', {}).get('visibility', 0) > 0.5 and
            landmarks.get('right_knee', {}).get('visibility', 0) > 0.5
        )
        
        ankle_visible = (
            landmarks.get('left_ankle', {}).get('visibility', 0) > 0.5 and
            landmarks.get('right_ankle', {}).get('visibility', 0) > 0.5
        )
        
        # 座位では膝は見えるが足首は見えにくい場合が多い
        if knee_visible and not ankle_visible:
            return True
        
        # 膝と腰の位置関係をチェック
        if knee_visible and all(key in landmarks for key in ['left_hip', 'right_hip', 'left_knee', 'right_knee']):
            hip_y = (landmarks['left_hip']['y'] + landmarks['right_hip']['y']) / 2
            knee_y = (landmarks['left_knee']['y'] + landmarks['right_knee']['y']) / 2
            
            # 座位では膝が腰より下に位置する
            if knee_y > hip_y:
                return True
        
        return False