from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import Dict, Any
import os
import logging
from pathlib import Path

from app.services.report_generator import ReportGenerator
from app.models.posture_result import PostureAnalysisResult
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

report_generator = ReportGenerator()

@router.post("/generate")
async def generate_report(analysis_result: PostureAnalysisResult) -> Dict[str, Any]:
    """Generate a PDF report from analysis results"""
    try:
        logger.info("Generating PDF report")
        report_data = await report_generator.generate_pdf_report(analysis_result)
        
        return {
            "success": True,
            "report_id": report_data["id"],
            "filename": report_data["filename"],
            "download_url": f"/api/reports/download/{report_data['id']}",
            "message": "Report generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )

@router.get("/download/{report_id}")
async def download_report(report_id: str):
    """Download a generated report by ID"""
    try:
        # Find the report file
        report_filename = f"posture_report_{report_id}.pdf"
        report_path = Path(settings.REPORTS_DIR) / report_filename
        
        if not report_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Report not found"
            )
        
        return FileResponse(
            path=str(report_path),
            filename=report_filename,
            media_type="application/pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download report: {str(e)}"
        )

@router.get("/list")
async def list_reports() -> Dict[str, Any]:
    """List all available reports"""
    try:
        reports_dir = Path(settings.REPORTS_DIR)
        
        if not reports_dir.exists():
            return {"reports": []}
        
        reports = []
        for report_file in reports_dir.glob("posture_report_*.pdf"):
            report_id = report_file.stem.replace("posture_report_", "")
            stat = report_file.stat()
            
            reports.append({
                "id": report_id,
                "filename": report_file.name,
                "size": stat.st_size,
                "created_at": stat.st_mtime,
                "download_url": f"/api/reports/download/{report_id}"
            })
        
        # Sort by creation time (newest first)
        reports.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "reports": reports,
            "total": len(reports)
        }
        
    except Exception as e:
        logger.error(f"Error listing reports: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list reports: {str(e)}"
        )

@router.delete("/{report_id}")
async def delete_report(report_id: str) -> Dict[str, Any]:
    """Delete a report by ID"""
    try:
        report_filename = f"posture_report_{report_id}.pdf"
        report_path = Path(settings.REPORTS_DIR) / report_filename
        
        if not report_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Report not found"
            )
        
        os.remove(report_path)
        
        return {
            "success": True,
            "message": f"Report {report_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete report: {str(e)}"
        )

@router.get("/template/preview")
async def preview_report_template() -> Dict[str, Any]:
    """Preview report template structure"""
    return {
        "template": {
            "sections": [
                {
                    "name": "header",
                    "title": "姿勢分析レポート",
                    "description": "Analysis date and basic information"
                },
                {
                    "name": "score",
                    "title": "総合スコア",
                    "description": "Overall posture score with interpretation"
                },
                {
                    "name": "metrics",
                    "title": "詳細測定値",
                    "description": "Detailed metrics table with normal ranges"
                },
                {
                    "name": "chart",
                    "title": "姿勢評価チャート",
                    "description": "Radar chart visualization"
                },
                {
                    "name": "recommendations",
                    "title": "改善提案",
                    "description": "Personalized exercise recommendations"
                }
            ],
            "supported_formats": ["PDF"],
            "languages": ["Japanese", "English (planned)"]
        }
    }