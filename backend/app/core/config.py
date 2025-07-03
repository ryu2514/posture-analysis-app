from pydantic import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Posture Analysis API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5000",
        "https://posture-analysis.vercel.app"
    ]
    
    # MediaPipe Settings
    MEDIAPIPE_MODEL_COMPLEXITY: int = 1
    MEDIAPIPE_MIN_DETECTION_CONFIDENCE: float = 0.5
    MEDIAPIPE_MIN_TRACKING_CONFIDENCE: float = 0.5
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "bmp"]
    
    # Storage Settings (for production, use cloud storage)
    UPLOAD_DIR: str = "uploads"
    REPORTS_DIR: str = "reports"
    
    # Analysis Settings
    AGE_GROUPS: dict = {
        "child": {"min": 3, "max": 12, "scaling_factor": 0.8},
        "teen": {"min": 13, "max": 17, "scaling_factor": 0.9},
        "adult": {"min": 18, "max": 64, "scaling_factor": 1.0},
        "elderly": {"min": 65, "max": 90, "scaling_factor": 1.1}
    }
    
    # Reference Values for Normal Posture
    REFERENCE_VALUES: dict = {
        "pelvic_tilt": {"normal": [5, 15], "unit": "degrees"},
        "thoracic_kyphosis": {"normal": [25, 45], "unit": "degrees"},
        "cervical_lordosis": {"normal": [15, 35], "unit": "degrees"},
        "shoulder_height_diff": {"normal": [0, 1.5], "unit": "cm"},
        "head_forward_posture": {"normal": [0, 2.5], "unit": "cm"},
        "lumbar_lordosis": {"normal": [30, 50], "unit": "degrees"},
        "scapular_protraction": {"normal": [0, 2], "unit": "cm"},
        "trunk_lateral_deviation": {"normal": [0, 1], "unit": "cm"}
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Create directories if they don't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)