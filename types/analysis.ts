export interface PostureAnalysis {
  score: number // 0-100 overall posture score
  metrics: {
    headForwardPosition: {
      angle: number // CVA angle in degrees
      score: number // 0-100 score for this metric
      severity: 'normal' | 'mild' | 'moderate' | 'severe'
    }
    shoulderHeight: {
      leftHeight: number // pixel position
      rightHeight: number // pixel position
      difference: number // absolute difference in pixels
      score: number // 0-100 score for this metric
      severity: 'normal' | 'mild' | 'moderate' | 'severe'
    }
    spineAlignment: {
      deviation: number // deviation from vertical in degrees
      score: number // 0-100 score for this metric
      severity: 'normal' | 'mild' | 'moderate' | 'severe'
    }
  }
  recommendations: string[]
  landmarks?: {
    [key: string]: {
      x: number
      y: number
      confidence: number
    }
  }
}

export interface AnalysisRequest {
  imageData: string // base64 encoded image
  metadata?: {
    width: number
    height: number
    format: string
  }
}

export interface AnalysisResponse {
  success: boolean
  data?: PostureAnalysis
  error?: {
    code: string
    message: string
    details?: any
  }
}

export interface Landmark {
  x: number
  y: number
  confidence: number
  name: string
}