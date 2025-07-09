import numpy as np
import math
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class PoseDetector:
    """Advanced pose detection and orientation analysis"""
    
    def __init__(self):
        self.pose_orientations = {
            'sagittal': 'side_view',      # 矢状面（横向き）
            'frontal': 'front_view',      # 前額面（正面）
            'posterior': 'back_view',     # 後面（後ろ）
            'oblique': 'oblique_view'     # 斜め
        }
    
    def detect_pose_orientation(self, landmarks: Dict) -> str:
        """
        Detect the orientation of the pose (sagittal, frontal, posterior, oblique)
        Based on shoulder and hip visibility and positioning
        """
        try:
            # Key landmarks for orientation detection
            left_shoulder = landmarks.get('left_shoulder')
            right_shoulder = landmarks.get('right_shoulder')
            left_hip = landmarks.get('left_hip')
            right_hip = landmarks.get('right_hip')
            nose = landmarks.get('nose')
            left_ear = landmarks.get('left_ear')
            right_ear = landmarks.get('right_ear')
            
            if not all([left_shoulder, right_shoulder, left_hip, right_hip]):
                return 'unknown'
            
            # Calculate visibility scores
            shoulder_visibility = (left_shoulder['visibility'] + right_shoulder['visibility']) / 2
            hip_visibility = (left_hip['visibility'] + right_hip['visibility']) / 2
            
            # Calculate shoulder width (normalized)
            shoulder_width = abs(left_shoulder['x'] - right_shoulder['x'])
            hip_width = abs(left_hip['x'] - right_hip['x'])
            
            # Calculate depth indicators
            shoulder_z_diff = abs(left_shoulder.get('z', 0) - right_shoulder.get('z', 0))
            hip_z_diff = abs(left_hip.get('z', 0) - right_hip.get('z', 0))
            
            # Ear visibility for head orientation
            ear_visibility_diff = 0
            if left_ear and right_ear:
                ear_visibility_diff = abs(left_ear['visibility'] - right_ear['visibility'])
            
            logger.info(f"Pose analysis - Shoulder width: {shoulder_width:.3f}, Hip width: {hip_width:.3f}")
            logger.info(f"Visibility - Shoulders: {shoulder_visibility:.3f}, Hips: {hip_visibility:.3f}")
            logger.info(f"Z-diff - Shoulders: {shoulder_z_diff:.3f}, Hips: {hip_z_diff:.3f}")
            
            # Decision logic based on multiple factors
            if shoulder_width < 0.1 and hip_width < 0.1:
                # Very narrow profile - likely sagittal view
                return 'sagittal'
            elif shoulder_width > 0.3 and hip_width > 0.2:
                # Wide profile - likely frontal or posterior
                if ear_visibility_diff > 0.3:
                    return 'oblique'
                else:
                    # Check if it's front or back based on nose visibility
                    if nose and nose['visibility'] > 0.7:
                        return 'frontal'
                    else:
                        return 'posterior'
            elif 0.1 <= shoulder_width <= 0.3:
                # Medium width - oblique view
                return 'oblique'
            else:
                return 'frontal'  # Default fallback
                
        except Exception as e:
            logger.error(f"Error detecting pose orientation: {str(e)}")
            return 'unknown'
    
    def calculate_pose_quality_score(self, landmarks: Dict) -> float:
        """
        Calculate overall pose quality score based on landmark visibility and positioning
        """
        try:
            key_landmarks = [
                'nose', 'left_shoulder', 'right_shoulder',
                'left_hip', 'right_hip', 'left_knee', 'right_knee'
            ]
            
            total_visibility = 0
            valid_landmarks = 0
            
            for landmark_name in key_landmarks:
                landmark = landmarks.get(landmark_name)
                if landmark:
                    total_visibility += landmark['visibility']
                    valid_landmarks += 1
            
            if valid_landmarks == 0:
                return 0.0
            
            base_score = total_visibility / valid_landmarks
            
            # Bonus for symmetry in frontal/posterior views
            left_shoulder = landmarks.get('left_shoulder')
            right_shoulder = landmarks.get('right_shoulder')
            left_hip = landmarks.get('left_hip')
            right_hip = landmarks.get('right_hip')
            
            symmetry_bonus = 0
            if all([left_shoulder, right_shoulder, left_hip, right_hip]):
                shoulder_symmetry = 1 - abs(left_shoulder['visibility'] - right_shoulder['visibility'])
                hip_symmetry = 1 - abs(left_hip['visibility'] - right_hip['visibility'])
                symmetry_bonus = (shoulder_symmetry + hip_symmetry) / 20  # Small bonus
            
            return min(1.0, base_score + symmetry_bonus)
            
        except Exception as e:
            logger.error(f"Error calculating pose quality: {str(e)}")
            return 0.0
    
    def get_orientation_specific_landmarks(self, landmarks: Dict, orientation: str) -> List[str]:
        """
        Return the most relevant landmarks for analysis based on pose orientation
        """
        base_landmarks = ['nose', 'left_shoulder', 'right_shoulder', 'left_hip', 'right_hip']
        
        orientation_landmarks = {
            'sagittal': base_landmarks + [
                'left_ear', 'right_ear', 'left_knee', 'right_knee',
                'left_ankle', 'right_ankle', 'left_elbow', 'right_elbow'
            ],
            'frontal': base_landmarks + [
                'left_eye', 'right_eye', 'left_knee', 'right_knee',
                'left_ankle', 'right_ankle', 'left_wrist', 'right_wrist'
            ],
            'posterior': base_landmarks + [
                'left_knee', 'right_knee', 'left_ankle', 'right_ankle',
                'left_elbow', 'right_elbow'
            ],
            'oblique': base_landmarks + [
                'left_ear', 'right_ear', 'left_eye', 'right_eye',
                'left_knee', 'right_knee', 'left_ankle', 'right_ankle'
            ]
        }
        
        return orientation_landmarks.get(orientation, base_landmarks)
    
    def validate_landmark_consistency(self, landmarks: Dict) -> Dict[str, bool]:
        """
        Validate landmark positions for anatomical consistency
        """
        validation_results = {}
        
        try:
            # Check head-shoulder relationship
            nose = landmarks.get('nose')
            left_shoulder = landmarks.get('left_shoulder')
            right_shoulder = landmarks.get('right_shoulder')
            
            if all([nose, left_shoulder, right_shoulder]):
                # Head should be above shoulders
                avg_shoulder_y = (left_shoulder['y'] + right_shoulder['y']) / 2
                validation_results['head_above_shoulders'] = nose['y'] < avg_shoulder_y
            
            # Check shoulder-hip relationship
            left_hip = landmarks.get('left_hip')
            right_hip = landmarks.get('right_hip')
            
            if all([left_shoulder, right_shoulder, left_hip, right_hip]):
                # Shoulders should be above hips
                avg_shoulder_y = (left_shoulder['y'] + right_shoulder['y']) / 2
                avg_hip_y = (left_hip['y'] + right_hip['y']) / 2
                validation_results['shoulders_above_hips'] = avg_shoulder_y < avg_hip_y
            
            # Check hip-knee relationship
            left_knee = landmarks.get('left_knee')
            right_knee = landmarks.get('right_knee')
            
            if all([left_hip, right_hip, left_knee, right_knee]):
                # Hips should be above knees
                avg_hip_y = (left_hip['y'] + right_hip['y']) / 2
                avg_knee_y = (left_knee['y'] + right_knee['y']) / 2
                validation_results['hips_above_knees'] = avg_hip_y < avg_knee_y
            
            # Check knee-ankle relationship
            left_ankle = landmarks.get('left_ankle')
            right_ankle = landmarks.get('right_ankle')
            
            if all([left_knee, right_knee, left_ankle, right_ankle]):
                # Knees should be above ankles
                avg_knee_y = (left_knee['y'] + right_knee['y']) / 2
                avg_ankle_y = (left_ankle['y'] + right_ankle['y']) / 2
                validation_results['knees_above_ankles'] = avg_knee_y < avg_ankle_y
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating landmarks: {str(e)}")
            return {'validation_error': False}
    
    def calculate_bilateral_symmetry(self, landmarks: Dict) -> Dict[str, float]:
        """
        Calculate bilateral symmetry scores for paired landmarks
        """
        symmetry_scores = {}
        
        pairs = [
            ('left_shoulder', 'right_shoulder'),
            ('left_hip', 'right_hip'),
            ('left_knee', 'right_knee'),
            ('left_ankle', 'right_ankle'),
            ('left_elbow', 'right_elbow'),
            ('left_wrist', 'right_wrist')
        ]
        
        try:
            for left_name, right_name in pairs:
                left_landmark = landmarks.get(left_name)
                right_landmark = landmarks.get(right_name)
                
                if left_landmark and right_landmark:
                    # Calculate height difference (y-coordinate)
                    height_diff = abs(left_landmark['y'] - right_landmark['y'])
                    
                    # Calculate visibility difference
                    visibility_diff = abs(left_landmark['visibility'] - right_landmark['visibility'])
                    
                    # Combined symmetry score (0 = perfect symmetry, 1 = maximum asymmetry)
                    symmetry_score = 1 - ((height_diff + visibility_diff) / 2)
                    symmetry_scores[f"{left_name}_{right_name}_symmetry"] = max(0, symmetry_score)
            
            return symmetry_scores
            
        except Exception as e:
            logger.error(f"Error calculating bilateral symmetry: {str(e)}")
            return {}