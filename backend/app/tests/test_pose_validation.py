import pytest
import numpy as np
from backend.app.utils.pose_validation import PoseValidation

class TestPoseValidation:
    
    def create_valid_landmarks(self):
        """Create a set of valid landmarks for testing"""
        return {
            'nose': {'x': 0.5, 'y': 0.1, 'z': 0.0, 'visibility': 0.9},
            'left_ear': {'x': 0.45, 'y': 0.15, 'z': 0.0, 'visibility': 0.8},
            'right_ear': {'x': 0.55, 'y': 0.15, 'z': 0.0, 'visibility': 0.8},
            'left_shoulder': {'x': 0.3, 'y': 0.25, 'z': 0.0, 'visibility': 0.95},
            'right_shoulder': {'x': 0.7, 'y': 0.25, 'z': 0.0, 'visibility': 0.95},
            'left_hip': {'x': 0.35, 'y': 0.55, 'z': 0.0, 'visibility': 0.9},
            'right_hip': {'x': 0.65, 'y': 0.55, 'z': 0.0, 'visibility': 0.9},
        }
    
    def create_invalid_landmarks(self):
        """Create a set of invalid landmarks for testing"""
        return {
            'nose': {'x': 0.5, 'y': 0.1, 'z': 0.0, 'visibility': 0.2},  # Low visibility
            'left_shoulder': {'x': 0.3, 'y': 0.25, 'z': 0.0, 'visibility': 0.95},
            'right_shoulder': {'x': 0.7, 'y': 0.25, 'z': 0.0, 'visibility': 0.95},
            # Missing required landmarks (ears, hips)
        }
    
    def test_validate_landmarks_success(self):
        """Test landmark validation with valid landmarks"""
        landmarks = self.create_valid_landmarks()
        
        is_valid = PoseValidation.validate_landmarks(landmarks)
        
        assert is_valid is True
    
    def test_validate_landmarks_missing_required(self):
        """Test landmark validation with missing required landmarks"""
        landmarks = {
            'nose': {'x': 0.5, 'y': 0.1, 'z': 0.0, 'visibility': 0.9},
            'left_shoulder': {'x': 0.3, 'y': 0.25, 'z': 0.0, 'visibility': 0.95},
            # Missing other required landmarks
        }
        
        is_valid = PoseValidation.validate_landmarks(landmarks)
        
        assert is_valid is False
    
    def test_validate_landmarks_low_visibility(self):
        """Test landmark validation with low visibility landmarks"""
        landmarks = self.create_valid_landmarks()
        landmarks['nose']['visibility'] = 0.3  # Low visibility
        
        is_valid = PoseValidation.validate_landmarks(landmarks)
        
        assert is_valid is False
    
    def test_check_pose_quality(self):
        """Test pose quality assessment"""
        landmarks = self.create_valid_landmarks()
        
        quality_scores = PoseValidation.check_pose_quality(landmarks)
        
        # Check that quality scores are returned
        assert 'overall' in quality_scores
        assert 'shoulder_symmetry' in quality_scores
        assert 'hip_symmetry' in quality_scores
        assert 'average_visibility' in quality_scores
        
        # Check score ranges
        assert 0 <= quality_scores['overall'] <= 1
        assert 0 <= quality_scores['shoulder_symmetry'] <= 1
        assert 0 <= quality_scores['hip_symmetry'] <= 1
        assert 0 <= quality_scores['average_visibility'] <= 1
    
    def test_check_pose_quality_asymmetric(self):
        """Test pose quality with asymmetric landmarks"""
        landmarks = self.create_valid_landmarks()
        
        # Make shoulders very uneven
        landmarks['left_shoulder']['y'] = 0.15
        landmarks['right_shoulder']['y'] = 0.4
        
        quality_scores = PoseValidation.check_pose_quality(landmarks)
        
        # Shoulder symmetry should be low
        assert quality_scores['shoulder_symmetry'] <= 0.5
    
    def test_validate_angle_measurement_valid(self):
        """Test angle measurement validation with valid angles"""
        valid_angles = [0, 45, 90, 135, 180]
        
        for angle in valid_angles:
            is_valid = PoseValidation.validate_angle_measurement(angle)
            assert is_valid is True
    
    def test_validate_angle_measurement_invalid(self):
        """Test angle measurement validation with invalid angles"""
        invalid_angles = [-10, 200, float('nan'), float('inf')]
        
        for angle in invalid_angles:
            is_valid = PoseValidation.validate_angle_measurement(angle)
            assert is_valid is False
    
    def test_validate_angle_measurement_custom_range(self):
        """Test angle measurement validation with custom range"""
        angle = 30
        custom_range = (20, 40)
        
        is_valid = PoseValidation.validate_angle_measurement(angle, custom_range)
        assert is_valid is True
        
        # Test outside custom range
        invalid_angle = 50
        is_valid = PoseValidation.validate_angle_measurement(invalid_angle, custom_range)
        assert is_valid is False
    
    def test_check_measurement_consistency(self):
        """Test measurement consistency checking"""
        landmarks = self.create_valid_landmarks()
        
        issues = PoseValidation.check_measurement_consistency(landmarks)
        
        # Should return a list (may be empty for good landmarks)
        assert isinstance(issues, list)
    
    def test_check_measurement_consistency_facing_away(self):
        """Test consistency checking when subject is not facing camera"""
        landmarks = self.create_valid_landmarks()
        
        # Move nose outside ear range (not facing camera)
        landmarks['nose']['x'] = 0.8  # Outside left/right ear range
        
        issues = PoseValidation.check_measurement_consistency(landmarks)
        
        # Should detect the issue
        assert len(issues) > 0
        assert any('facing' in issue.lower() for issue in issues)
    
    def test_filter_noisy_landmarks(self):
        """Test filtering of noisy landmarks"""
        landmarks = self.create_valid_landmarks()
        
        # Add some noisy landmarks
        landmarks['noisy_landmark'] = {'x': 0.5, 'y': 0.5, 'visibility': 0.1}
        
        filtered = PoseValidation.filter_noisy_landmarks(landmarks, min_visibility=0.5)
        
        # Noisy landmark should be filtered out
        assert 'noisy_landmark' not in filtered
        assert 'nose' in filtered  # Good landmark should remain
    
    def test_estimate_body_scale(self):
        """Test body scale estimation"""
        landmarks = self.create_valid_landmarks()
        
        scale = PoseValidation.estimate_body_scale(landmarks)
        
        # Should return a positive scale factor
        assert scale is not None
        assert scale > 0
        assert 0.5 < scale < 2.0  # Reasonable range
    
    def test_estimate_body_scale_missing_landmarks(self):
        """Test body scale estimation with missing landmarks"""
        landmarks = {'nose': {'x': 0.5, 'y': 0.1}}  # Missing shoulder and hip
        
        scale = PoseValidation.estimate_body_scale(landmarks)
        
        # Should return None when required landmarks are missing
        assert scale is None
    
    def test_validate_measurement_set(self):
        """Test validation of complete measurement set"""
        measurements = {
            'pelvic_tilt': 10.0,           # Valid
            'thoracic_kyphosis': 35.0,     # Valid
            'cervical_lordosis': 25.0,     # Valid
            'shoulder_height_difference': 100.0,  # Invalid (too high)
            'head_forward_posture': 2.0,   # Valid
        }
        
        validation_results = PoseValidation.validate_measurement_set(measurements)
        
        # Check validation results
        assert validation_results['pelvic_tilt'] is True
        assert validation_results['thoracic_kyphosis'] is True
        assert validation_results['cervical_lordosis'] is True
        assert validation_results['shoulder_height_difference'] is False  # Should be invalid
        assert validation_results['head_forward_posture'] is True
    
    def test_validate_measurement_set_unknown_measurement(self):
        """Test validation with unknown measurement types"""
        measurements = {
            'unknown_measurement': 50.0,
        }
        
        validation_results = PoseValidation.validate_measurement_set(measurements)
        
        # Unknown measurements should be assumed valid
        assert validation_results['unknown_measurement'] is True
    
    @pytest.mark.parametrize("visibility,expected", [
        (0.9, True),   # High visibility
        (0.5, True),   # Medium visibility
        (0.3, False),  # Low visibility
        (0.1, False),  # Very low visibility
    ])
    def test_visibility_threshold(self, visibility, expected):
        """Test different visibility thresholds"""
        landmarks = {
            'nose': {'x': 0.5, 'y': 0.1, 'visibility': visibility},
            'left_shoulder': {'x': 0.3, 'y': 0.25, 'visibility': 0.9},
            'right_shoulder': {'x': 0.7, 'y': 0.25, 'visibility': 0.9},
            'left_hip': {'x': 0.35, 'y': 0.55, 'visibility': 0.9},
            'right_hip': {'x': 0.65, 'y': 0.55, 'visibility': 0.9},
            'left_ear': {'x': 0.45, 'y': 0.15, 'visibility': 0.9},
            'right_ear': {'x': 0.55, 'y': 0.15, 'visibility': 0.9},
        }
        
        is_valid = PoseValidation.validate_landmarks(landmarks)
        assert is_valid == expected
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Test with empty landmarks
        empty_landmarks = {}
        assert PoseValidation.validate_landmarks(empty_landmarks) is False
        
        # Test with None values
        none_landmarks = {
            'nose': None,
            'left_shoulder': {'x': 0.3, 'y': 0.25, 'visibility': 0.9},
        }
        
        # Should handle gracefully
        try:
            PoseValidation.validate_landmarks(none_landmarks)
        except Exception:
            pytest.fail("Should handle None values gracefully")
        
        # Test quality check with empty landmarks
        quality = PoseValidation.check_pose_quality({})
        assert isinstance(quality, dict)
        
        # Test scale estimation with extreme values
        extreme_landmarks = {
            'left_shoulder': {'x': 0, 'y': 0},
            'left_hip': {'x': 0, 'y': 0},  # Same position
        }
        scale = PoseValidation.estimate_body_scale(extreme_landmarks)
        # Should handle division by zero gracefully