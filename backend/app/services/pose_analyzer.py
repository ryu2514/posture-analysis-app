import mediapipe as mp
import cv2
import numpy as np
from typing import Optional, Dict, List, Tuple
import logging
from io import BytesIO
from PIL import Image

from app.models.posture_result import PostureAnalysisResult, PostureMetrics
from app.core.config import settings
from app.utils.angle_calculator import AngleCalculator

logger = logging.getLogger(__name__)

class PoseAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=settings.MEDIAPIPE_MODEL_COMPLEXITY,
            enable_segmentation=False,
            min_detection_confidence=settings.MEDIAPIPE_MIN_DETECTION_CONFIDENCE
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.angle_calc = AngleCalculator()
        
    async def analyze_image(self, image_data: bytes) -> Optional[PostureAnalysisResult]:
        try:
            # Convert bytes to image
            image = Image.open(BytesIO(image_data))
            image_rgb = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Process with MediaPipe
            results = self.pose.process(cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB))
            
            if not results.pose_landmarks:
                logger.warning("No pose landmarks detected")
                return None
            
            # Extract landmarks
            landmarks = self._extract_landmarks(results.pose_landmarks)
            
            # Calculate posture metrics
            metrics = self._calculate_posture_metrics(landmarks, image.size)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(metrics)
            
            return PostureAnalysisResult(
                landmarks=landmarks,
                metrics=metrics,
                overall_score=overall_score,
                image_width=image.size[0],
                image_height=image.size[1],
                confidence=self._calculate_confidence(results.pose_landmarks)
            )
            
        except Exception as e:
            logger.error(f"Error in pose analysis: {str(e)}")
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