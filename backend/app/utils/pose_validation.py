import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class PoseValidation:
    """Validation utilities for pose landmarks and measurements"""
    
    @staticmethod
    def validate_landmarks(landmarks: Dict[str, Dict[str, float]]) -> bool:
        """Validate that required landmarks are present and have good visibility"""
        
        required_landmarks = [
            'nose', 'left_shoulder', 'right_shoulder', 
            'left_hip', 'right_hip', 'left_ear', 'right_ear'
        ]
        
        # Check if all required landmarks are present
        for landmark_name in required_landmarks:
            if landmark_name not in landmarks:
                logger.warning(f"Missing required landmark: {landmark_name}")
                return False
            
            landmark = landmarks[landmark_name]
            if landmark is None or 'visibility' not in landmark or landmark['visibility'] < 0.5:
                logger.warning(f"Invalid or low visibility for landmark: {landmark_name}")
                return False
        
        return True
    
    @staticmethod
    def check_pose_quality(landmarks: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Assess the quality of the detected pose"""
        
        quality_scores = {}
        
        # Symmetry check
        left_shoulder = landmarks.get('left_shoulder', {})
        right_shoulder = landmarks.get('right_shoulder', {})
        left_hip = landmarks.get('left_hip', {})
        right_hip = landmarks.get('right_hip', {})
        
        if all([left_shoulder, right_shoulder, left_hip, right_hip]):
            # Shoulder symmetry
            shoulder_diff = abs(left_shoulder.get('y', 0) - right_shoulder.get('y', 0))
            quality_scores['shoulder_symmetry'] = max(0, 1 - shoulder_diff * 2)
            
            # Hip symmetry
            hip_diff = abs(left_hip.get('y', 0) - right_hip.get('y', 0))
            quality_scores['hip_symmetry'] = max(0, 1 - hip_diff * 2)
        
        # Visibility scores
        total_visibility = 0
        count = 0
        for landmark_name, landmark in landmarks.items():
            if 'visibility' in landmark:
                total_visibility += landmark['visibility']
                count += 1
        
        if count > 0:
            quality_scores['average_visibility'] = total_visibility / count
        
        # Overall quality score
        if quality_scores:
            quality_scores['overall'] = sum(quality_scores.values()) / len(quality_scores)
        else:
            quality_scores['overall'] = 0.0
        
        return quality_scores
    
    @staticmethod
    def validate_angle_measurement(angle: float, 
                                 expected_range: Tuple[float, float] = (0, 180)) -> bool:
        """Validate that an angle measurement is within reasonable bounds"""
        
        min_angle, max_angle = expected_range
        
        if not (min_angle <= angle <= max_angle):
            logger.warning(f"Angle {angle} outside expected range {expected_range}")
            return False
        
        # Check for NaN or infinite values
        if np.isnan(angle) or np.isinf(angle):
            logger.warning(f"Invalid angle value: {angle}")
            return False
        
        return True
    
    @staticmethod
    def check_measurement_consistency(landmarks: Dict[str, Dict[str, float]]) -> List[str]:
        """Check for consistency issues in measurements"""
        
        issues = []
        
        # Check if person is facing the camera (front view)
        nose = landmarks.get('nose', {})
        left_ear = landmarks.get('left_ear', {})
        right_ear = landmarks.get('right_ear', {})
        
        if all([nose, left_ear, right_ear]):
            nose_x = nose.get('x', 0.5)
            left_ear_x = left_ear.get('x', 0)
            right_ear_x = right_ear.get('x', 1)
            
            # For front view, nose should be between ears
            if not (min(left_ear_x, right_ear_x) <= nose_x <= max(left_ear_x, right_ear_x)):
                issues.append("Subject may not be facing the camera directly")
        
        # Check for unrealistic body proportions
        left_shoulder = landmarks.get('left_shoulder', {})
        right_shoulder = landmarks.get('right_shoulder', {})
        left_hip = landmarks.get('left_hip', {})
        right_hip = landmarks.get('right_hip', {})
        
        if all([left_shoulder, right_shoulder, left_hip, right_hip]):
            # Shoulder width vs hip width ratio
            shoulder_width = abs(left_shoulder.get('x', 0) - right_shoulder.get('x', 1))
            hip_width = abs(left_hip.get('x', 0) - right_hip.get('x', 1))
            
            if shoulder_width > 0 and hip_width > 0:
                ratio = shoulder_width / hip_width
                if ratio < 0.7 or ratio > 1.5:
                    issues.append("Unusual shoulder to hip width ratio detected")
        
        return issues
    
    @staticmethod
    def filter_noisy_landmarks(landmarks: Dict[str, Dict[str, float]], 
                             min_visibility: float = 0.3) -> Dict[str, Dict[str, float]]:
        """Filter out landmarks with low visibility or confidence"""
        
        filtered_landmarks = {}
        
        for landmark_name, landmark in landmarks.items():
            visibility = landmark.get('visibility', 0)
            
            if visibility >= min_visibility:
                filtered_landmarks[landmark_name] = landmark
            else:
                logger.debug(f"Filtered out landmark {landmark_name} due to low visibility: {visibility}")
        
        return filtered_landmarks
    
    @staticmethod
    def estimate_body_scale(landmarks: Dict[str, Dict[str, float]]) -> Optional[float]:
        """Estimate body scale factor based on landmark distances"""
        
        # Use shoulder to hip distance as reference
        left_shoulder = landmarks.get('left_shoulder', {})
        left_hip = landmarks.get('left_hip', {})
        
        if not (left_shoulder and left_hip):
            return None
        
        shoulder_y = left_shoulder.get('y', 0)
        hip_y = left_hip.get('y', 0)
        
        torso_length = abs(shoulder_y - hip_y)
        
        # Average torso length is approximately 0.3 of total body height in normalized coordinates
        # This gives us a scale factor for age/size adjustments
        if torso_length > 0:
            return torso_length / 0.3
        
        return None
    
    @staticmethod
    def validate_measurement_set(measurements: Dict[str, float]) -> Dict[str, bool]:
        """Validate a complete set of posture measurements"""
        
        validation_results = {}
        
        # Define expected ranges for each measurement
        expected_ranges = {
            'pelvic_tilt': (0, 30),           # degrees
            'thoracic_kyphosis': (10, 60),    # degrees
            'cervical_lordosis': (0, 50),     # degrees
            'shoulder_height_difference': (0, 10),  # cm
            'head_forward_posture': (0, 15),   # cm
            'lumbar_lordosis': (10, 70),      # degrees
            'scapular_protraction': (0, 8),   # cm
            'trunk_lateral_deviation': (0, 10) # cm
        }
        
        for measurement_name, value in measurements.items():
            if measurement_name in expected_ranges:
                expected_range = expected_ranges[measurement_name]
                validation_results[measurement_name] = PoseValidation.validate_angle_measurement(
                    value, expected_range
                )
            else:
                # Unknown measurement, assume valid
                validation_results[measurement_name] = True
        
        return validation_results