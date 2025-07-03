from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

class PostureMetrics(BaseModel):
    """Model for posture analysis metrics"""
    pelvic_tilt: float = Field(..., description="Pelvic tilt angle in degrees")
    thoracic_kyphosis: float = Field(..., description="Thoracic kyphosis angle in degrees") 
    cervical_lordosis: float = Field(..., description="Cervical lordosis angle in degrees")
    shoulder_height_difference: float = Field(..., description="Shoulder height difference in cm")
    head_forward_posture: float = Field(..., description="Head forward posture distance in cm")
    lumbar_lordosis: float = Field(..., description="Lumbar lordosis angle in degrees")
    scapular_protraction: float = Field(..., description="Scapular protraction distance in cm")
    trunk_lateral_deviation: float = Field(..., description="Trunk lateral deviation in cm")

class PostureAnalysisResult(BaseModel):
    """Complete posture analysis result"""
    landmarks: Dict[str, Dict[str, float]] = Field(..., description="MediaPipe pose landmarks")
    metrics: PostureMetrics = Field(..., description="Calculated posture metrics")
    overall_score: float = Field(..., ge=0, le=100, description="Overall posture score (0-100)")
    image_width: int = Field(..., description="Original image width")
    image_height: int = Field(..., description="Original image height")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence")
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PostureRecommendation(BaseModel):
    """Posture improvement recommendations"""
    category: str = Field(..., description="Exercise/stretch category")
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed description")
    difficulty: str = Field(..., description="Difficulty level: beginner/intermediate/advanced")
    duration: str = Field(..., description="Recommended duration")
    frequency: str = Field(..., description="Recommended frequency")
    image_url: Optional[str] = Field(None, description="Demonstration image URL")
    video_url: Optional[str] = Field(None, description="Demonstration video URL")

class PostureReport(BaseModel):
    """Complete posture analysis report"""
    analysis_result: PostureAnalysisResult
    recommendations: List[PostureRecommendation]
    risk_assessment: Dict[str, str] = Field(..., description="Risk levels for different body regions")
    summary: str = Field(..., description="Overall assessment summary")
    generated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserProfile(BaseModel):
    """User profile for personalized analysis"""
    user_id: str
    age: int = Field(..., ge=3, le=120)
    gender: str = Field(..., regex="^(male|female|other)$")
    height: Optional[float] = Field(None, description="Height in cm")
    weight: Optional[float] = Field(None, description="Weight in kg")
    activity_level: str = Field("moderate", regex="^(sedentary|light|moderate|active|very_active)$")
    medical_conditions: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class PostureHistory(BaseModel):
    """User's posture analysis history"""
    user_id: str
    analysis_results: List[PostureAnalysisResult]
    trend_data: Dict[str, List[float]] = Field(default_factory=dict)
    improvement_score: float = Field(0.0, description="Overall improvement score")
    last_analysis: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class ApiResponse(BaseModel):
    """Standard API response model"""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }