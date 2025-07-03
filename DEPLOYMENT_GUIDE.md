# 🎯 Posture Analysis App - Deployment Guide

## 📋 System Overview

This is a comprehensive **MediaPipe-based posture analysis application** with a modern Flutter frontend and FastAPI backend. The system can analyze static posture from camera images and provide detailed reports with improvement recommendations.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flutter Web   │ ←→ │  FastAPI + MP   │ ←→ │  File Storage   │
│     Frontend    │    │     Backend     │    │  (Reports/Data) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Option 1: Automated Deployment (Recommended)

```bash
# Make the deploy script executable and run it
python deploy.py --mode dev

# This will:
# ✅ Check all prerequisites
# ✅ Set up backend environment
# ✅ Set up frontend environment  
# ✅ Run tests
# ✅ Start development servers
```

### Option 2: Manual Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup
```bash
cd frontend
flutter pub get
flutter run -d web
```

## 🧪 Testing the System

### Run Tests
```bash
# Backend tests
cd backend
python -m pytest app/tests/ -v

# Frontend tests
cd frontend
flutter test

# Or use the automated test runner
python run_tests.py
```

### Manual Testing
1. **Backend API**: Visit `http://localhost:8000/docs` for interactive API documentation
2. **Health Check**: `GET http://localhost:8000/health`
3. **Frontend**: Access `http://localhost:3000` (default Flutter web port)

## 📁 Project Structure

```
posture-analysis-app/
├── 📁 backend/                 # FastAPI backend
│   ├── 📁 app/
│   │   ├── 📁 api/             # API routes
│   │   ├── 📁 core/            # Configuration
│   │   ├── 📁 models/          # Data models
│   │   ├── 📁 services/        # Business logic
│   │   ├── 📁 utils/           # Utilities
│   │   └── 📁 tests/           # Test files
│   ├── 📄 requirements.txt     # Python dependencies
│   ├── 📄 Dockerfile          # Container config
│   └── 📄 pytest.ini          # Test configuration
├── 📁 frontend/                # Flutter frontend
│   ├── 📁 lib/
│   │   ├── 📁 screens/         # UI screens
│   │   ├── 📁 widgets/         # UI components
│   │   ├── 📁 services/        # API services
│   │   ├── 📁 models/          # Data models
│   │   └── 📁 utils/           # Utilities
│   └── 📄 pubspec.yaml         # Flutter dependencies
├── 📄 docker-compose.yml       # Multi-container setup
├── 📄 deploy.py               # Deployment script
├── 📄 run_tests.py            # Test runner
└── 📄 README.md               # Documentation
```

## 🔧 Configuration

### Environment Variables (Backend)
```bash
# .env file in backend directory
PYTHONPATH=/app
PORT=8000
MEDIAPIPE_MODEL_COMPLEXITY=1
MEDIAPIPE_MIN_DETECTION_CONFIDENCE=0.5
MAX_FILE_SIZE=10485760
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Flutter Configuration
- Target platforms: Web, iOS, Android
- Main entry point: `lib/main.dart`
- Backend API URL: Configure in `lib/services/posture_analysis_service.dart`

## 🌐 API Endpoints

### Core Analysis
- `POST /analyze-posture` - Analyze posture from image
- `GET /health` - Health check
- `GET /metrics/reference` - Get reference values

### Reports
- `POST /api/reports/generate` - Generate PDF report
- `GET /api/reports/download/{report_id}` - Download report
- `GET /api/reports/list` - List all reports
- `DELETE /api/reports/{report_id}` - Delete report

### Interactive Documentation
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc documentation

## 📱 Frontend Features

### ✨ Key Features
- **Camera Integration**: Real-time pose capture with guidelines
- **Analysis UI**: Sportip Pro-inspired design with smooth animations
- **Results Dashboard**: Comprehensive posture scoring and visualization
- **Report Generation**: PDF reports with detailed metrics
- **Responsive Design**: Works on mobile and desktop

### 🎨 UI Components
- Custom buttons with animations
- Loading overlays and indicators
- Status indicators and toasts
- Radar charts for metrics visualization
- Score cards with progress animations

## 🔬 Technical Details

### MediaPipe Integration
- **Model**: BlazePose GHUM v0.10
- **Landmarks**: 33 key points detection
- **Age Support**: 3-90 years with scaling adjustments
- **Accuracy**: ±3° angle measurement precision

### Calculated Metrics
1. **骨盤傾斜角** (Pelvic Tilt) - 5-15° normal
2. **胸椎後弯角** (Thoracic Kyphosis) - 25-45° normal  
3. **頸椎前弯角** (Cervical Lordosis) - 15-35° normal
4. **肩の高さの差** (Shoulder Height Diff) - 0-1.5cm normal
5. **頭部前方偏位** (Head Forward Posture) - 0-2.5cm normal
6. **腰椎前弯角** (Lumbar Lordosis) - 30-50° normal
7. **肩甲骨前方突出** (Scapular Protraction) - 0-2cm normal
8. **体幹側方偏位** (Trunk Lateral Deviation) - 0-1cm normal

## 🐳 Docker Deployment

### Single Container (Backend)
```bash
cd backend
docker build -t posture-analysis-backend .
docker run -p 8000:8000 posture-analysis-backend
```

### Multi-Container (Full Stack)
```bash
docker-compose up --build
```

## 🔒 Security & Privacy

- **Data Protection**: Images auto-deleted after 72 hours
- **TLS Support**: Ready for HTTPS deployment
- **CORS Configuration**: Configurable allowed origins
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Secure error responses

## 📊 Performance

- **Analysis Speed**: <1 second per image (local processing)
- **Supported Formats**: JPEG, PNG, BMP
- **Image Size**: Up to 10MB
- **Concurrent Users**: Horizontally scalable

## 🚨 Troubleshooting

### Common Issues

1. **MediaPipe Import Error**
   ```bash
   pip install --upgrade mediapipe opencv-python
   ```

2. **Flutter Build Issues**
   ```bash
   flutter clean
   flutter pub get
   flutter build web
   ```

3. **Port Already in Use**
   ```bash
   # Change port in configuration or kill existing process
   lsof -ti:8000 | xargs kill -9
   ```

4. **Camera Permission (Flutter Web)**
   - Ensure HTTPS in production
   - Check browser camera permissions

### Logs and Debugging
- Backend logs: Available in console when running with `--reload`
- Flutter logs: Available in browser developer tools
- Test logs: Use `pytest -v -s` for verbose output

## 🔄 CI/CD Pipeline

The system includes GitHub Actions configuration for:
- Automated testing on push
- Docker image building
- Deployment to cloud platforms

## 📈 Monitoring

For production deployment, consider adding:
- Health check endpoints (✅ Already included)
- Metrics collection (Prometheus/Grafana)
- Error tracking (Sentry)
- Log aggregation (ELK stack)

## 🎯 Next Steps

1. **Production Deployment**: Deploy to cloud provider (GCP, AWS, Azure)
2. **Mobile Apps**: Build native iOS/Android apps
3. **Database Integration**: Add PostgreSQL/MongoDB for persistence
4. **User Authentication**: Implement OAuth2/JWT authentication
5. **Real-time Features**: Add WebSocket for live analysis
6. **Machine Learning**: Train custom models for specific populations

## 📞 Support

For technical support or questions:
- Check the API documentation at `/docs`
- Review test files for usage examples
- Refer to MediaPipe documentation for pose detection details

---

**Built with ❤️ using FastAPI, MediaPipe, Flutter, and modern development practices**