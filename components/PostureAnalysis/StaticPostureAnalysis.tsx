"use client"

import React, { useState, useRef, useEffect } from 'react'
import { classifyKendall } from '@/lib/kendall'
import { useDropzone } from 'react-dropzone'
import { Pose } from '@mediapipe/pose'
import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils'
import { PostureAnalysis, PostureMeasurements, PostureFeedback } from '@/types/posture'

interface StaticPostureAnalysisProps {
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

export default function StaticPostureAnalysis({ onAnalysisComplete }: StaticPostureAnalysisProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [uploadedImage, setUploadedImage] = useState<string | null>(null)
  const [pose, setPose] = useState<Pose | null>(null)
  const [analysisComplete, setAnalysisComplete] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<PostureAnalysis | null>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const imageRef = useRef<HTMLImageElement>(null)

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
        console.log('MediaPipe initialized successfully')

      } catch (error) {
        console.error('MediaPipe初期化エラー:', error)
      }
    }

    initializeMediaPipe()
  }, [])

  const onResults = (results: any) => {
    console.log('MediaPipe onResults called:', results)
    
    if (!canvasRef.current || !imageRef.current) {
      console.log('Canvas or image ref not available')
      return
    }

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) {
      console.log('Canvas context not available')
      return
    }

    // 画像の表示サイズを取得
    const imageElement = imageRef.current
    const displayWidth = imageElement.offsetWidth
    const displayHeight = imageElement.offsetHeight
    
    console.log('Display size:', displayWidth, 'x', displayHeight)
    console.log('Pose landmarks detected:', !!results.poseLandmarks)
    console.log('Canvas element:', canvas)
    
    // キャンバスサイズを表示サイズに合わせる
    canvas.width = displayWidth
    canvas.height = displayHeight
    
    // 重要：Canvasを画像と同じサイズ・位置に設定
    console.log('Setting canvas overlay position')
    
    canvas.style.width = `${displayWidth}px`
    canvas.style.height = `${displayHeight}px`
    canvas.style.position = 'absolute'  // fixed → absolute に変更
    canvas.style.top = '0px'            // 親要素(relative)基準で配置
    canvas.style.left = '0px'
    canvas.style.zIndex = '10'
    canvas.style.border = 'none'
    canvas.style.backgroundColor = 'transparent'
    canvas.style.pointerEvents = 'none' // マウスイベントを無効化
    
    console.log('Canvas size set to:', canvas.width, 'x', canvas.height)

    // 透明な背景でクリア（ポーズのみ描画）
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // ポーズランドマークを描画
    if (results.poseLandmarks) {
      console.log('Drawing landmarks, count:', results.poseLandmarks.length)
      
      // スケール調整（MediaPipeの座標は0-1の範囲）
      const scaledLandmarks = results.poseLandmarks.map((landmark: any) => ({
        x: landmark.x * displayWidth,
        y: landmark.y * displayHeight,
        z: landmark.z
      }))

      console.log('First landmark scaled:', scaledLandmarks[0])

      // 手動でランドマークを描画（MediaPipe描画関数の代替）
      console.log('Drawing landmarks manually...')
      
      // ランドマークを赤い円で描画
      ctx.fillStyle = '#FF0000'
      scaledLandmarks.forEach((landmark, index) => {
        ctx.beginPath()
        ctx.arc(landmark.x, landmark.y, 5, 0, 2 * Math.PI)
        ctx.fill()
        
        // ランドマーク番号を表示
        ctx.fillStyle = '#000000'
        ctx.font = '10px Arial'
        ctx.fillText(index.toString(), landmark.x + 7, landmark.y - 7)
        ctx.fillStyle = '#FF0000'
      })
      
      // 接続線を緑で描画
      ctx.strokeStyle = '#00FF00'
      ctx.lineWidth = 3
      POSE_CONNECTIONS.forEach(([start, end]) => {
        if (scaledLandmarks[start] && scaledLandmarks[end]) {
          ctx.beginPath()
          ctx.moveTo(scaledLandmarks[start].x, scaledLandmarks[start].y)
          ctx.lineTo(scaledLandmarks[end].x, scaledLandmarks[end].y)
          ctx.stroke()
        }
      })
      
      console.log('Manual drawing completed')

      // MediaPipeの結果を使用して分析を実行
      const analysis = analyzePostureFromLandmarks(results.poseLandmarks)
      
      // 元画像とポーズを合成したキャンバスを生成
      const compositeCanvas = document.createElement('canvas')
      const compositeCtx = compositeCanvas.getContext('2d')
      
      if (compositeCtx && imageElement) {
        compositeCanvas.width = displayWidth
        compositeCanvas.height = displayHeight
        
        // 元画像を描画
        compositeCtx.drawImage(imageElement, 0, 0, displayWidth, displayHeight)
        
        // ポーズランドマークを描画
        const scaledLandmarks = results.poseLandmarks.map((landmark: any) => ({
          x: landmark.x * displayWidth,
          y: landmark.y * displayHeight,
          z: landmark.z
        }))
        
        // ランドマークを赤い円で描画
        compositeCtx.fillStyle = '#FF0000'
        scaledLandmarks.forEach((landmark, index) => {
          compositeCtx.beginPath()
          compositeCtx.arc(landmark.x, landmark.y, 5, 0, 2 * Math.PI)
          compositeCtx.fill()
          
          // ランドマーク番号を表示
          compositeCtx.fillStyle = '#000000'
          compositeCtx.font = '10px Arial'
          compositeCtx.fillText(index.toString(), landmark.x + 7, landmark.y - 7)
          compositeCtx.fillStyle = '#FF0000'
        })
        
        // 接続線を緑で描画
        compositeCtx.strokeStyle = '#00FF00'
        compositeCtx.lineWidth = 3
        POSE_CONNECTIONS.forEach(([start, end]) => {
          if (scaledLandmarks[start] && scaledLandmarks[end]) {
            compositeCtx.beginPath()
            compositeCtx.moveTo(scaledLandmarks[start].x, scaledLandmarks[start].y)
            compositeCtx.lineTo(scaledLandmarks[end].x, scaledLandmarks[end].y)
            compositeCtx.stroke()
          }
        })
        
        // 合成画像をBlobとして保存
        compositeCanvas.toBlob((blob) => {
          if (blob) {
            analysis.imageUrl = URL.createObjectURL(blob)
          }
          // 分析結果を保存
          setAnalysisResult(analysis)
          setIsAnalyzing(false)
          setAnalysisComplete(true)
          
          console.log('Composite image created with pose overlay')
        })
      }
    } else {
      console.log('No pose landmarks detected')
      setIsAnalyzing(false)
      alert('姿勢が検出されませんでした。全身が写るように撮影してください。')
    }
  }

  const onDrop = async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    const imageUrl = URL.createObjectURL(file)
    setUploadedImage(imageUrl)
    
    setIsAnalyzing(true)
    
    // 画像がロードされてからMediaPipeで解析
    setTimeout(() => {
      if (pose && imageRef.current) {
        console.log('Starting MediaPipe analysis...')
        // 画像が完全にレンダリングされるまで待つ
        const checkImage = () => {
          if (imageRef.current && imageRef.current.offsetWidth > 0) {
            console.log('Sending image to MediaPipe, size:', imageRef.current.offsetWidth, 'x', imageRef.current.offsetHeight)
            pose.send({ image: imageRef.current })
          } else {
            console.log('Image not ready, retrying...')
            setTimeout(checkImage, 100)
          }
        }
        checkImage()
      } else {
        console.log('Pose not initialized or image ref not available')
      }
    }, 100)
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
          <h2 className="text-2xl font-bold text-gray-800">静的姿勢解析</h2>
          <p className="text-gray-600 mt-2">
            正面または側面から撮影した立位姿勢の写真をアップロードして、詳細な姿勢分析を行います
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
                <div className="text-4xl">📸</div>
                <div>
                  <p className="text-lg font-medium text-gray-700">
                    姿勢写真をドラッグ&ドロップ
                  </p>
                  <p className="text-sm text-gray-500">
                    または クリックしてファイルを選択
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
                    alt="アップロード済み画像"
                    className="max-w-md max-h-96 object-contain rounded-lg border block"
                    crossOrigin="anonymous"
                    style={{ display: 'block' }}
                  />
                  <canvas
                    ref={canvasRef}
                    className="absolute top-0 left-0 pointer-events-none"
                  />
                </div>
              </div>
              
              {isAnalyzing && (
                <div className="text-center space-y-4">
                  <div className="inline-flex items-center px-4 py-2 bg-blue-100 rounded-lg">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-3"></div>
                    <span className="text-blue-800 font-medium">AIによる姿勢解析中...</span>
                  </div>
                  <p className="text-sm text-gray-600">
                    MediaPipeでポーズランドマークを検出中...
                  </p>
                </div>
              )}
              
              {analysisComplete && analysisResult && (
                <div className="space-y-6">
                  <div className="text-center space-y-4">
                    <div className="inline-flex items-center px-4 py-2 bg-green-100 rounded-lg">
                      <div className="text-green-600 mr-3">✓</div>
                      <span className="text-green-800 font-medium">分析完了！詳細結果</span>
                    </div>
                  </div>
                  
                  {/* 分析結果表示 */}
                  <div className="bg-gray-50 rounded-lg p-6">
                    <h3 className="text-xl font-bold text-gray-800 mb-4">姿勢分析結果</h3>
                    
                    <div className="grid md:grid-cols-2 gap-6">
                      {/* スコア表示 */}
                      <div className="bg-white rounded-lg p-4">
                        <h4 className="font-semibold text-gray-700 mb-2">総合スコア</h4>
                        <div className="flex items-center space-x-3">
                          <div className="text-3xl font-bold text-blue-600">{analysisResult.score}</div>
                          <div className="text-gray-500">/ 100</div>
                          <div className={`px-2 py-1 rounded text-xs font-medium ${
                            analysisResult.feedback.severity === 'good' ? 'bg-green-100 text-green-800' :
                            analysisResult.feedback.severity === 'mild' ? 'bg-yellow-100 text-yellow-800' :
                            analysisResult.feedback.severity === 'moderate' ? 'bg-orange-100 text-orange-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {analysisResult.feedback.severity === 'good' ? '良好' :
                             analysisResult.feedback.severity === 'mild' ? '軽度' :
                             analysisResult.feedback.severity === 'moderate' ? '中程度' : '要注意'}
                          </div>
                        </div>
                      </div>
                      
                      {/* 測定値表示 */}
                      <div className="bg-white rounded-lg p-4">
                        <h4 className="font-semibold text-gray-700 mb-3">主要測定値</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span>頭部前方位:</span>
                            <span className="font-medium">{analysisResult.measurements.headForwardAngle.toFixed(1)}°</span>
                          </div>
                          <div className="flex justify-between">
                            <span>肩の高さ差:</span>
                            <span className="font-medium">{analysisResult.measurements.shoulderHeight.difference.toFixed(1)}cm</span>
                          </div>
                          <div className="flex justify-between">
                            <span>骨盤傾斜:</span>
                            <span className="font-medium">{Math.abs(analysisResult.measurements.pelvisPosition.anterior).toFixed(1)}°</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* 総合評価 */}
                    <div className="mt-4 bg-white rounded-lg p-4">
                      <h4 className="font-semibold text-gray-700 mb-2">総合評価</h4>
                      <p className="text-gray-600">{analysisResult.feedback.overall}</p>
                    </div>
                    
                    {/* 部位別評価 */}
                    <div className="mt-4 bg-white rounded-lg p-4">
                      <h4 className="font-semibold text-gray-700 mb-3">部位別評価</h4>
                      <div className="grid md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-medium text-gray-600">頭部:</span>
                          <p className="text-gray-500 mt-1">{analysisResult.feedback.areas.head}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-600">肩:</span>
                          <p className="text-gray-500 mt-1">{analysisResult.feedback.areas.shoulders}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-600">脊柱:</span>
                          <p className="text-gray-500 mt-1">{analysisResult.feedback.areas.spine}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-600">骨盤:</span>
                          <p className="text-gray-500 mt-1">{analysisResult.feedback.areas.pelvis}</p>
                        </div>
                      </div>
                    </div>
                    
                    {/* 改善提案 */}
                    {analysisResult.recommendations && analysisResult.recommendations.length > 0 && (
                      <div className="mt-4 bg-white rounded-lg p-4">
                        <h4 className="font-semibold text-gray-700 mb-3">改善提案</h4>
                        <div className="space-y-3">
                          {analysisResult.recommendations.map((rec, index) => (
                            <div key={index} className="border-l-4 border-blue-500 pl-4">
                              <div className="font-medium text-gray-700">{rec.title}</div>
                              <div className="text-sm text-gray-600 mt-1">{rec.description}</div>
                              {rec.exercises && rec.exercises.map((exercise, exIndex) => (
                                <div key={exIndex} className="mt-2 text-xs text-gray-500">
                                  <strong>{exercise.name}:</strong> {exercise.description} 
                                  ({exercise.sets}セット × {exercise.reps}回 × {exercise.duration}秒)
                                </div>
                              ))}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              <div className="flex justify-center space-x-4">
                <button
                  onClick={() => {
                    setUploadedImage(null)
                    setIsAnalyzing(false)
                    setAnalysisComplete(false)
                    setAnalysisResult(null)
                  }}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  disabled={isAnalyzing}
                >
                  別の画像を選択
                </button>
                {analysisComplete && analysisResult && (
                  <button
                    onClick={() => {
                      // 詳細レポート表示画面へ
                      onAnalysisComplete(analysisResult)
                    }}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    📄 詳細レポート表示
                  </button>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="p-6 bg-gray-50 border-t">
          <h3 className="font-semibold text-gray-800 mb-3">撮影のポイント</h3>
          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <div className="space-y-2">
              <h4 className="font-medium text-gray-700">正面撮影時</h4>
              <ul className="space-y-1 text-gray-600">
                <li>• 足を肩幅に開いて自然に立つ</li>
                <li>• カメラは胸の高さに設置</li>
                <li>• 全身が写るように撮影</li>
              </ul>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium text-gray-700">側面撮影時</h4>
              <ul className="space-y-1 text-gray-600">
                <li>• 横向きで自然に立つ</li>
                <li>• 頭から足まで全体を撮影</li>
                <li>• 背景はシンプルに</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// MediaPipeの結果から姿勢分析を実行
function analyzePostureFromLandmarks(landmarks: any[]): PostureAnalysis {
  if (landmarks.length < 33) {
    throw new Error('十分なランドマークが検出されませんでした')
  }

  // 主要なランドマーク取得
  const leftShoulder = landmarks[11]
  const rightShoulder = landmarks[12]
  const leftHip = landmarks[23]
  const rightHip = landmarks[24]
  const nose = landmarks[0]
  const leftEar = landmarks[7]
  const rightEar = landmarks[8]

  // 頭部前方位計算（CVA）
  const headForward = calculateHeadForwardAngle(nose, leftEar, rightEar, leftShoulder, rightShoulder)
  
  // 肩の高さ差計算
  const shoulderHeightDiff = Math.abs(leftShoulder.y - rightShoulder.y) * 100
  
  // 骨盤傾斜計算
  const pelvisTilt = calculatePelvisTilt(leftHip, rightHip)

  // 追加指標（Kendall分類近似のため）
  const earMid = midpoint(leftEar, rightEar)
  const shoulderMid = midpoint(leftShoulder, rightShoulder)
  const hipMid = midpoint(leftHip, rightHip)
  const leftAnkle = landmarks[27]
  const rightAnkle = landmarks[28]
  const ankleMid = midpoint(leftAnkle, rightAnkle)
  const shoulderWidth = distance(leftShoulder, rightShoulder)
  const headOffsetPct = shoulderWidth > 0 ? Math.abs(earMid.x - shoulderMid.x) / shoulderWidth * 100 : 0
  const trunkTiltDeg = (() => {
    const dx = shoulderMid.x - hipMid.x
    const dy = shoulderMid.y - hipMid.y
    const rad = Math.atan2(dx, dy)
    return Math.abs(rad * (180 / Math.PI))
  })()
  const pelvisTranslationPct = shoulderWidth > 0 ? ((hipMid.x - ankleMid.x) / shoulderWidth) * 100 : 0

  // CVA（水平基準）を別途計算して分類に使用
  const cvaDeg = (() => {
    const dx = earMid.x - shoulderMid.x
    const dy = earMid.y - shoulderMid.y
    const rad = Math.atan2(-dy, dx)
    return Math.abs(rad * (180 / Math.PI))
  })()

  const kendall = classifyKendall({
    cvaDeg,
    headOffsetPct,
    trunkTiltDeg,
    pelvisTranslationPct,
  })

  const measurements: PostureMeasurements = {
    headForwardAngle: headForward,
    shoulderHeight: {
      left: leftShoulder.y * 100,
      right: rightShoulder.y * 100,
      difference: shoulderHeightDiff
    },
    spinalAlignment: {
      cervical: headForward,
      thoracic: Math.abs(leftShoulder.y - leftHip.y) * 180,
      lumbar: Math.abs(pelvisTilt)
    },
    pelvisPosition: {
      anterior: pelvisTilt > 0 ? pelvisTilt : 0,
      posterior: pelvisTilt < 0 ? Math.abs(pelvisTilt) : 0,
      lateral: Math.abs(leftHip.y - rightHip.y) * 100
    }
  }

  // 姿勢評価とフィードバック生成
  const feedback = generatePostureFeedback(headForward, shoulderHeightDiff, pelvisTilt, kendall.label)
  const score = calculatePostureScore(headForward, shoulderHeightDiff, pelvisTilt)

  return {
    id: `mediapipe_static_${Date.now()}`,
    timestamp: new Date(),
    type: 'static',
    imageUrl: '', // キャンバスから生成される
    measurements,
    feedback,
    score,
    recommendations: generateRecommendations(headForward, shoulderHeightDiff, pelvisTilt)
  }
}

function calculateHeadForwardAngle(nose: any, leftEar: any, rightEar: any, leftShoulder: any, rightShoulder: any): number {
  // 耳の中点
  const earMidX = (leftEar.x + rightEar.x) / 2
  const earMidY = (leftEar.y + rightEar.y) / 2
  
  // 肩の中点
  const shoulderMidX = (leftShoulder.x + rightShoulder.x) / 2
  const shoulderMidY = (leftShoulder.y + rightShoulder.y) / 2
  
  // 垂直線からの角度計算
  const deltaX = earMidX - shoulderMidX
  const deltaY = earMidY - shoulderMidY
  
  return Math.abs(Math.atan2(deltaX, deltaY) * (180 / Math.PI))
}

function calculatePelvisTilt(leftHip: any, rightHip: any): number {
  const deltaY = leftHip.y - rightHip.y
  const deltaX = leftHip.x - rightHip.x
  return Math.atan2(deltaY, deltaX) * (180 / Math.PI)
}

function generatePostureFeedback(headForward: number, shoulderDiff: number, pelvisTilt: number, kendallLabel?: string): PostureFeedback {
  const issues: string[] = []
  let severity: 'good' | 'mild' | 'moderate' | 'severe' = 'good'

  if (headForward > 25) {
    issues.push('頭部の前方突出が確認されます')
    severity = 'severe'
  } else if (headForward > 15) {
    issues.push('軽度の頭部前方位が見られます')
    severity = severity === 'good' ? 'mild' : severity
  }

  if (shoulderDiff > 3) {
    issues.push('肩の高さに左右差があります')
    severity = severity === 'good' ? 'moderate' : 'severe'
  }

  if (Math.abs(pelvisTilt) > 5) {
    issues.push('骨盤の傾きが見られます')
    severity = severity === 'good' ? 'mild' : severity
  }

  const headline = kendallLabel ? `Kendall分類: ${kendallLabel}。` : ''
  return {
    overall: headline + (issues.length > 0 ? issues.join('。') + '。' : '良好な姿勢を保っています。'),
    areas: {
      head: headForward > 15 ? '頭部が前方に突出しています。頸椎への負担が懸念されます。' : '頭部の位置は良好です。',
      shoulders: shoulderDiff > 2 ? `肩の高さに${shoulderDiff.toFixed(1)}cmの差があります。` : '肩のバランスは良好です。',
      spine: '脊柱アライメントが評価されました。',
      pelvis: Math.abs(pelvisTilt) > 5 ? '骨盤の傾きが確認されます。' : '骨盤の位置は良好です。'
    },
    severity,
    futureRisk: severity !== 'good' ? '姿勢改善により将来的なリスクを軽減できます。' : 'リスクは低く、良好な状態です。'
  }
}

function calculatePostureScore(headForward: number, shoulderDiff: number, pelvisTilt: number): number {
  let score = 100

  // 頭部前方位による減点
  if (headForward > 25) score -= 30
  else if (headForward > 15) score -= 15

  // 肩の高さ差による減点
  if (shoulderDiff > 3) score -= 20
  else if (shoulderDiff > 2) score -= 10

  // 骨盤傾斜による減点
  if (Math.abs(pelvisTilt) > 5) score -= 15

  return Math.max(score, 0)
}

function generateRecommendations(headForward: number, shoulderDiff: number, pelvisTilt: number) {
  const recommendations = []

  if (headForward > 15) {
    recommendations.push({
      category: 'exercise' as const,
      title: '頸部屈筋群強化',
      description: 'MediaPipe解析に基づく頭部前方位改善エクササイズ',
      priority: 'high' as const,
      exercises: [{
        name: 'チンイン運動',
        description: '顎を引いて後頭部を壁に押し付ける',
        sets: 3,
        reps: 10,
        duration: 5
      }]
    })
  }

  if (shoulderDiff > 2) {
    recommendations.push({
      category: 'exercise' as const,
      title: '肩バランス改善',
      description: 'MediaPipe検出による左右肩の高さ差改善',
      priority: 'high' as const,
      exercises: [{
        name: '肩甲骨リセット',
        description: '肩甲骨を寄せて下げる動作を繰り返す',
        sets: 3,
        reps: 15,
        duration: 3
      }]
    })
  }

  return recommendations
}

function midpoint(a: any, b: any) { return { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 } }
function distance(a: any, b: any) { return Math.hypot(b.x - a.x, b.y - a.y) }

// Kendall classification uses shared lib
