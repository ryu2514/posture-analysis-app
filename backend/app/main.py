from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import logging
from typing import Dict, Any

from app.services.pose_analyzer import PoseAnalyzer
from app.services.report_generator import ReportGenerator
from app.models.posture_result import PostureAnalysisResult
from app.core.config import settings
from app.api import reports

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Posture Analysis API",
    description="MediaPipe based posture analysis system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include routers
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

pose_analyzer = PoseAnalyzer()
report_generator = ReportGenerator()

@app.get("/")
async def root():
    return {"message": "Posture Analysis API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "mediapipe": "ready"}

@app.post("/analyze-posture")
async def analyze_posture(file: UploadFile = File(...)) -> Dict[str, Any]:
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        image_data = await file.read()
        logger.info(f"Processing image: {file.filename}, size: {len(image_data)} bytes")
        
        result = await pose_analyzer.analyze_image(image_data)
        
        if not result:
            raise HTTPException(status_code=422, detail="Could not detect pose landmarks")
        
        return result.dict()
        
    except Exception as e:
        logger.error(f"Error analyzing posture: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/generate-report")
async def generate_report(analysis_result: PostureAnalysisResult):
    try:
        report_data = await report_generator.generate_pdf_report(analysis_result)
        return {"report_url": report_data["url"], "report_id": report_data["id"]}
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.get("/metrics/reference")
async def get_reference_values():
    return {
        "pelvic_tilt": {"normal_range": [-5, 15], "unit": "degrees"},
        "thoracic_kyphosis": {"normal_range": [25, 45], "unit": "degrees"},
        "cervical_lordosis": {"normal_range": [15, 35], "unit": "degrees"},
        "shoulder_elevation": {"normal_range": [-2, 2], "unit": "cm"},
        "head_forward": {"normal_range": [0, 5], "unit": "cm"},
        "overall_score": {"excellent": [90, 100], "good": [70, 89], "fair": [50, 69], "poor": [0, 49]}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)