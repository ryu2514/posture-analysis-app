# 🚀 Deployment Guide

## 📋 Prerequisites

### GitHub Repository
- Repository: `https://github.com/ryu2514/posture-analysis-app.git`
- Branch: `main`

### Required Secrets
Configure these secrets in GitHub Settings > Secrets and variables > Actions:

1. **Docker Hub**
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Your Docker Hub password

2. **Server Access**
   - `HOST`: Server IP address or domain
   - `USERNAME`: SSH username
   - `SSH_KEY`: Private SSH key for server access
   - `PORT`: SSH port (default: 22)

## 🔧 Deployment Options

### Option 1: GitHub Actions (Recommended)
1. Push to `main` branch
2. GitHub Actions automatically:
   - Tests the code
   - Builds Docker image
   - Pushes to Docker Hub
   - Deploys to server

### Option 2: Manual Docker Deployment
```bash
# Build image
docker build -t posture-analysis:latest .

# Run container
docker run -d \
  --name posture-analysis \
  -p 8000:8000 \
  -e PYTHONPATH=/app \
  -e UVICORN_HOST=0.0.0.0 \
  -e UVICORN_PORT=8000 \
  --restart unless-stopped \
  posture-analysis:latest

# Health check
curl http://localhost:8000/health
```

### Option 3: Docker Compose (Development)
```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## 🌐 Access Points

After deployment:
- **Main App**: `http://your-server:8000/fixed`
- **API Docs**: `http://your-server:8000/docs`
- **Health Check**: `http://your-server:8000/health`

## 📊 Features

### Core Features
- MediaPipe pose analysis (33 landmarks)
- Multi-directional analysis (sagittal, frontal, posterior)
- Real-time visualization
- 8 posture metrics evaluation

### Enhanced Features v2.0
- **Color-coded judgments**: Green/Yellow/Red assessment
- **Posture type classification**: Ideal, S-curve, flat back, etc.
- **Knee valgus/varus analysis**: Q-angle calculation
- **Heel inclination measurement**: Foot alignment
- **Seated posture analysis**: Desk work posture evaluation
- **Improvement suggestions**: Personalized recommendations

## 🔍 Monitoring

### Health Checks
```bash
# Basic health
curl http://localhost:8000/health

# Performance metrics
curl http://localhost:8000/api/performance/summary
```

### Logs
```bash
# Container logs
docker logs posture-analysis

# Application logs
docker exec posture-analysis tail -f /app/logs/app.log
```

## 🛠️ Troubleshooting

### Common Issues
1. **Port already in use**: Stop existing services on port 8000
2. **MediaPipe import error**: Ensure all system dependencies are installed
3. **Memory issues**: Allocate at least 2GB RAM

### Performance Optimization
- Use SSD storage for faster image processing
- Allocate sufficient memory (2GB minimum)
- Enable GPU acceleration if available

## 🔒 Security

### Implemented Security
- HTTPS/SSL support
- CORS configuration
- File upload validation
- Rate limiting
- Security headers

### Production Recommendations
- Use reverse proxy (nginx)
- Enable SSL/TLS encryption
- Configure firewall rules
- Set up monitoring and alerting

## 📈 Scaling

### Horizontal Scaling
```bash
# Multiple instances
docker run -d --name posture-analysis-1 -p 8001:8000 posture-analysis:latest
docker run -d --name posture-analysis-2 -p 8002:8000 posture-analysis:latest

# Load balancer configuration needed
```

### Vertical Scaling
```bash
# Resource limits
docker run -d \
  --name posture-analysis \
  --memory=4g \
  --cpus=2 \
  -p 8000:8000 \
  posture-analysis:latest
```

## 🎯 Testing

### API Testing
```bash
# Health check
curl -X GET http://localhost:8000/health

# Analyze image
curl -X POST http://localhost:8000/analyze-posture \
  -F "file=@test-image.jpg"

# Get reference values
curl -X GET http://localhost:8000/metrics/reference
```

### UI Testing
1. Access: `http://localhost:8000/fixed`
2. Upload test image
3. Verify analysis results
4. Check color judgments and posture classification

## 📞 Support

### Documentation
- API Documentation: `/docs`
- Health Status: `/health`
- Performance Metrics: `/api/performance/summary`

### Troubleshooting
- Check logs: `docker logs posture-analysis`
- Verify health: `curl http://localhost:8000/health`
- Performance: `curl http://localhost:8000/api/performance/summary`

---

**Version**: 2.0  
**Last Updated**: 2024-12-07  
**Status**: Production Ready