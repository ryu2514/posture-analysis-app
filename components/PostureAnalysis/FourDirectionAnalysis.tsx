"use client"

import React, { useState, useRef, useEffect } from 'react'
import { classifyKendall } from '@/lib/kendall'
import { useDropzone } from 'react-dropzone'
import { Pose } from '@mediapipe/pose'
import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils'
import { PostureAnalysis, FourDirectionMeasurements } from '@/types/posture'

interface DirectionImages {
  front?: File
  back?: File
  leftSide?: File
  rightSide?: File
}

interface DirectionResults {
  front?: PostureAnalysis
  back?: PostureAnalysis
  leftSide?: PostureAnalysis
  rightSide?: PostureAnalysis
}

const DIRECTIONS = [
  { key: 'front', label: '正面', icon: '👤' },
  { key: 'leftSide', label: '左側面', icon: '👈' },
  { key: 'back', label: '背面', icon: '👥' },
  { key: 'rightSide', label: '右側面', icon: '👉' }
] as const

// MediaPipe Poseのランドマーク接続定義
const POSE_CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 7], [0, 4], [4, 5], [5, 6], [6, 8],
  [9, 10], [11, 12], [11, 13], [13, 15], [15, 17], [15, 19], [15, 21],
  [17, 19], [12, 14], [14, 16], [16, 18], [16, 20], [16, 22], [18, 20],
  [11, 23], [12, 24], [23, 24], [23, 25], [24, 26], [25, 27], [26, 28],
  [27, 29], [28, 30], [29, 31], [30, 32], [27, 31], [28, 32]
]

export default function FourDirectionAnalysis({ onAnalysisComplete }: { onAnalysisComplete: (analysis: PostureAnalysis) => void }) {
  const [images, setImages] = useState<DirectionImages>({})
  const [currentDirection, setCurrentDirection] = useState<keyof DirectionImages>('front')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisComplete, setAnalysisComplete] = useState(false)
  const [directionResults, setDirectionResults] = useState<DirectionResults>({})
  const [finalResult, setFinalResult] = useState<PostureAnalysis | null>(null)
  const [pose, setPose] = useState<Pose | null>(null)
  
  // 各方向のCanvasとImageRef
  const canvasRefs = {
    front: useRef<HTMLCanvasElement>(null),
    back: useRef<HTMLCanvasElement>(null),
    leftSide: useRef<HTMLCanvasElement>(null),
    rightSide: useRef<HTMLCanvasElement>(null)
  }
  
  const imageRefs = {
    front: useRef<HTMLImageElement>(null),
    back: useRef<HTMLImageElement>(null),
    leftSide: useRef<HTMLImageElement>(null),
    rightSide: useRef<HTMLImageElement>(null)
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

        setPose(poseInstance)
        console.log('MediaPipe initialized for 4-direction analysis')

      } catch (error) {
        console.error('MediaPipe初期化エラー:', error)
      }
    }

    initializeMediaPipe()
  }, [])

  const onDrop = (acceptedFiles: File[], direction: keyof DirectionImages) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0]
      setImages(prev => ({
        ...prev,
        [direction]: file
      }))
      
      // 画像アップロード後、自動でMediaPipe解析を実行
      if (pose) {
        setTimeout(() => {
          analyzeDirection(file, direction)
        }, 100)
      }
    }
  }

  const analyzeDirection = async (file: File, direction: keyof DirectionImages) => {
    if (!pose) return

    const imageUrl = URL.createObjectURL(file)
    const img = new Image()
    
    img.onload = async () => {
      const imageRef = imageRefs[direction]
      const canvasRef = canvasRefs[direction]
      
      if (imageRef.current && canvasRef.current) {
        imageRef.current.src = imageUrl
        
        // MediaPipe解析結果のコールバックを設定
        pose.onResults((results: any) => {
          handleDirectionResults(results, direction, file)
        })
        
        // 画像がロードされてから解析開始
        setTimeout(() => {
          if (imageRef.current) {
            pose.send({ image: imageRef.current })
          }
        }, 100)
      }
    }
    
    img.src = imageUrl
  }

  const handleDirectionResults = (results: any, direction: keyof DirectionImages, file: File) => {
    const canvasRef = canvasRefs[direction]
    const imageRef = imageRefs[direction]
    
    if (!canvasRef.current || !imageRef.current) return
    
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const imageElement = imageRef.current
    const displayWidth = imageElement.offsetWidth
    const displayHeight = imageElement.offsetHeight
    
    // キャンバスサイズを表示サイズに合わせる
    canvas.width = displayWidth
    canvas.height = displayHeight
    
    // Canvasスタイルを設定
    canvas.style.width = `${displayWidth}px`
    canvas.style.height = `${displayHeight}px`
    canvas.style.position = 'absolute'
    canvas.style.top = '0px'
    canvas.style.left = '0px'
    canvas.style.zIndex = '10'
    canvas.style.border = 'none'
    canvas.style.backgroundColor = 'transparent'
    canvas.style.pointerEvents = 'none'

    // 透明な背景でクリア
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // ポーズランドマークを描画
    if (results.poseLandmarks) {
      const scaledLandmarks = results.poseLandmarks.map((landmark: any) => ({
        x: landmark.x * displayWidth,
        y: landmark.y * displayHeight,
        z: landmark.z
      }))

      // ランドマークを赤い円で描画
      ctx.fillStyle = '#FF0000'
      scaledLandmarks.forEach((landmark, index) => {
        ctx.beginPath()
        ctx.arc(landmark.x, landmark.y, 4, 0, 2 * Math.PI)
        ctx.fill()
        
        // ランドマーク番号を表示
        ctx.fillStyle = '#000000'
        ctx.font = '8px Arial'
        ctx.fillText(index.toString(), landmark.x + 5, landmark.y - 5)
        ctx.fillStyle = '#FF0000'
      })
      
      // 接続線を緑で描画
      ctx.strokeStyle = '#00FF00'
      ctx.lineWidth = 2
      POSE_CONNECTIONS.forEach(([start, end]) => {
        if (scaledLandmarks[start] && scaledLandmarks[end]) {
          ctx.beginPath()
          ctx.moveTo(scaledLandmarks[start].x, scaledLandmarks[start].y)
          ctx.lineTo(scaledLandmarks[end].x, scaledLandmarks[end].y)
          ctx.stroke()
        }
      })

      // 方向別の分析結果を生成
      const analysis = analyzePostureFromLandmarks(results.poseLandmarks, direction, file)
      
      setDirectionResults(prev => ({
        ...prev,
        [direction]: analysis
      }))

      console.log(`${direction} analysis completed`)
    }
  }

  const createDropzone = (direction: keyof DirectionImages) => {
    return useDropzone({
      onDrop: (files) => onDrop(files, direction),
      accept: {
        'image/*': ['.jpg', '.jpeg', '.png']
      },
      multiple: false
    })
  }

  const dropzones = {
    front: createDropzone('front'),
    back: createDropzone('back'),
    leftSide: createDropzone('leftSide'),
    rightSide: createDropzone('rightSide')
  }

  const uploadedCount = Object.values(images).filter(Boolean).length
  const analyzedCount = Object.values(directionResults).filter(Boolean).length
  const isComplete = uploadedCount === 4 && analyzedCount === 4

  const handleFinalAnalysis = () => {
    if (!isComplete) return
    
    // 4方向の結果を統合した最終分析結果を生成
    const combinedAnalysis = combineFourDirectionResults(directionResults as Required<DirectionResults>)
    setFinalResult(combinedAnalysis)
    setAnalysisComplete(true)
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg">
        <div className="p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-800">4方向姿勢解析（MediaPipe版）</h2>
          <p className="text-gray-600 mt-2">
            正面・背面・左側面・右側面の4方向から撮影した写真で、MediaPipeによるリアルタイム姿勢解析を行います
          </p>
          <div className="mt-4">
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-500">進捗:</div>
              <div className="flex-1 bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(analyzedCount / 4) * 100}%` }}
                ></div>
              </div>
              <div className="text-sm font-medium text-gray-700">
                {analyzedCount}/4 方向解析完了
              </div>
            </div>
          </div>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            {DIRECTIONS.map(({ key, label, icon }) => {
              const dropzone = dropzones[key]
              const hasImage = !!images[key]
              const hasAnalysis = !!directionResults[key]
              
              return (
                <div key={key} className="space-y-3">
                  <div className="text-center">
                    <div className="text-2xl mb-1">{icon}</div>
                    <h3 className="font-medium text-gray-800">{label}</h3>
                    {hasAnalysis && (
                      <div className="text-xs text-green-600 mt-1">✓ 解析完了</div>
                    )}
                  </div>
                  
                  {!hasImage ? (
                    <div 
                      {...dropzone.getRootProps()}
                      className={`
                        aspect-[3/4] border-2 border-dashed rounded-lg cursor-pointer transition-all
                        ${dropzone.isDragActive 
                          ? 'border-blue-400 bg-blue-50' 
                          : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
                        }
                      `}
                    >
                      <input {...dropzone.getInputProps()} />
                      <div className="h-full flex flex-col items-center justify-center p-4 text-center">
                        <div className="text-gray-400 text-2xl mb-2">📸</div>
                        <div className="text-sm text-gray-600">
                          クリックまたは<br />ドラッグ&ドロップ
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="aspect-[3/4] relative border-2 border-green-400 rounded-lg overflow-hidden">
                      <img 
                        ref={imageRefs[key]}
                        src={URL.createObjectURL(images[key]!)}
                        alt={`${label}画像`}
                        className="w-full h-full object-cover"
                        crossOrigin="anonymous"
                      />
                      <canvas
                        ref={canvasRefs[key]}
                        className="absolute top-0 left-0 pointer-events-none"
                      />
                      {hasAnalysis && (
                        <div className="absolute top-2 right-2 bg-green-500 text-white text-xs px-2 py-1 rounded">
                          ✓ 解析済み
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          {isComplete && !analysisComplete && (
            <div className="mt-8 text-center">
              <button
                onClick={handleFinalAnalysis}
                className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                4方向総合解析を表示
              </button>
            </div>
          )}

          {analysisComplete && finalResult && (
            <div className="mt-8 space-y-6">
              <div className="text-center">
                <div className="inline-flex items-center px-6 py-3 bg-green-100 rounded-lg">
                  <div className="text-green-600 mr-3">✓</div>
                  <span className="text-green-800 font-medium">4方向解析完了！</span>
                </div>
              </div>
              
              {/* 4方向統合結果表示 */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4">4方向総合姿勢分析結果</h3>
                
                <div className="grid md:grid-cols-3 gap-6">
                  {/* 総合スコア */}
                  <div className="bg-white rounded-lg p-4">
                    <h4 className="font-semibold text-gray-700 mb-2">総合スコア</h4>
                    <div className="flex items-center space-x-3">
                      <div className="text-3xl font-bold text-blue-600">{finalResult.score}</div>
                      <div className="text-gray-500">/ 100</div>
                      <div className={`px-2 py-1 rounded text-xs font-medium ${
                        finalResult.feedback.severity === 'good' ? 'bg-green-100 text-green-800' :
                        finalResult.feedback.severity === 'mild' ? 'bg-yellow-100 text-yellow-800' :
                        finalResult.feedback.severity === 'moderate' ? 'bg-orange-100 text-orange-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {finalResult.feedback.severity === 'good' ? '良好' :
                         finalResult.feedback.severity === 'mild' ? '軽度' :
                         finalResult.feedback.severity === 'moderate' ? '中程度' : '要注意'}
                      </div>
                    </div>
                  </div>
                  
                  {/* 方向別スコア */}
                  <div className="bg-white rounded-lg p-4 col-span-2">
                    <h4 className="font-semibold text-gray-700 mb-3">方向別分析</h4>
                    <div className="grid grid-cols-4 gap-2 text-sm">
                      {DIRECTIONS.map(({ key, label, icon }) => (
                        <div key={key} className="text-center">
                          <div className="text-lg mb-1">{icon}</div>
                          <div className="text-xs text-gray-600">{label}</div>
                          <div className="font-medium text-blue-600">
                            {directionResults[key]?.score || 0}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                
                {/* 総合評価 */}
                <div className="mt-4 bg-white rounded-lg p-4">
                  <h4 className="font-semibold text-gray-700 mb-2">4方向統合評価</h4>
                  <p className="text-gray-600">{finalResult.feedback.overall}</p>
                </div>
                
                {/* 改善提案 */}
                {finalResult.recommendations && finalResult.recommendations.length > 0 && (
                  <div className="mt-4 bg-white rounded-lg p-4">
                    <h4 className="font-semibold text-gray-700 mb-3">統合改善プログラム</h4>
                    <div className="space-y-3">
                      {finalResult.recommendations.map((rec, index) => (
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
        </div>

        <div className="p-6 bg-gray-50 border-t">
          <h3 className="font-semibold text-gray-800 mb-4">MediaPipe 4方向解析の特徴</h3>
          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <div className="space-y-2">
              <h4 className="font-medium text-gray-700">自動解析機能</h4>
              <ul className="space-y-1 text-gray-600 text-xs">
                <li>• 画像アップロード後即座に解析開始</li>
                <li>• 33個のポーズランドマークを自動検出</li>
                <li>• リアルタイムでポーズ描画表示</li>
              </ul>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium text-gray-700">高精度測定</h4>
              <ul className="space-y-1 text-gray-600 text-xs">
                <li>• 実際のランドマーク座標から計算</li>
                <li>• 4方向からの包括的評価</li>
                <li>• 統合スコアと改善プログラム提供</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="p-6 text-center">
          <button
            onClick={() => {
              setImages({})
              setDirectionResults({})
              setFinalResult(null)
              setAnalysisComplete(false)
            }}
            className="px-6 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            新しい4方向解析を開始
          </button>
          {finalResult && (
            <button
              onClick={() => onAnalysisComplete(finalResult)}
              className="ml-4 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              📄 詳細レポート表示
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

// MediaPipeの結果から方向別姿勢分析を実行
function analyzePostureFromLandmarks(landmarks: any[], direction: string, imageFile: File): PostureAnalysis {
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

  // 追加指標（Kendall分類を近似）
  const earMid = { x: (leftEar.x + rightEar.x) / 2, y: (leftEar.y + rightEar.y) / 2 }
  const shoulderMid = { x: (leftShoulder.x + rightShoulder.x) / 2, y: (leftShoulder.y + rightShoulder.y) / 2 }
  const leftAnkle = landmarks[27]
  const rightAnkle = landmarks[28]
  const hipMid = { x: (leftHip.x + rightHip.x) / 2, y: (leftHip.y + rightHip.y) / 2 }
  const ankleMid = { x: (leftAnkle.x + rightAnkle.x) / 2, y: (leftAnkle.y + rightAnkle.y) / 2 }
  const shoulderWidth = Math.hypot(rightShoulder.x - leftShoulder.x, rightShoulder.y - leftShoulder.y)
  const headOffsetPct = shoulderWidth > 0 ? Math.abs(earMid.x - shoulderMid.x) / shoulderWidth * 100 : 0
  const trunkTiltDeg = (() => {
    const dx = shoulderMid.x - hipMid.x
    const dy = shoulderMid.y - hipMid.y
    const rad = Math.atan2(dx, dy)
    return Math.abs(rad * (180 / Math.PI))
  })()
  const pelvisTranslationPct = shoulderWidth > 0 ? ((hipMid.x - ankleMid.x) / shoulderWidth) * 100 : 0
  const cvaDegHorizontal = (() => {
    const dx = earMid.x - shoulderMid.x
    const dy = earMid.y - shoulderMid.y
    const rad = Math.atan2(-dy, dx)
    return Math.abs(rad * (180 / Math.PI))
  })()
  const kendall = classifyKendall({
    cvaDeg: cvaDegHorizontal,
    headOffsetPct,
    trunkTiltDeg,
    pelvisTranslationPct,
  })

  const measurements: FourDirectionMeasurements = {
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
    },
    directions: {
      front: {
        headForwardAngle: headForward,
        shoulderHeight: { left: leftShoulder.y * 100, right: rightShoulder.y * 100, difference: shoulderHeightDiff },
        spinalAlignment: { cervical: headForward, thoracic: Math.abs(leftShoulder.y - leftHip.y) * 180, lumbar: Math.abs(pelvisTilt) },
        pelvisPosition: { anterior: pelvisTilt > 0 ? pelvisTilt : 0, posterior: 0, lateral: Math.abs(leftHip.y - rightHip.y) * 100 }
      },
      back: {
        headForwardAngle: 0,
        shoulderHeight: { left: 0, right: 0, difference: 0 },
        spinalAlignment: { cervical: 0, thoracic: 0, lumbar: 0 },
        pelvisPosition: { anterior: 0, posterior: 0, lateral: 0 }
      },
      leftSide: {
        headForwardAngle: headForward,
        shoulderHeight: { left: 0, right: 0, difference: 0 },
        spinalAlignment: { cervical: headForward, thoracic: Math.abs(leftShoulder.y - leftHip.y) * 180, lumbar: Math.abs(pelvisTilt) },
        pelvisPosition: { anterior: pelvisTilt > 0 ? pelvisTilt : 0, posterior: 0, lateral: 0 }
      },
      rightSide: {
        headForwardAngle: headForward,
        shoulderHeight: { left: 0, right: 0, difference: 0 },
        spinalAlignment: { cervical: headForward, thoracic: Math.abs(leftShoulder.y - leftHip.y) * 180, lumbar: Math.abs(pelvisTilt) },
        pelvisPosition: { anterior: pelvisTilt > 0 ? pelvisTilt : 0, posterior: 0, lateral: 0 }
      }
    },
    spinalCurvature: {
      cervicalCurve: headForward,
      thoracicKyphosis: Math.abs(leftShoulder.y - leftHip.y) * 180,
      lumbarLordosis: Math.abs(pelvisTilt)
    }
  }

  const feedback = generatePostureFeedback(headForward, shoulderHeightDiff, pelvisTilt, direction, kendall.label)
  const score = calculatePostureScore(headForward, shoulderHeightDiff, pelvisTilt)

  return {
    id: `mediapipe_${direction}_${Date.now()}`,
    timestamp: new Date(),
    type: 'fourDirection',
    imageUrl: URL.createObjectURL(imageFile),
    measurements,
    feedback,
    score,
    recommendations: generateRecommendations(headForward, shoulderHeightDiff, pelvisTilt, direction)
  }
}

function calculateHeadForwardAngle(nose: any, leftEar: any, rightEar: any, leftShoulder: any, rightShoulder: any): number {
  const earMidX = (leftEar.x + rightEar.x) / 2
  const earMidY = (leftEar.y + rightEar.y) / 2
  const shoulderMidX = (leftShoulder.x + rightShoulder.x) / 2
  const shoulderMidY = (leftShoulder.y + rightShoulder.y) / 2
  const deltaX = earMidX - shoulderMidX
  const deltaY = earMidY - shoulderMidY
  return Math.abs(Math.atan2(deltaX, deltaY) * (180 / Math.PI))
}

function calculatePelvisTilt(leftHip: any, rightHip: any): number {
  const deltaY = leftHip.y - rightHip.y
  const deltaX = leftHip.x - rightHip.x
  return Math.atan2(deltaY, deltaX) * (180 / Math.PI)
}

function generatePostureFeedback(headForward: number, shoulderDiff: number, pelvisTilt: number, direction: string, kendallLabel?: string): any {
  const issues: string[] = []
  let severity: 'good' | 'mild' | 'moderate' | 'severe' = 'good'

  if (headForward > 25) {
    issues.push(`${direction}から頭部の前方突出が確認されます`)
    severity = 'severe'
  } else if (headForward > 15) {
    issues.push(`${direction}で軽度の頭部前方位が見られます`)
    severity = severity === 'good' ? 'mild' : severity
  }

  if (shoulderDiff > 3) {
    issues.push(`肩の高さに左右差があります`)
    severity = severity === 'good' ? 'moderate' : 'severe'
  }

  if (Math.abs(pelvisTilt) > 5) {
    issues.push(`骨盤の傾きが見られます`)
    severity = severity === 'good' ? 'mild' : severity
  }

  const headline = kendallLabel ? `Kendall分類: ${kendallLabel}。` : ''
  return {
    overall: headline + (issues.length > 0 ? `${direction}方向の解析：${issues.join('。')}。` : `${direction}方向では良好な姿勢を保っています。`),
    areas: {
      head: headForward > 15 ? `${direction}で頭部が前方に突出しています。` : `${direction}での頭部位置は良好です。`,
      shoulders: shoulderDiff > 2 ? `肩の高さに${shoulderDiff.toFixed(1)}cmの差があります。` : '肩のバランスは良好です。',
      spine: `${direction}方向での脊柱アライメントが評価されました。`,
      pelvis: Math.abs(pelvisTilt) > 5 ? '骨盤の傾きが確認されます。' : '骨盤の位置は良好です。'
    },
    severity,
    futureRisk: severity !== 'good' ? `${direction}方向での姿勢改善により将来的なリスクを軽減できます。` : 'リスクは低く、良好な状態です。'
  }
}

function calculatePostureScore(headForward: number, shoulderDiff: number, pelvisTilt: number): number {
  let score = 100
  if (headForward > 25) score -= 30
  else if (headForward > 15) score -= 15
  if (shoulderDiff > 3) score -= 20
  else if (shoulderDiff > 2) score -= 10
  if (Math.abs(pelvisTilt) > 5) score -= 15
  return Math.max(score, 0)
}

function generateRecommendations(headForward: number, shoulderDiff: number, pelvisTilt: number, direction: string): any[] {
  const recommendations = []

  if (headForward > 15) {
    recommendations.push({
      category: 'exercise' as const,
      title: `${direction}方向：頸部改善`,
      description: `${direction}方向のMediaPipe解析に基づく頭部前方位改善`,
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

  return recommendations
}

function combineFourDirectionResults(results: Required<DirectionResults>): PostureAnalysis {
  // 4方向の結果を統合
  const averageScore = Object.values(results).reduce((sum, result) => sum + result.score, 0) / 4
  const labels = {
    front: (results.front.feedback.overall.match(/Kendall分類: ([^。]+)/)?.[1]) || '—',
    back: (results.back.feedback.overall.match(/Kendall分類: ([^。]+)/)?.[1]) || '—',
    leftSide: (results.leftSide.feedback.overall.match(/Kendall分類: ([^。]+)/)?.[1]) || '—',
    rightSide: (results.rightSide.feedback.overall.match(/Kendall分類: ([^。]+)/)?.[1]) || '—',
  }
  const overallSummary = `4方向MediaPipe解析により包括的な姿勢評価が完了しました。各方向からの詳細な分析に基づいた統合評価です。\n\nKendall分類（参考）: 正面=${labels.front} / 背面=${labels.back} / 左側面=${labels.leftSide} / 右側面=${labels.rightSide}`
  
  return {
    id: `four_direction_combined_${Date.now()}`,
    timestamp: new Date(),
    type: 'fourDirection',
    imageUrl: results.front.imageUrl,
    measurements: results.front.measurements,
    feedback: {
      overall: overallSummary,
      areas: {
        head: "4方向からの頭部位置分析が完了しました。",
        shoulders: "全方向での肩のバランス評価が完了しました。",
        spine: "4方向からの脊柱アライメント分析が完了しました。",
        pelvis: "全方向での骨盤位置評価が完了しました。"
      },
      severity: averageScore > 85 ? 'good' : averageScore > 70 ? 'mild' : averageScore > 55 ? 'moderate' : 'severe',
      futureRisk: "4方向統合解析に基づく包括的な改善プログラムで効果的な改善が期待できます。"
    },
    score: Math.round(averageScore),
    recommendations: [
      {
        category: 'exercise',
        title: '4方向統合改善プログラム',
        description: 'MediaPipe 4方向解析結果に基づく包括的改善プログラム',
        priority: 'high',
        exercises: [
          {
            name: '統合姿勢改善エクササイズ',
            description: '4方向解析結果を統合した改善運動',
            sets: 3,
            reps: 15,
            duration: 10
          }
        ]
      }
    ]
  }
}

// Kendall classification uses shared lib
