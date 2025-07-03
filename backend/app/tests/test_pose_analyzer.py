import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from PIL import Image
import io

from app.services.pose_analyzer import PoseAnalyzer
from app.models.posture_result import PostureAnalysisResult, PostureMetrics

class TestPoseAnalyzer:
    
    def setup_method(self):
        self.analyzer = PoseAnalyzer()
    
    def create_mock_landmarks(self):
        """Create mock MediaPipe landmarks for testing"""
        landmarks = {}
        
        # Define standard landmark positions for a normal posture
        landmark_positions = {
            'nose': {'x': 0.5, 'y': 0.1, 'z': 0.0, 'visibility': 0.9},
            'left_ear': {'x': 0.45, 'y': 0.15, 'z': 0.0, 'visibility': 0.8},
            'right_ear': {'x': 0.55, 'y': 0.15, 'z': 0.0, 'visibility': 0.8},
            'left_shoulder': {'x': 0.3, 'y': 0.25, 'z': 0.0, 'visibility': 0.95},
            'right_shoulder': {'x': 0.7, 'y': 0.25, 'z': 0.0, 'visibility': 0.95},
            'left_elbow': {'x': 0.25, 'y': 0.35, 'z': 0.0, 'visibility': 0.9},
            'right_elbow': {'x': 0.75, 'y': 0.35, 'z': 0.0, 'visibility': 0.9},
            'left_hip': {'x': 0.35, 'y': 0.55, 'z': 0.0, 'visibility': 0.9},
            'right_hip': {'x': 0.65, 'y': 0.55, 'z': 0.0, 'visibility': 0.9},
            'left_knee': {'x': 0.37, 'y': 0.75, 'z': 0.0, 'visibility': 0.85},
            'right_knee': {'x': 0.63, 'y': 0.75, 'z': 0.0, 'visibility': 0.85},
            'left_ankle': {'x': 0.39, 'y': 0.9, 'z': 0.0, 'visibility': 0.8},
            'right_ankle': {'x': 0.61, 'y': 0.9, 'z': 0.0, 'visibility': 0.8},
        }
        
        return landmark_positions
    
    def create_test_image(self, width=640, height=480):
        """Create a test image for analysis"""
        # Create a simple test image
        image = Image.new('RGB', (width, height), color='white')
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()
    
    @patch('app.services.pose_analyzer.mp.solutions.pose.Pose')
    @pytest.mark.asyncio
    async def test_analyze_image_success(self, mock_pose_class):
        """Test successful image analysis"""
        # Setup mock
        mock_pose_instance = MagicMock()
        mock_pose_class.return_value = mock_pose_instance
        
        # Create mock results
        mock_landmark = MagicMock()
        mock_landmark.x = 0.5
        mock_landmark.y = 0.3
        mock_landmark.z = 0.0
        mock_landmark.visibility = 0.9
        
        mock_landmarks = MagicMock()
        mock_landmarks.landmark = [mock_landmark] * 33  # MediaPipe has 33 landmarks
        
        mock_results = MagicMock()
        mock_results.pose_landmarks = mock_landmarks
        
        mock_pose_instance.process.return_value = mock_results
        
        # Create analyzer with mocked pose
        analyzer = PoseAnalyzer()
        analyzer.pose = mock_pose_instance
        
        # Test image analysis
        test_image = self.create_test_image()
        result = await analyzer.analyze_image(test_image)
        
        # Verify result
        assert result is not None
        assert isinstance(result, PostureAnalysisResult)
        assert result.overall_score >= 0
        assert result.overall_score <= 100
        assert result.confidence >= 0
        assert result.confidence <= 1
    
    @patch('app.services.pose_analyzer.mp.solutions.pose.Pose')
    @pytest.mark.asyncio
    async def test_analyze_image_no_landmarks(self, mock_pose_class):
        """Test image analysis when no landmarks are detected"""
        # Setup mock with no landmarks
        mock_pose_instance = MagicMock()
        mock_pose_class.return_value = mock_pose_instance
        
        mock_results = MagicMock()
        mock_results.pose_landmarks = None
        
        mock_pose_instance.process.return_value = mock_results
        
        # Create analyzer with mocked pose
        analyzer = PoseAnalyzer()
        analyzer.pose = mock_pose_instance
        
        # Test image analysis
        test_image = self.create_test_image()
        result = await analyzer.analyze_image(test_image)
        
        # Should return None when no landmarks detected
        assert result is None
    
    def test_extract_landmarks(self):
        """Test landmark extraction from MediaPipe results"""
        # Create mock pose landmarks
        mock_landmark = MagicMock()
        mock_landmark.x = 0.5
        mock_landmark.y = 0.3
        mock_landmark.z = 0.0
        mock_landmark.visibility = 0.9
        
        mock_pose_landmarks = MagicMock()
        mock_pose_landmarks.landmark = [mock_landmark] * 33
        
        # Extract landmarks
        landmarks = self.analyzer._extract_landmarks(mock_pose_landmarks)
        
        # Verify extraction
        assert len(landmarks) > 0
        assert 'nose' in landmarks
        assert 'left_shoulder' in landmarks
        assert 'right_shoulder' in landmarks
        
        # Check landmark structure
        nose_landmark = landmarks['nose']
        assert 'x' in nose_landmark
        assert 'y' in nose_landmark
        assert 'z' in nose_landmark
        assert 'visibility' in nose_landmark
    
    def test_calculate_posture_metrics(self):
        """Test posture metrics calculation"""
        landmarks = self.create_mock_landmarks()
        image_size = (640, 480)
        
        metrics = self.analyzer._calculate_posture_metrics(landmarks, image_size)
        
        # Verify metrics structure
        assert isinstance(metrics, PostureMetrics)
        assert hasattr(metrics, 'pelvic_tilt')
        assert hasattr(metrics, 'thoracic_kyphosis')
        assert hasattr(metrics, 'cervical_lordosis')
        assert hasattr(metrics, 'shoulder_height_difference')
        assert hasattr(metrics, 'head_forward_posture')
        
        # Verify metrics are within reasonable ranges
        assert 0 <= metrics.pelvic_tilt <= 45
        assert 0 <= metrics.thoracic_kyphosis <= 90
        assert 0 <= metrics.cervical_lordosis <= 90
        assert metrics.shoulder_height_difference >= 0
        assert metrics.head_forward_posture >= 0
    
    def test_calculate_overall_score(self):
        """Test overall score calculation"""
        # Create metrics with good posture
        good_metrics = PostureMetrics(
            pelvic_tilt=10.0,
            thoracic_kyphosis=35.0,
            cervical_lordosis=25.0,
            shoulder_height_difference=0.5,
            head_forward_posture=1.0,
            lumbar_lordosis=40.0,
            scapular_protraction=1.0,
            trunk_lateral_deviation=0.5
        )
        
        good_score = self.analyzer._calculate_overall_score(good_metrics)
        
        # Should score well
        assert good_score >= 70
        assert good_score <= 100
        
        # Create metrics with poor posture
        poor_metrics = PostureMetrics(
            pelvic_tilt=25.0,
            thoracic_kyphosis=60.0,
            cervical_lordosis=5.0,
            shoulder_height_difference=5.0,
            head_forward_posture=8.0,
            lumbar_lordosis=70.0,
            scapular_protraction=6.0,
            trunk_lateral_deviation=4.0
        )
        
        poor_score = self.analyzer._calculate_overall_score(poor_metrics)
        
        # Should score poorly
        assert poor_score < good_score
        assert poor_score >= 0
    
    def test_score_metric(self):
        """Test individual metric scoring"""
        # Test metric within normal range
        normal_value = 12.0
        normal_range = [5.0, 15.0]
        normal_score = self.analyzer._score_metric(normal_value, normal_range)
        assert normal_score == 100.0
        
        # Test metric outside normal range (too high)
        high_value = 25.0
        high_score = self.analyzer._score_metric(high_value, normal_range)
        assert high_score < 100.0
        assert high_score >= 0.0
        
        # Test metric outside normal range (too low)
        low_value = 0.0
        low_score = self.analyzer._score_metric(low_value, normal_range)
        assert low_score < 100.0
        assert low_score >= 0.0
    
    def test_calculate_confidence(self):
        """Test confidence calculation"""
        # Create mock pose landmarks with varying visibility
        landmarks = []
        
        # Create landmarks with high visibility
        for i in range(33):
            landmark = MagicMock()
            landmark.visibility = 0.9 if i < 4 else 0.5  # Key landmarks have high visibility
            landmarks.append(landmark)
        
        mock_pose_landmarks = MagicMock()
        mock_pose_landmarks.landmark = landmarks
        
        confidence = self.analyzer._calculate_confidence(mock_pose_landmarks)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.7  # Should be high with good visibility
    
    @pytest.mark.parametrize("image_format", ['JPEG', 'PNG', 'BMP'])
    def test_different_image_formats(self, image_format):
        """Test analysis with different image formats"""
        # Create test image in different formats
        image = Image.new('RGB', (640, 480), color='white')
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image_format)
        image_data = img_byte_arr.getvalue()
        
        # Should not raise an exception
        try:
            # This would normally call MediaPipe, but we're just testing the preprocessing
            from PIL import Image
            test_image = Image.open(io.BytesIO(image_data))
            assert test_image.size == (640, 480)
        except Exception as e:
            pytest.fail(f"Failed to process {image_format} image: {e}")
    
    def test_error_handling(self):
        """Test error handling in pose analysis"""
        # Test with invalid image data
        invalid_data = b"not an image"
        
        # Should handle gracefully without crashing
        with pytest.raises(Exception):
            Image.open(io.BytesIO(invalid_data))
    
    @pytest.mark.asyncio
    async def test_analyze_image_with_corrupted_data(self):
        """Test analysis with corrupted image data"""
        corrupted_data = b"corrupted image data"
        
        result = await self.analyzer.analyze_image(corrupted_data)
        
        # Should return None for corrupted data
        assert result is None