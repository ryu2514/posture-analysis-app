#!/usr/bin/env python3
"""
Test runner script for the Posture Analysis Application
"""

import sys
import subprocess
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and return the result"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=Path(__file__).parent
        )
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    """Main test runner function"""
    print("🚀 Starting Posture Analysis Application Tests")
    print(f"Working directory: {os.getcwd()}")
    
    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        sys.exit(1)
    
    os.chdir(backend_dir)
    print(f"Changed to backend directory: {backend_dir}")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Check Python environment
    tests_total += 1
    if run_command("python3 --version", "Python Version Check"):
        tests_passed += 1
    
    # Test 2: Install dependencies
    tests_total += 1
    if run_command("pip3 install -r requirements.txt", "Install Dependencies"):
        tests_passed += 1
    
    # Test 3: Import check - verify all modules can be imported
    tests_total += 1
    import_check = """
python3 -c "
try:
    import mediapipe as mp
    import cv2
    import numpy as np
    import fastapi
    import uvicorn
    print('✅ All core dependencies imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"
    """
    if run_command(import_check, "Import Dependencies Check"):
        tests_passed += 1
    
    # Test 4: Run unit tests
    tests_total += 1
    if run_command("python3 -m pytest app/tests/test_angle_calculator.py -v", "Angle Calculator Tests"):
        tests_passed += 1
    
    # Test 5: Run pose validation tests
    tests_total += 1
    if run_command("python3 -m pytest app/tests/test_pose_validation.py -v", "Pose Validation Tests"):
        tests_passed += 1
    
    # Test 6: Run pose analyzer tests
    tests_total += 1
    if run_command("python3 -m pytest app/tests/test_pose_analyzer.py -v", "Pose Analyzer Tests"):
        tests_passed += 1
    
    # Test 7: Run integration tests
    tests_total += 1
    if run_command("python3 -m pytest app/tests/test_integration.py -v", "Integration Tests"):
        tests_passed += 1
    
    # Test 8: Check code style
    tests_total += 1
    if run_command("python3 -m flake8 app/ --max-line-length=100 --exclude=__pycache__", "Code Style Check"):
        tests_passed += 1
    
    # Test 9: Verify API can start (quick check)
    tests_total += 1
    api_check = """
python3 -c "
from app.main import app
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.get('/')
assert response.status_code == 200
print('✅ API startup check passed')
"
    """
    if run_command(api_check, "API Startup Check"):
        tests_passed += 1
    
    # Test 10: MediaPipe basic functionality test
    tests_total += 1
    mediapipe_check = """
python3 -c "
import mediapipe as mp
import numpy as np
import cv2

# Create a simple test image
test_image = np.ones((480, 640, 3), dtype=np.uint8) * 255

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.1)

try:
    results = pose.process(test_image)
    print('✅ MediaPipe Pose initialization successful')
    pose.close()
except Exception as e:
    print(f'❌ MediaPipe error: {e}')
    exit(1)
"
    """
    if run_command(mediapipe_check, "MediaPipe Functionality Check"):
        tests_passed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("🎯 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    print(f"Success Rate: {(tests_passed/tests_total)*100:.1f}%")
    
    if tests_passed == tests_total:
        print("🎉 ALL TESTS PASSED! The posture analysis system is ready!")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)