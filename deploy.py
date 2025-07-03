#!/usr/bin/env python3
"""
Deployment script for Posture Analysis Application
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse
import json

class PostureAnalysisDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        
    def check_prerequisites(self):
        """Check if all required tools are installed"""
        print("🔍 Checking prerequisites...")
        
        required_tools = {
            'python': 'python --version',
            'flutter': 'flutter --version',
            'docker': 'docker --version',
            'git': 'git --version'
        }
        
        missing_tools = []
        
        for tool, command in required_tools.items():
            try:
                result = subprocess.run(
                    command.split(), 
                    capture_output=True, 
                    text=True, 
                    check=True
                )
                print(f"  ✅ {tool}: Found")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"  ❌ {tool}: Not found")
                missing_tools.append(tool)
        
        if missing_tools:
            print(f"\n❌ Missing required tools: {', '.join(missing_tools)}")
            print("Please install the missing tools and try again.")
            return False
        
        print("✅ All prerequisites satisfied")
        return True
    
    def setup_backend(self):
        """Set up the backend environment"""
        print("\n🚀 Setting up backend...")
        
        # Change to backend directory
        os.chdir(self.backend_dir)
        
        # Create virtual environment if it doesn't exist
        venv_path = self.backend_dir / "venv"
        if not venv_path.exists():
            print("  📦 Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        
        # Install dependencies
        print("  📦 Installing Python dependencies...")
        pip_executable = venv_path / "bin" / "pip" if os.name != 'nt' else venv_path / "Scripts" / "pip.exe"
        subprocess.run([str(pip_executable), "install", "-r", "requirements.txt"], check=True)
        
        print("✅ Backend setup completed")
    
    def setup_frontend(self):
        """Set up the frontend environment"""
        print("\n📱 Setting up frontend...")
        
        # Change to frontend directory
        os.chdir(self.frontend_dir)
        
        # Install Flutter dependencies
        print("  📦 Installing Flutter dependencies...")
        subprocess.run(["flutter", "pub", "get"], check=True)
        
        # Generate code if needed
        print("  🔧 Running code generation...")
        try:
            subprocess.run(["flutter", "packages", "pub", "run", "build_runner", "build"], 
                         capture_output=True, check=False)
        except:
            pass  # build_runner might not be configured
        
        print("✅ Frontend setup completed")
    
    def run_tests(self):
        """Run all tests"""
        print("\n🧪 Running tests...")
        
        # Backend tests
        print("  🧪 Running backend tests...")
        os.chdir(self.backend_dir)
        
        try:
            # Activate virtual environment and run tests
            if os.name == 'nt':
                pytest_cmd = ["venv\\Scripts\\python.exe", "-m", "pytest", "app/tests/", "-v"]
            else:
                pytest_cmd = ["venv/bin/python", "-m", "pytest", "app/tests/", "-v"]
            
            result = subprocess.run(pytest_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("    ✅ Backend tests passed")
            else:
                print("    ⚠️ Some backend tests failed (continuing anyway)")
                print(f"    Output: {result.stdout}")
        except Exception as e:
            print(f"    ⚠️ Could not run backend tests: {e}")
        
        # Frontend tests
        print("  🧪 Running frontend tests...")
        os.chdir(self.frontend_dir)
        
        try:
            result = subprocess.run(["flutter", "test"], capture_output=True, text=True)
            if result.returncode == 0:
                print("    ✅ Frontend tests passed")
            else:
                print("    ⚠️ Some frontend tests failed (continuing anyway)")
        except Exception as e:
            print(f"    ⚠️ Could not run frontend tests: {e}")
        
        print("✅ Tests completed")
    
    def build_for_production(self):
        """Build the application for production"""
        print("\n🏗️ Building for production...")
        
        # Build backend (Docker image)
        print("  🐳 Building backend Docker image...")
        os.chdir(self.backend_dir)
        subprocess.run([
            "docker", "build", 
            "-t", "posture-analysis-backend:latest", 
            "."
        ], check=True)
        
        # Build frontend
        print("  📱 Building Flutter web app...")
        os.chdir(self.frontend_dir)
        subprocess.run(["flutter", "build", "web"], check=True)
        
        print("✅ Production build completed")
    
    def start_development_servers(self):
        """Start development servers"""
        print("\n🚀 Starting development servers...")
        
        # Start backend
        print("  🌐 Starting backend server...")
        backend_process = subprocess.Popen([
            "docker-compose", "up", "--build", "-d"
        ], cwd=self.project_root)
        
        print("  📱 Flutter web app can be started with: flutter run -d web")
        print("\n✅ Development environment is ready!")
        print("\n📍 URLs:")
        print("  - Backend API: http://localhost:8000")
        print("  - API Documentation: http://localhost:8000/docs")
        print("  - Frontend (after flutter run): http://localhost:3000")
    
    def create_env_file(self):
        """Create environment configuration file"""
        print("\n⚙️ Creating environment configuration...")
        
        env_content = """# Posture Analysis App Environment Configuration
# Backend Configuration
PYTHONPATH=/app
PORT=8000
HOST=0.0.0.0

# MediaPipe Configuration
MEDIAPIPE_MODEL_COMPLEXITY=1
MEDIAPIPE_MIN_DETECTION_CONFIDENCE=0.5

# File Upload Settings
MAX_FILE_SIZE=10485760
UPLOAD_DIR=uploads
REPORTS_DIR=reports

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Development Settings
DEBUG=true
LOG_LEVEL=INFO
"""
        
        env_path = self.backend_dir / ".env"
        with open(env_path, "w") as f:
            f.write(env_content)
        
        print(f"  ✅ Created {env_path}")
    
    def generate_deployment_summary(self):
        """Generate deployment summary"""
        summary = {
            "project": "Posture Analysis Application",
            "version": "1.0.0",
            "components": {
                "backend": {
                    "technology": "FastAPI + MediaPipe",
                    "port": 8000,
                    "endpoints": [
                        "/analyze-posture",
                        "/generate-report", 
                        "/metrics/reference",
                        "/health"
                    ]
                },
                "frontend": {
                    "technology": "Flutter Web",
                    "features": [
                        "Camera integration",
                        "Real-time pose analysis",
                        "Sportip Pro-inspired UI",
                        "Report generation"
                    ]
                }
            },
            "deployment": {
                "backend": "Docker container",
                "frontend": "Static web build",
                "database": "Local file storage (development)"
            }
        }
        
        summary_path = self.project_root / "deployment_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 Deployment summary saved to: {summary_path}")

def main():
    parser = argparse.ArgumentParser(description="Deploy Posture Analysis Application")
    parser.add_argument("--mode", choices=["dev", "prod"], default="dev",
                       help="Deployment mode (default: dev)")
    parser.add_argument("--skip-tests", action="store_true",
                       help="Skip running tests")
    parser.add_argument("--no-build", action="store_true",
                       help="Skip building (development only)")
    
    args = parser.parse_args()
    
    deployer = PostureAnalysisDeployer()
    
    print("🎯 Posture Analysis Application Deployment")
    print(f"Mode: {args.mode}")
    print("=" * 50)
    
    # Check prerequisites
    if not deployer.check_prerequisites():
        sys.exit(1)
    
    # Create environment file
    deployer.create_env_file()
    
    # Setup backend
    deployer.setup_backend()
    
    # Setup frontend
    deployer.setup_frontend()
    
    # Run tests (unless skipped)
    if not args.skip_tests:
        deployer.run_tests()
    
    # Build or start based on mode
    if args.mode == "prod":
        deployer.build_for_production()
        print("\n🎉 Production build completed!")
        print("Deploy the built artifacts to your production environment.")
    else:
        if not args.no_build:
            deployer.start_development_servers()
        print("\n🎉 Development environment ready!")
    
    # Generate summary
    deployer.generate_deployment_summary()
    
    print("\n✨ Deployment completed successfully!")

if __name__ == "__main__":
    main()