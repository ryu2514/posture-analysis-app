import pytest
import math
from backend.app.utils.angle_calculator import AngleCalculator

class TestAngleCalculator:
    
    def setup_method(self):
        self.calc = AngleCalculator()
    
    def test_calculate_angle_90_degrees(self):
        """Test angle calculation for a perfect 90-degree angle"""
        point1 = {'x': 0, 'y': 1}  # Top
        point2 = {'x': 0, 'y': 0}  # Center
        point3 = {'x': 1, 'y': 0}  # Right
        
        angle = self.calc.calculate_angle(point1, point2, point3)
        assert abs(angle - 90.0) < 0.1
    
    def test_calculate_angle_180_degrees(self):
        """Test angle calculation for a straight line (180 degrees)"""
        point1 = {'x': -1, 'y': 0}  # Left
        point2 = {'x': 0, 'y': 0}   # Center
        point3 = {'x': 1, 'y': 0}   # Right
        
        angle = self.calc.calculate_angle(point1, point2, point3)
        assert abs(angle - 180.0) < 0.1
    
    def test_calculate_distance(self):
        """Test distance calculation between two points"""
        point1 = {'x': 0, 'y': 0}
        point2 = {'x': 3, 'y': 4}
        
        distance = self.calc.calculate_distance(point1, point2)
        assert abs(distance - 5.0) < 0.01  # 3-4-5 triangle
    
    def test_calculate_midpoint(self):
        """Test midpoint calculation"""
        point1 = {'x': 0, 'y': 0}
        point2 = {'x': 4, 'y': 6}
        
        midpoint = self.calc.calculate_midpoint(point1, point2)
        assert midpoint['x'] == 2
        assert midpoint['y'] == 3
    
    def test_pelvic_tilt_calculation(self):
        """Test pelvic tilt angle calculation"""
        # Simulate level hips
        left_hip = {'x': 0.3, 'y': 0.5}
        right_hip = {'x': 0.7, 'y': 0.5}
        
        tilt = self.calc.calculate_pelvic_tilt(left_hip, right_hip)
        assert abs(tilt) < 1.0  # Should be nearly zero for level hips
        
        # Simulate tilted hips
        left_hip_tilted = {'x': 0.3, 'y': 0.45}
        right_hip_tilted = {'x': 0.7, 'y': 0.55}
        
        tilt_tilted = self.calc.calculate_pelvic_tilt(left_hip_tilted, right_hip_tilted)
        assert tilt_tilted > 1.0  # Should show measurable tilt
    
    def test_thoracic_kyphosis_calculation(self):
        """Test thoracic kyphosis calculation"""
        # Simulate normal posture
        left_shoulder = {'x': 0.3, 'y': 0.25}
        right_shoulder = {'x': 0.7, 'y': 0.25}
        left_hip = {'x': 0.35, 'y': 0.55}
        right_hip = {'x': 0.65, 'y': 0.55}
        
        kyphosis = self.calc.calculate_thoracic_kyphosis(
            left_shoulder, right_shoulder, left_hip, right_hip
        )
        
        assert 0 <= kyphosis <= 60  # Reasonable range for kyphosis
    
    def test_cervical_lordosis_calculation(self):
        """Test cervical lordosis calculation"""
        nose = {'x': 0.5, 'y': 0.1}
        left_ear = {'x': 0.45, 'y': 0.15}
        right_ear = {'x': 0.55, 'y': 0.15}
        left_shoulder = {'x': 0.3, 'y': 0.25}
        right_shoulder = {'x': 0.7, 'y': 0.25}
        
        lordosis = self.calc.calculate_cervical_lordosis(
            nose, left_ear, right_ear, left_shoulder, right_shoulder
        )
        
        assert 0 <= lordosis <= 180  # Valid angle range
    
    def test_shoulder_height_difference(self):
        """Test shoulder height difference calculation"""
        # Level shoulders
        left_shoulder = {'x': 0.3, 'y': 0.25}
        right_shoulder = {'x': 0.7, 'y': 0.25}
        image_size = (1920, 1080)
        
        diff = self.calc.calculate_shoulder_height_difference(
            left_shoulder, right_shoulder, image_size
        )
        assert abs(diff) < 0.5  # Should be minimal for level shoulders
        
        # Uneven shoulders
        left_shoulder_high = {'x': 0.3, 'y': 0.23}
        right_shoulder_low = {'x': 0.7, 'y': 0.27}
        
        diff_uneven = self.calc.calculate_shoulder_height_difference(
            left_shoulder_high, right_shoulder_low, image_size
        )
        assert diff_uneven > 0.5  # Should show measurable difference
    
    def test_head_forward_posture(self):
        """Test head forward posture calculation"""
        # Normal alignment
        nose = {'x': 0.5, 'y': 0.1}
        left_ear = {'x': 0.48, 'y': 0.15}
        right_ear = {'x': 0.52, 'y': 0.15}
        left_shoulder = {'x': 0.3, 'y': 0.25}
        right_shoulder = {'x': 0.7, 'y': 0.25}
        
        forward_distance = self.calc.calculate_head_forward_posture(
            nose, left_ear, right_ear, left_shoulder, right_shoulder
        )
        
        assert forward_distance >= 0  # Should be non-negative
        assert forward_distance < 50   # Reasonable upper bound in cm
    
    def test_knee_valgus_varus(self):
        """Test knee angle calculations"""
        # Simulate normal leg alignment
        left_hip = {'x': 0.35, 'y': 0.55}
        left_knee = {'x': 0.37, 'y': 0.70}
        left_ankle = {'x': 0.39, 'y': 0.85}
        
        right_hip = {'x': 0.65, 'y': 0.55}
        right_knee = {'x': 0.63, 'y': 0.70}
        right_ankle = {'x': 0.61, 'y': 0.85}
        
        angles = self.calc.calculate_knee_valgus_varus(
            left_hip, left_knee, left_ankle,
            right_hip, right_knee, right_ankle
        )
        
        assert 'left_knee_angle' in angles
        assert 'right_knee_angle' in angles
        assert 0 <= angles['left_knee_angle'] <= 45
        assert 0 <= angles['right_knee_angle'] <= 45
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Test with identical points (should handle division by zero)
        point = {'x': 0.5, 'y': 0.5}
        
        angle = self.calc.calculate_angle(point, point, point)
        assert not math.isnan(angle)
        
        distance = self.calc.calculate_distance(point, point)
        assert distance == 0
        
        midpoint = self.calc.calculate_midpoint(point, point)
        assert midpoint['x'] == point['x']
        assert midpoint['y'] == point['y']
    
    def test_coordinate_ranges(self):
        """Test calculations with coordinates outside normal range"""
        # Test with coordinates outside [0,1] range
        point1 = {'x': -0.5, 'y': 1.5}
        point2 = {'x': 0.5, 'y': 0.5}
        point3 = {'x': 1.5, 'y': -0.5}
        
        # Should still calculate without errors
        angle = self.calc.calculate_angle(point1, point2, point3)
        assert not math.isnan(angle)
        assert 0 <= angle <= 180
    
    @pytest.mark.parametrize("left_hip,right_hip,expected_range", [
        ({'x': 0.3, 'y': 0.5}, {'x': 0.7, 'y': 0.5}, (0, 2)),      # Level hips
        ({'x': 0.3, 'y': 0.4}, {'x': 0.7, 'y': 0.6}, (20, 35)),    # Tilted hips
        ({'x': 0.3, 'y': 0.6}, {'x': 0.7, 'y': 0.4}, (20, 35)),    # Opposite tilt
    ])
    def test_pelvic_tilt_scenarios(self, left_hip, right_hip, expected_range):
        """Test pelvic tilt calculation with various scenarios"""
        tilt = self.calc.calculate_pelvic_tilt(left_hip, right_hip)
        assert expected_range[0] <= tilt <= expected_range[1]