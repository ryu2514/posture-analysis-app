"use client"

import React, { useState, useRef, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import { Pose } from '@mediapipe/pose'
import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils'
import { PostureAnalysis, SeatedPostureMeasurements } from '@/types/posture'

interface SeatedPostureAnalysisProps {
  onAnalysisComplete: (analysis: PostureAnalysis) => void
}

// MediaPipe Poseのランドマーク接続定義
const POSE_CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 7], [0, 4], [4, 5], [5, 6], [6, 8],
  [9, 10], [11, 12], [11, 13], [13, 15], [15, 17], [15, 19], [15, 21],
  [17, 19], [12, 14], [14, 16], [16, 18], [16, 20], [16, 22], [18, 20],
  [11, 23], [12, 24], [23, 24], [23, 25], [24, 26], [25, 27], [26, 28],
  [27, 29], [28, 30], [29, 31], [30, 32], [27, 31], [28, 32]
]

export default function SeatedPostureAnalysis({ onAnalysisComplete }: SeatedPostureAnalysisProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [uploadedImage, setUploadedImage] = useState<string | null>(null)
  const [pose, setPose] = useState<Pose | null>(null)
  const [analysis, setAnalysis] = useState<PostureAnalysis | null>(null)
  const [landmarks, setLandmarks] = useState<any>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const imageRef = useRef<HTMLImageElement>(null)

  const onResults = (results: any) => {
    if (!canvasRef.current || !imageRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // キャンバスサイズを画像に合わせて設定
    canvas.width = imageRef.current.offsetWidth
    canvas.height = imageRef.current.offsetHeight

    // 画像とキャンバスのスケール計算
    const scaleX = canvas.width / results.image.width
    const scaleY = canvas.height / results.image.height

    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // ポーズランドマークを描画
    if (results.poseLandmarks) {
      setLandmarks(results.poseLandmarks)
      
      // スケールされた座標でランドマークを描画
      const scaledLandmarks = results.poseLandmarks.map((landmark: any) => ({
        x: landmark.x * scaleX,
        y: landmark.y * scaleY,
        z: landmark.z
      }))
      
      // 接続線を描画
      drawConnectors(ctx, scaledLandmarks, POSE_CONNECTIONS, {
        color: '#00FF00',
        lineWidth: 2
      })
      
      // ランドマークを描画
      drawLandmarks(ctx, scaledLandmarks, {
        color: '#FF0000',
        lineWidth: 1,
        radius: 3
      })

      // 座位姿勢専用の分析を実行
      const seatedAnalysis = analyzeSeatedPostureLive(results.poseLandmarks)
      setAnalysis(seatedAnalysis)
    }
  }

  // MediaPipe初期化
  useEffect(() => {
    const initializeMediaPipe = async () => {
      if (typeof window === 'undefined') return

      try {
        const poseInstance = new Pose({
          locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`
          }
        })

        poseInstance.setOptions({
          modelComplexity: 1,
          smoothLandmarks: true,
          enableSegmentation: false,
          smoothSegmentation: true,
          minDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5
        })

        poseInstance.onResults(onResults)
        setPose(poseInstance)

      } catch (error) {
        console.error('MediaPipe初期化エラー:', error)
      }
    }

    initializeMediaPipe()
  }, [])

  const onDrop = async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    const imageUrl = URL.createObjectURL(file)
    setUploadedImage(imageUrl)
    
    setIsAnalyzing(true)
    setAnalysis(null)
    setLandmarks(null)
    
    // 画像がロードされたらMediaPipeで解析
    const img = new Image()
    img.onload = async () => {
      if (pose) {
        await pose.send({ image: img })
      }
      setIsAnalyzing(false)
    }
    img.src = imageUrl
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png']
    },
    multiple: false
  })

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg">
        <div className="p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-800">座位姿勢解析</h2>
          <p className="text-gray-600 mt-2">
            椅子に座った状態での姿勢を分析し、デスクワークに適した姿勢改善をサポートします
          </p>
        </div>

        <div className="p-6">
          {!uploadedImage ? (
            <div 
              {...getRootProps()} 
              className={`
                border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors
                ${isDragActive 
                  ? 'border-blue-400 bg-blue-50' 
                  : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
                }
              `}
            >
              <input {...getInputProps()} />
              <div className="space-y-4">
                <div className="text-4xl">🪑</div>
                <div>
                  <p className="text-lg font-medium text-gray-700">
                    座位姿勢の写真をアップロード
                  </p>
                  <p className="text-sm text-gray-500">
                    クリックまたはドラッグ&ドロップ
                  </p>
                </div>
                <div className="text-xs text-gray-400">
                  JPG, PNG形式 / 最大10MB
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="flex justify-center">
                <div className="relative inline-block">
                  <img 
                    ref={imageRef}
                    src={uploadedImage} 
                    alt="座位姿勢画像" 
                    className="max-w-md max-h-96 object-contain rounded-lg border"
                  />
                  <canvas
                    ref={canvasRef}
                    className="absolute top-0 left-0 rounded-lg pointer-events-none"
                    style={{ width: '100%', height: '100%' }}
                  />
                </div>
              </div>

              {/* リアルタイム分析結果表示 */}
              {analysis && (
                <div className="bg-gray-50 rounded-lg p-6">
                  <h3 className="font-semibold text-gray-800 mb-4">MediaPipe座位姿勢解析結果</h3>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <h4 className="font-medium text-gray-700">姿勢測定値</h4>
                      <div className="text-sm space-y-1">
                        <p>背中の角度: <span className="font-mono text-blue-600">{analysis.measurements.backAngle?.toFixed(1)}°</span></p>
                        <p>首の前方位: <span className="font-mono text-blue-600">{analysis.measurements.neckAngle?.toFixed(1)}°</span></p>
                        <p>肩の高さ差: <span className="font-mono text-blue-600">{analysis.measurements.shoulderPosition?.height?.toFixed(1)}cm</span></p>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <h4 className="font-medium text-gray-700">総合評価</h4>
                      <div className="flex items-center space-x-2">
                        <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          analysis.score >= 80 ? 'bg-green-100 text-green-800' :
                          analysis.score >= 60 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {analysis.score}点
                        </div>
                        <span className="text-sm text-gray-600">
                          {analysis.score >= 80 ? '良好' : analysis.score >= 60 ? '要改善' : '要注意'}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 pt-4 border-t">
                    <button
                      onClick={() => {
                        if (analysis) {
                          onAnalysisComplete(analysis)
                        }
                      }}
                      className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                    >
                      📊 詳細解析結果を表示
                    </button>
                  </div>
                </div>
              )}
              
              {isAnalyzing && (
                <div className="text-center space-y-4">
                  <div className="inline-flex items-center px-4 py-2 bg-blue-100 rounded-lg">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-3"></div>
                    <span className="text-blue-800 font-medium">座位姿勢解析中...</span>
                  </div>
                  <p className="text-sm text-gray-600">
                    背中の角度、首の位置、肩の高さ、適切な椅子・机の高さを分析しています
                  </p>
                </div>
              )}
              
              <div className="flex justify-center space-x-4">
                <button
                  onClick={() => {
                    setUploadedImage(null)
                    setIsAnalyzing(false)
                    setAnalysis(null)
                    setLandmarks(null)
                  }}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  disabled={isAnalyzing}
                >
                  別の画像を選択
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="p-6 bg-gray-50 border-t">
          <h3 className="font-semibold text-gray-800 mb-4">座位姿勢撮影のポイント</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="font-medium text-gray-700 flex items-center">
                📐 撮影角度・位置
              </h4>
              <ul className="space-y-1 text-sm text-gray-600">
                <li>• 側面から撮影（真横から）</li>
                <li>• カメラは座った状態の腰の高さに設置</li>
                <li>• 頭から足まで全身が写るように</li>
                <li>• 椅子と机も一緒に写す</li>
              </ul>
            </div>

            <div className="space-y-3">
              <h4 className="font-medium text-gray-700 flex items-center">
                👔 服装・姿勢
              </h4>
              <ul className="space-y-1 text-sm text-gray-600">
                <li>• 普段の作業時の服装で</li>
                <li>• いつもの座り方で自然に</li>
                <li>• 手は膝の上または机の上に</li>
                <li>• 背景はシンプルに</li>
              </ul>
            </div>

            <div className="space-y-3">
              <h4 className="font-medium text-gray-700 flex items-center">
                ⚠️ 注意事項
              </h4>
              <ul className="space-y-1 text-sm text-gray-600">
                <li>• 撮影用に姿勢を正さない</li>
                <li>• 普段通りの自然な姿勢で</li>
                <li>• 椅子の種類や机の高さも重要な情報</li>
                <li>• 足元まで写るように撮影</li>
              </ul>
            </div>

            <div className="space-y-3">
              <h4 className="font-medium text-gray-700 flex items-center">
                📊 分析項目
              </h4>
              <ul className="space-y-1 text-sm text-gray-600">
                <li>• 背中の丸まり具合</li>
                <li>• 首・頭の前方突出</li>
                <li>• 肩の位置とバランス</li>
                <li>• 適切な椅子・机の高さ提案</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="p-6 border-t bg-blue-50">
          <div className="flex items-start space-x-3">
            <div className="text-blue-500 text-xl">💡</div>
            <div>
              <h4 className="font-medium text-blue-800 mb-2">座位姿勢改善の効果</h4>
              <p className="text-sm text-blue-700">
                デスクワークでの正しい座位姿勢は、肩こり・首こり・腰痛の軽減、集中力の向上、
                疲労軽減につながります。個人の体型に合わせた椅子と机の高さ調整も重要です。
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function analyzeSeatedPostureLive(landmarks: any[]): PostureAnalysis {
  if (landmarks.length < 33) {
    throw new Error('ランドマークが不足しています')
  }

  // 座位姿勢分析に重要なランドマーク
  const nose = landmarks[0]
  const leftEar = landmarks[7]
  const rightEar = landmarks[8]
  const leftShoulder = landmarks[11]
  const rightShoulder = landmarks[12]
  const leftHip = landmarks[23]
  const rightHip = landmarks[24]
  const leftKnee = landmarks[25]
  const rightKnee = landmarks[26]

  // 背中の丸まり角度計算（胸椎の屈曲）
  const backAngle = calculateBackRoundingAngle(leftShoulder, rightShoulder, leftHip, rightHip)
  
  // 首の前方突出角度計算
  const neckAngle = calculateNeckForwardAngle(nose, leftEar, rightEar, leftShoulder, rightShoulder)
  
  // 肩の高さ差
  const shoulderHeightDiff = Math.abs(leftShoulder.y - rightShoulder.y) * 100
  
  // 股関節角度計算（座位での適切な角度）
  const hipAngle = calculateSeatedHipAngle(leftHip, rightHip, leftKnee, rightKnee)
  
  // 総合スコア計算（座位姿勢専用）
  const score = calculateSeatedPostureScore(backAngle, neckAngle, shoulderHeightDiff, hipAngle)

  const measurements: SeatedPostureMeasurements = {
    backAngle,
    neckAngle,
    shoulderPosition: {
      height: shoulderHeightDiff,
      forward: Math.abs((leftShoulder.x + rightShoulder.x) / 2 - (leftHip.x + rightHip.x) / 2) * 100
    },
    hipPosition: {
      angle: hipAngle,
      support: 85.0 // デフォルト値
    },
    recommendedChairHeight: calculateRecommendedChairHeight(leftHip, leftKnee),
    recommendedDeskHeight: calculateRecommendedDeskHeight(leftShoulder, rightShoulder)
  }

  return {
    id: `seated_mediapipe_${Date.now()}`,
    timestamp: new Date(),
    type: 'seated',
    imageUrl: '',
    measurements: measurements as any,
    feedback: {
      overall: generateSeatedOverallFeedback(backAngle, neckAngle, shoulderHeightDiff, hipAngle),
      areas: {
        head: generateHeadFeedback(neckAngle),
        shoulders: generateShoulderFeedback(shoulderHeightDiff),
        spine: generateSpineFeedback(backAngle),
        pelvis: generatePelvisFeedback(hipAngle)
      },
      severity: score >= 70 ? 'mild' : score >= 50 ? 'moderate' : 'severe',
      futureRisk: generateSeatedRiskAssessment(score)
    },
    score,
    recommendations: generateSeatedRecommendations(backAngle, neckAngle, shoulderHeightDiff, hipAngle)
  }
}

function calculateBackRoundingAngle(leftShoulder: any, rightShoulder: any, leftHip: any, rightHip: any): number {
  // 肩の中点と腰の中点を結ぶ線の角度
  const shoulderMidX = (leftShoulder.x + rightShoulder.x) / 2
  const shoulderMidY = (leftShoulder.y + rightShoulder.y) / 2
  const hipMidX = (leftHip.x + rightHip.x) / 2
  const hipMidY = (leftHip.y + rightHip.y) / 2
  
  const deltaX = shoulderMidX - hipMidX
  const deltaY = shoulderMidY - hipMidY
  
  // 垂直線からの逸脱角度
  return Math.abs(Math.atan2(deltaX, deltaY) * (180 / Math.PI))
}

function calculateNeckForwardAngle(nose: any, leftEar: any, rightEar: any, leftShoulder: any, rightShoulder: any): number {
  const earMidX = (leftEar.x + rightEar.x) / 2
  const shoulderMidX = (leftShoulder.x + rightShoulder.x) / 2
  
  // 頭部の前方突出度
  return Math.abs((earMidX - shoulderMidX) * 100)
}

function calculateSeatedHipAngle(leftHip: any, rightHip: any, leftKnee: any, rightKnee: any): number {
  // 股関節角度の計算（座位での理想は90-110度）
  const hipMidX = (leftHip.x + rightHip.x) / 2
  const hipMidY = (leftHip.y + rightHip.y) / 2
  const kneeMidX = (leftKnee.x + rightKnee.x) / 2
  const kneeMidY = (leftKnee.y + rightKnee.y) / 2
  
  const deltaX = kneeMidX - hipMidX
  const deltaY = kneeMidY - hipMidY
  
  return Math.abs(Math.atan2(deltaY, deltaX) * (180 / Math.PI))
}

function calculateSeatedPostureScore(backAngle: number, neckAngle: number, shoulderDiff: number, hipAngle: number): number {
  let score = 100
  
  // 背中の丸まり減点
  if (backAngle > 20) score -= 25
  else if (backAngle > 10) score -= 15
  
  // 首の前方突出減点
  if (neckAngle > 5) score -= 20
  else if (neckAngle > 3) score -= 10
  
  // 肩の高さ差減点
  if (shoulderDiff > 3) score -= 15
  else if (shoulderDiff > 2) score -= 8
  
  // 股関節角度減点（90-110度が理想）
  if (hipAngle < 80 || hipAngle > 120) score -= 15
  else if (hipAngle < 85 || hipAngle > 115) score -= 8
  
  return Math.max(0, score)
}

function calculateRecommendedChairHeight(hip: any, knee: any): number {
  // 膝と腰の高さ差から推奨椅子高さを計算
  const heightDiff = Math.abs(hip.y - knee.y) * 100
  return Math.round(35 + heightDiff * 0.5) // 基準値35cm + 調整値
}

function calculateRecommendedDeskHeight(leftShoulder: any, rightShoulder: any): number {
  // 肩の高さから推奨机高さを計算
  const shoulderHeight = (leftShoulder.y + rightShoulder.y) / 2
  return Math.round(60 + shoulderHeight * 20) // 基準値60cm + 調整値
}

function generateSeatedOverallFeedback(backAngle: number, neckAngle: number, shoulderDiff: number, hipAngle: number): string {
  const issues = []
  if (backAngle > 15) issues.push('背中の丸まり')
  if (neckAngle > 4) issues.push('首の前方突出')
  if (shoulderDiff > 2.5) issues.push('肩の高さの左右差')
  if (hipAngle < 85 || hipAngle > 115) issues.push('股関節角度の不適切')
  
  if (issues.length === 0) {
    return 'MediaPipe解析により、座位姿勢は良好な状態です。'
  } else {
    return `MediaPipe解析により、${issues.join('、')}が確認されました。座位姿勢の改善をお勧めします。`
  }
}

function generateHeadFeedback(neckAngle: number): string {
  if (neckAngle > 5) return `首が${neckAngle.toFixed(1)}cm前方に突出しています。ストレートネックのリスクがあります。`
  if (neckAngle > 3) return `軽度の首の前方突出が見られます。`
  return '頭部の位置は適切です。'
}

function generateShoulderFeedback(shoulderDiff: number): string {
  if (shoulderDiff > 3) return `肩の高さに${shoulderDiff.toFixed(1)}cmの左右差があります。`
  if (shoulderDiff > 2) return `軽度の肩の高さ差が見られます。`
  return '肩のバランスは良好です。'
}

function generateSpineFeedback(backAngle: number): string {
  if (backAngle > 20) return `背中が${backAngle.toFixed(1)}度丸まっています。胸椎の過度な後弯が確認されます。`
  if (backAngle > 10) return `軽度の背中の丸まりが見られます。`
  return '背骨のアライメントは良好です。'
}

function generatePelvisFeedback(hipAngle: number): string {
  if (hipAngle < 80) return `股関節角度が${hipAngle.toFixed(1)}度と浅すぎます。`
  if (hipAngle > 120) return `股関節角度が${hipAngle.toFixed(1)}度と深すぎます。`
  if (hipAngle < 85 || hipAngle > 115) return `股関節角度が理想的な範囲から少し外れています。`
  return '股関節角度は適切です。'
}

function generateSeatedRiskAssessment(score: number): string {
  if (score >= 80) return '良好な座位姿勢を維持されています。定期的なストレッチを心がけてください。'
  if (score >= 60) return '軽度の姿勢問題があります。デスクワーク環境の見直しと定期的なエクササイズが効果的です。'
  return '座位姿勢に複数の問題があります。長時間のデスクワークにより、肩こり・首こり・腰痛のリスクが高まります。'
}

function generateSeatedRecommendations(backAngle: number, neckAngle: number, shoulderDiff: number, hipAngle: number) {
  const recommendations = []
  
  if (backAngle > 15 || neckAngle > 4) {
    recommendations.push({
      category: 'exercise',
      title: '座位姿勢改善エクササイズ',
      description: 'デスクワーク中にできる姿勢改善運動',
      priority: 'high'
    })
  }
  
  if (hipAngle < 85 || hipAngle > 115) {
    recommendations.push({
      category: 'ergonomics',
      title: '椅子の高さ調整',
      description: '股関節が90-110度になるよう椅子の高さを調整',
      priority: 'high'
    })
  }
  
  recommendations.push({
    category: 'lifestyle',
    title: 'デスクワーク環境最適化',
    description: 'MediaPipe解析に基づく個別の環境改善提案',
    priority: 'medium'
  })
  
  return recommendations
}