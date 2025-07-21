from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import time
import os
from typing import Dict, Any

from backend.app.services.pose_analyzer import PoseAnalyzer
from backend.app.services.report_generator import ReportGenerator
from backend.app.models.posture_result import PostureAnalysisResult
from backend.app.core.config import settings
from backend.app.api import reports
from backend.app.utils.logger import get_logger
from backend.app.utils.performance_monitor import get_performance_monitor

logger = get_logger("main_api")

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

# Static files setup
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")

@app.get("/")
async def root():
    """Serve Flutter app or API info"""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    else:
        return {"message": "Posture Analysis API", "version": "1.0.0", "docs": "/docs", "frontend": "Flutter app loading..."}

# Serve static files
if os.path.exists(static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
    app.mount("/icons", StaticFiles(directory=os.path.join(static_dir, "icons")), name="icons")
    app.mount("/canvaskit", StaticFiles(directory=os.path.join(static_dir, "canvaskit")), name="canvaskit")
    
    @app.get("/flutter.js")
    async def flutter_js():
        return FileResponse(os.path.join(static_dir, "flutter.js"))
    
    @app.get("/flutter_bootstrap.js")
    async def flutter_bootstrap_js():
        return FileResponse(os.path.join(static_dir, "flutter_bootstrap.js"))
    
    @app.get("/flutter_service_worker.js")
    async def flutter_service_worker_js():
        return FileResponse(os.path.join(static_dir, "flutter_service_worker.js"))
    
    @app.get("/main.dart.js")
    async def main_dart_js():
        return FileResponse(os.path.join(static_dir, "main.dart.js"))
    
    @app.get("/manifest.json")
    async def manifest_json():
        return FileResponse(os.path.join(static_dir, "manifest.json"))
    
    @app.get("/favicon.png")
    async def favicon():
        file_path = os.path.join(static_dir, "favicon.png")
        if os.path.exists(file_path):
            return FileResponse(file_path)
        else:
            raise HTTPException(status_code=404)
    
    @app.get("/favicon.ico")
    async def favicon_ico():
        file_path = os.path.join(static_dir, "favicon.png")
        if os.path.exists(file_path):
            return FileResponse(file_path)
        else:
            raise HTTPException(status_code=404)
    
    @app.get("/icons/{icon_name}")
    async def serve_icons(icon_name: str):
        """アイコンファイルを提供"""
        icon_path = os.path.join(static_dir, "icons", icon_name)
        print(f"Looking for icon at: {icon_path}")  # デバッグ
        print(f"Static dir: {static_dir}")  # デバッグ
        print(f"Icon exists: {os.path.exists(icon_path)}")  # デバッグ
        if os.path.exists(icon_path):
            return FileResponse(icon_path)
        else:
            raise HTTPException(status_code=404, detail=f"Icon {icon_name} not found at {icon_path}")
    

pose_analyzer = PoseAnalyzer()
report_generator = ReportGenerator()
performance_monitor = get_performance_monitor()

@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の処理"""
    logger.info("🚀 姿勢分析APIサーバー起動中...")
    logger.log_system_info()
    logger.info("✅ 起動完了", 
               app_name="Posture Analysis API",
               version="1.0.0",
               allowed_origins=settings.ALLOWED_ORIGINS)


@app.get("/health")
async def health_check(request: Request):
    client_ip = request.client.host
    logger.log_api_request("/health", "GET", client_ip)
    
    response = {"status": "healthy", "mediapipe": "ready"}
    logger.log_api_response("/health", 200, 0.001)
    return response

@app.get("/api/health")
async def api_health_check(request: Request):
    client_ip = request.client.host
    logger.log_api_request("/api/health", "GET", client_ip)
    
    response = {"status": "healthy", "mediapipe": "ready"}
    logger.log_api_response("/api/health", 200, 0.001)
    return response

@app.post("/api/analyze")
async def analyze_posture(request: Request, file: UploadFile = File(...)) -> Dict[str, Any]:
    start_time = time.time()
    client_ip = request.client.host
    
    # 基本バリデーション
    if not file.content_type.startswith("image/"):
        logger.warning("無効なファイル形式", 
                      filename=file.filename,
                      content_type=file.content_type,
                      client_ip=client_ip)
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        image_data = await file.read()
        file_size = len(image_data)
        
        # APIリクエストログ
        logger.log_api_request("/analyze-posture", "POST", client_ip, file_size)
        
        # 姿勢分析実行
        analysis_timer = logger.start_timer("api_analysis")
        result = await pose_analyzer.analyze_image(image_data)
        analysis_duration = logger.end_timer(analysis_timer)
        
        if result is None:
            # 検出失敗
            response_time = time.time() - start_time
            logger.log_api_response("/analyze-posture", 422, response_time, 
                                  "Could not detect pose landmarks in the image")
            raise HTTPException(status_code=422, detail="Could not detect pose landmarks in the image")
        
        # 成功レスポンス
        response_time = time.time() - start_time
        logger.log_api_response("/analyze-posture", 200, response_time)
        logger.info("姿勢分析API成功", 
                   filename=file.filename,
                   file_size=file_size,
                   analysis_duration=analysis_duration,
                   overall_score=result.overall_score,
                   client_ip=client_ip)
        
        return result.dict()
        
    except HTTPException:
        raise  # Re-raise HTTPExceptions as-is
    except Exception as e:
        response_time = time.time() - start_time
        logger.error("姿勢分析API内部エラー", error=e, 
                    filename=file.filename,
                    client_ip=client_ip)
        logger.log_api_response("/analyze-posture", 500, response_time, str(e))
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
        "pelvic_tilt": {"normal_range": [5, 15], "unit": "degrees"},
        "thoracic_kyphosis": {"normal_range": [25, 45], "unit": "degrees"},
        "cervical_lordosis": {"normal_range": [15, 35], "unit": "degrees"},
        "shoulder_elevation": {"normal_range": [0, 1.5], "unit": "cm"},
        "head_forward": {"normal_range": [0, 2.5], "unit": "cm"},
        "lumbar_lordosis": {"normal_range": [30, 50], "unit": "degrees"},
        "knee_valgus_varus": {"normal_range": [0, 10], "unit": "degrees"},
        "heel_inclination": {"normal_range": [0, 5], "unit": "degrees"},
        "seated_metrics": {
            "seated_pelvic_tilt": {"normal_range": [0, 15], "unit": "degrees"},
            "head_neck_position": {"normal_range": [0, 5], "unit": "cm"},
            "trunk_forward_lean": {"normal_range": [0, 20], "unit": "degrees"},
            "lateral_lean": {"normal_range": [0, 10], "unit": "degrees"}
        },
        "overall_score": {"excellent": [90, 100], "good": [70, 89], "fair": [50, 69], "poor": [0, 49]},
        "color_codes": {
            "excellent": "#22c55e",
            "good": "#84cc16", 
            "fair": "#eab308",
            "poor": "#f97316",
            "critical": "#ef4444"
        }
    }

@app.get("/demo", response_class=HTMLResponse)
async def demo_page():
    """HTML demo page for posture analysis"""
    import os
    # プロジェクトルートのdemo.htmlを参照
    demo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "demo.html")
    try:
        with open(demo_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Demo page not found</h1><p>Please run: python3 create_demo_page.py</p>"

@app.get("/debug", response_class=HTMLResponse)
async def debug_page():
    """Debug page for troubleshooting"""
    import os
    debug_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "debug_demo.html")
    try:
        with open(debug_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Debug page not found</h1><p>File: debug_demo.html not found</p>"

@app.get("/fixed", response_class=HTMLResponse)
async def fixed_demo_page():
    """Fixed demo page with improved progress tracking and error handling"""
    import os
    fixed_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "fixed_demo.html")
    try:
        with open(fixed_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Fixed demo page not found</h1><p>File: fixed_demo.html not found</p>"

@app.get("/test", response_class=HTMLResponse)
async def user_test_page():
    """User acceptance testing page"""
    import os
    test_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "test-demo.html")
    try:
        with open(test_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Test page not found</h1><p>File: test-demo.html not found</p>"

@app.get("/enhanced", response_class=HTMLResponse)
async def enhanced_demo_page():
    """Enhanced demo page with performance monitoring and improved UX"""
    import os
    # コンテナ内のパスを直接指定
    enhanced_path = "/app/enhanced_demo_v2.html"
    try:
        with open(enhanced_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # フォールバック: 元のファイルを試行
        fallback_path = "/app/enhanced_demo.html"
        try:
            with open(fallback_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "<h1>Enhanced demo page not found</h1><p>File: enhanced_demo_v2.html not found</p>"

@app.get("/api/performance/summary")
async def get_performance_summary():
    """パフォーマンスサマリー取得"""
    try:
        summary = performance_monitor.get_performance_summary()
        return summary
    except Exception as e:
        logger.error("パフォーマンスサマリー取得エラー", error=e)
        raise HTTPException(status_code=500, detail=f"Performance summary failed: {str(e)}")

@app.get("/api/performance/recommendations")
async def get_performance_recommendations():
    """パフォーマンス最適化推奨事項取得"""
    try:
        recommendations = performance_monitor.get_optimization_recommendations()
        return {"recommendations": recommendations}
    except Exception as e:
        logger.error("パフォーマンス推奨事項取得エラー", error=e)
        raise HTTPException(status_code=500, detail=f"Performance recommendations failed: {str(e)}")

@app.post("/api/performance/export")
async def export_performance_data():
    """パフォーマンスデータエクスポート"""
    try:
        import os
        export_path = "/Users/kobayashiryuju/posture-analysis-app/performance_export.json"
        performance_monitor.export_performance_data(export_path)
        
        # ファイルが存在するかチェック
        if os.path.exists(export_path):
            return {"status": "success", "export_path": export_path, "message": "Performance data exported"}
        else:
            raise HTTPException(status_code=500, detail="Export file was not created")
    except Exception as e:
        logger.error("パフォーマンスデータエクスポートエラー", error=e)
        raise HTTPException(status_code=500, detail=f"Performance export failed: {str(e)}")

@app.delete("/api/performance/clear")
async def clear_performance_history():
    """パフォーマンス履歴クリア"""
    try:
        performance_monitor.clear_history()
        return {"status": "success", "message": "Performance history cleared"}
    except Exception as e:
        logger.error("パフォーマンス履歴クリアエラー", error=e)
        raise HTTPException(status_code=500, detail=f"Performance clear failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)