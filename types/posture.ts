export interface PostureAnalysis {
  id: string
  timestamp: Date
  type: 'static' | 'fourDirection' | 'seated'
  imageUrl: string
  measurements: PostureMeasurements
  feedback: PostureFeedback
  score: number
  recommendations: Recommendation[]
}

export interface PostureMeasurements {
  headForwardAngle: number // CVA: 頭部前方位角度
  shoulderHeight: {
    left: number
    right: number
    difference: number
  }
  spinalAlignment: {
    cervical: number
    thoracic: number
    lumbar: number
  }
  pelvisPosition: {
    anterior: number // 前傾
    posterior: number // 後傾
    lateral: number // 側方傾斜
  }
}

export interface FourDirectionMeasurements extends PostureMeasurements {
  directions: {
    front: PostureMeasurements
    back: PostureMeasurements
    leftSide: PostureMeasurements
    rightSide: PostureMeasurements
  }
  spinalCurvature: {
    cervicalCurve: number
    thoracicKyphosis: number
    lumbarLordosis: number
  }
}

export interface SeatedPostureMeasurements {
  backAngle: number // 背中の角度
  neckAngle: number // 首の角度
  shoulderPosition: {
    height: number
    forward: number
  }
  hipPosition: {
    angle: number
    support: number
  }
  recommendedChairHeight: number
  recommendedDeskHeight: number
}

export interface PostureFeedback {
  overall: string
  areas: {
    head: string
    shoulders: string
    spine: string
    pelvis: string
  }
  severity: 'normal' | 'mild' | 'moderate' | 'severe'
  futureRisk: string
}

export interface Recommendation {
  category: 'exercise' | 'ergonomics' | 'lifestyle'
  title: string
  description: string
  exercises?: Exercise[]
  priority: 'high' | 'medium' | 'low'
}

export interface Exercise {
  name: string
  description: string
  sets: number
  reps: number
  duration?: number
  imageUrl?: string
  videoUrl?: string
}