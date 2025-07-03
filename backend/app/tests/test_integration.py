import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io
from PIL import Image
import json

from app.main import app
from app.services.pose_analyzer import PoseAnalyzer
from app.models.posture_result import PostureAnalysisResult, PostureMetrics

class TestIntegration:
    
    def setup_method(self):
        self.client = TestClient(app)
    
    def create_test_image(self, width=640, height=480, format='JPEG'):
        """Create a test image for API testing"""
        image = Image.new('RGB', (width, height), color='white')
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=format)
        img_byte_arr.seek(0)
        return img_byte_arr
    
    def create_mock_analysis_result(self):
        """Create a mock analysis result for testing"""
        landmarks = {
            'nose': {'x': 0.5, 'y': 0.1, 'z': 0.0, 'visibility': 0.9},
            'left_shoulder': {'x': 0.3, 'y': 0.25, 'z': 0.0, 'visibility': 0.95},
            'right_shoulder': {'x': 0.7, 'y': 0.25, 'z': 0.0, 'visibility': 0.95},
            'left_hip': {'x': 0.35, 'y': 0.55, 'z': 0.0, 'visibility': 0.9},
            'right_hip': {'x': 0.65, 'y': 0.55, 'z': 0.0, 'visibility': 0.9},
        }
        
        metrics = PostureMetrics(
            pelvic_tilt=10.0,
            thoracic_kyphosis=35.0,
            cervical_lordosis=25.0,
            shoulder_height_difference=1.0,
            head_forward_posture=2.0,
            lumbar_lordosis=40.0,
            scapular_protraction=1.5,
            trunk_lateral_deviation=0.5
        )
        
        return PostureAnalysisResult(
            landmarks=landmarks,
            metrics=metrics,
            overall_score=78.5,
            image_width=640,
            image_height=480,
            confidence=0.85,
            analysis_timestamp="2025-07-02T12:00:00"
        )
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = self.client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_reference_values_endpoint(self):
        """Test the reference values endpoint"""
        response = self.client.get("/metrics/reference")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that reference values are returned
        assert "pelvic_tilt" in data
        assert "thoracic_kyphosis" in data
        assert "cervical_lordosis" in data
        assert "overall_score" in data
        
        # Check structure of reference values
        pelvic_data = data["pelvic_tilt"]
        assert "normal_range" in pelvic_data
        assert "unit" in pelvic_data
        assert len(pelvic_data["normal_range"]) == 2
    
    @patch('app.services.pose_analyzer.PoseAnalyzer.analyze_image')
    def test_analyze_posture_success(self, mock_analyze):
        """Test successful posture analysis via API"""
        # Setup mock
        mock_result = self.create_mock_analysis_result()
        mock_analyze.return_value = mock_result
        
        # Create test image
        test_image = self.create_test_image()
        
        # Make API request
        response = self.client.post(
            "/analyze-posture",
            files={"file": ("test.jpg", test_image, "image/jpeg")}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "landmarks" in data
        assert "metrics" in data
        assert "overall_score" in data
        assert "confidence" in data
        
        # Verify data values
        assert data["overall_score"] == 78.5
        assert data["confidence"] == 0.85
        assert data["image_width"] == 640
        assert data["image_height"] == 480
    
    def test_analyze_posture_invalid_file_type(self):
        """Test posture analysis with invalid file type"""
        # Create a text file instead of image
        text_data = io.BytesIO(b"This is not an image")
        
        response = self.client.post(
            "/analyze-posture",
            files={"file": ("test.txt", text_data, "text/plain")}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "image" in data["detail"].lower()
    
    @patch('app.services.pose_analyzer.PoseAnalyzer.analyze_image')
    def test_analyze_posture_no_landmarks(self, mock_analyze):
        """Test posture analysis when no landmarks are detected"""
        # Setup mock to return None (no landmarks detected)
        mock_analyze.return_value = None
        
        test_image = self.create_test_image()
        
        response = self.client.post(
            "/analyze-posture",
            files={"file": ("test.jpg", test_image, "image/jpeg")}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert "pose landmarks" in data["detail"].lower()
    
    @patch('app.services.report_generator.ReportGenerator.generate_pdf_report')
    def test_generate_report_success(self, mock_generate):
        """Test successful report generation"""
        # Setup mock
        mock_generate.return_value = {
            "id": "test-report-123",
            "filename": "posture_report_test-report-123.pdf",
            "url": "/reports/posture_report_test-report-123.pdf"
        }
        
        # Create test analysis result
        analysis_result = self.create_mock_analysis_result()
        
        response = self.client.post(
            "/generate-report",
            json=analysis_result.dict()
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "report_url" in data
        assert "report_id" in data
        assert data["report_id"] == "test-report-123"
    
    def test_analyze_posture_missing_file(self):
        """Test posture analysis without uploading a file"""
        response = self.client.post("/analyze-posture")
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.parametrize("image_format", ["JPEG", "PNG"])
    def test_analyze_posture_different_formats(self, image_format):
        """Test posture analysis with different image formats"""
        with patch('app.services.pose_analyzer.PoseAnalyzer.analyze_image') as mock_analyze:
            mock_analyze.return_value = self.create_mock_analysis_result()
            
            test_image = self.create_test_image(format=image_format)
            mime_type = f"image/{image_format.lower()}"
            
            response = self.client.post(
                "/analyze-posture",
                files={"file": (f"test.{image_format.lower()}", test_image, mime_type)}
            )
            
            assert response.status_code == 200
    
    @patch('app.services.pose_analyzer.PoseAnalyzer.analyze_image')
    def test_analyze_posture_large_image(self, mock_analyze):
        """Test posture analysis with large image"""
        mock_analyze.return_value = self.create_mock_analysis_result()
        
        # Create a larger test image
        large_image = self.create_test_image(width=1920, height=1080)
        
        response = self.client.post(
            "/analyze-posture",
            files={"file": ("large_test.jpg", large_image, "image/jpeg")}
        )
        
        assert response.status_code == 200
    
    def test_cors_headers(self):
        """Test that CORS headers are properly set"""
        response = self.client.options("/analyze-posture")
        
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
    
    @patch('app.services.pose_analyzer.PoseAnalyzer.analyze_image')
    def test_concurrent_analysis_requests(self, mock_analyze):
        """Test handling multiple concurrent analysis requests"""
        mock_analyze.return_value = self.create_mock_analysis_result()
        
        # Create multiple test images
        test_images = [self.create_test_image() for _ in range(3)]
        
        # Make concurrent requests
        responses = []
        for i, image in enumerate(test_images):
            response = self.client.post(
                "/analyze-posture",
                files={"file": (f"test_{i}.jpg", image, "image/jpeg")}
            )
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
    
    def test_error_handling_invalid_json(self):
        """Test error handling with invalid JSON in report generation"""
        invalid_json = {"invalid": "data structure"}
        
        response = self.client.post(
            "/generate-report",
            json=invalid_json
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    @patch('app.services.pose_analyzer.PoseAnalyzer.analyze_image')
    def test_analysis_result_structure(self, mock_analyze):
        """Test that analysis result has correct structure"""
        mock_analyze.return_value = self.create_mock_analysis_result()
        
        test_image = self.create_test_image()
        
        response = self.client.post(
            "/analyze-posture",
            files={"file": ("test.jpg", test_image, "image/jpeg")}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check landmarks structure
        assert "landmarks" in data
        landmarks = data["landmarks"]
        assert "nose" in landmarks
        assert "left_shoulder" in landmarks
        
        # Check landmark point structure
        nose_data = landmarks["nose"]
        assert "x" in nose_data
        assert "y" in nose_data
        assert "z" in nose_data
        assert "visibility" in nose_data
        
        # Check metrics structure
        assert "metrics" in data
        metrics = data["metrics"]
        required_metrics = [
            "pelvic_tilt", "thoracic_kyphosis", "cervical_lordosis",
            "shoulder_height_difference", "head_forward_posture"
        ]
        for metric in required_metrics:
            assert metric in metrics
            assert isinstance(metrics[metric], (int, float))
    
    def test_api_versioning(self):
        """Test API versioning and backwards compatibility"""
        # Current version should work
        response = self.client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "version" in data
        assert data["version"] == "1.0.0"
    
    @patch('app.services.pose_analyzer.PoseAnalyzer.analyze_image')
    def test_response_time_performance(self, mock_analyze):
        """Test that API responds within reasonable time"""
        import time
        
        mock_analyze.return_value = self.create_mock_analysis_result()
        
        test_image = self.create_test_image()
        
        start_time = time.time()
        response = self.client.post(
            "/analyze-posture",
            files={"file": ("test.jpg", test_image, "image/jpeg")}
        )
        end_time = time.time()
        
        assert response.status_code == 200
        
        # Should respond within 2 seconds (excluding actual MediaPipe processing)
        response_time = end_time - start_time
        assert response_time < 2.0