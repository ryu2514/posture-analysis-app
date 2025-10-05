"use client"

import React, { useRef, useEffect, useState } from 'react'
import { classifyKendall } from '@/lib/kendall'
import { Pose } from '@mediapipe/pose'
import { Camera } from '@mediapipe/camera_utils'
import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils'
import { PostureAnalysis } from '@/types/posture'

interface MediaPipePoseAnalysisProps {
  onAnalysisComplete?: (analysis: PostureAnalysis) => void
}

// MediaPipe Poseのランドマーク接続定義
const POSE_CONNECTIONS: [number, number][] = [
  [0, 1], [1, 2], [2, 3], [3, 7], [0, 4], [4, 5], [5, 6], [6, 8],
  [9, 10], [11, 12], [11, 13], [13, 15], [15, 17], [15, 19], [15, 21],
  [17, 19], [12, 14], [14, 16], [16, 18], [16, 20], [16, 22], [18, 20],
  [11, 23], [12, 24], [23, 24], [23, 25], [24, 26], [25, 27], [26, 28],
  [27, 29], [28, 30], [29, 31], [30, 32], [27, 31], [28, 32]
]

export default function MediaPipePoseAnalysis({ onAnalysisComplete }: MediaPipePoseAnalysisProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [isActive, setIsActive] = useState(false)
  const [pose, setPose] = useState<Pose | null>(null)
  const [camera, setCamera] = useState<Camera | null>(null)
  const [landmarks, setLandmarks] = useState<any>(null)
  const [analysis, setAnalysis] = useState<string>('')
  const [showGuides, setShowGuides] = useState(true)

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

    return () => {
      if (camera) {
        camera.stop()
      }
    }
  }, [])

  const onResults = (results: any) => {
    if (!canvasRef.current || !videoRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // キャンバスサイズを設定
    canvas.width = videoRef.current.videoWidth
    canvas.height = videoRef.current.videoHeight

    // ビデオフレームを描画
    ctx.save()
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height)

    // ポーズランドマークを描画
    if (results.poseLandmarks) {
      setLandmarks(results.poseLandmarks)
      
      // 接続線を描画
      if (showGuides) {
        drawConnectors(ctx, results.poseLandmarks, POSE_CONNECTIONS, {
          color: '#00FF00',
          lineWidth: 2
        })
      }
      
      // ランドマークを描画
      if (showGuides) {
        drawLandmarks(ctx, results.poseLandmarks, {
          color: '#FF0000',
          lineWidth: 1,
          radius: 3
        })
      }

      // 姿勢分析を実行
      analyzePose(results.poseLandmarks, ctx)
    }

    ctx.restore()
  }

  const analyzePose = (landmarks: any[], ctx?: CanvasRenderingContext2D | null) => {
    if (landmarks.length < 33) return

    // 主要なランドマーク取得
    const leftShoulder = landmarks[11]
    const rightShoulder = landmarks[12]
    const leftHip = landmarks[23]
    const rightHip = landmarks[24]
    const leftKnee = landmarks[25]
    const rightKnee = landmarks[26]
    const leftAnkle = landmarks[27]
    const rightAnkle = landmarks[28]
    const nose = landmarks[0]
    const leftEar = landmarks[7]
    const rightEar = landmarks[8]

    // 頭部前方位計算（CVA）: C7(肩の中点)と耳珠(左右耳の中点)の線と水平線の角度
    const headForwardCVA = calculateCVA(leftEar, rightEar, leftShoulder, rightShoulder)
    
    // 肩の高さ差計算
    const shoulderHeightDiff = Math.abs(leftShoulder.y - rightShoulder.y) * 100
    // 肩の傾き（度）: 肩線と水平の角度
    const shoulderTiltDeg = calculateLineAngleDeg(leftShoulder, rightShoulder)
    
    // 骨盤傾斜計算
    const pelvisTilt = calculatePelvisTilt(leftHip, rightHip)

    // 前方頭位オフセット（肩幅比%）: 耳中点と肩中点の水平距離 / 肩幅
    const earMid = midpoint(leftEar, rightEar)
    const shoulderMid = midpoint(leftShoulder, rightShoulder)
    const hipMid = midpoint(leftHip, rightHip)
    const kneeMid = midpoint(leftKnee, rightKnee)
    const ankleMid = midpoint(leftAnkle, rightAnkle)
    const shoulderWidth = distance(leftShoulder, rightShoulder)
    const forwardHeadOffsetPct = shoulderWidth > 0 ? Math.abs((earMid.x - shoulderMid.x)) / shoulderWidth * 100 : 0

    // 体幹の鉛直からの傾き（肩→股関節の線と垂直のなす角）
    const trunkAngleFromVertical = () => {
      const dx = shoulderMid.x - hipMid.x
      const dy = shoulderMid.y - hipMid.y
      const rad = Math.atan2(dx, dy) // 垂直基準
      return Math.abs(rad * (180 / Math.PI))
    }

    const trunkTiltDeg = trunkAngleFromVertical()

    // 骨盤の前後翻訳（足関節に対する股関節の水平オフセット）
    const pelvisTranslationPct = shoulderWidth > 0 ? ((hipMid.x - ankleMid.x) / shoulderWidth) * 100 : 0

    const kendall = classifyKendall({
      cvaDeg: headForwardCVA,
      headOffsetPct: forwardHeadOffsetPct,
      shoulderTiltDeg,
      pelvisTiltLatDeg: pelvisTilt,
      trunkTiltDeg,
      pelvisTranslationPct,
      shoulderWidth,
    })

    // ガイド描画
    if (ctx && showGuides) {
      drawGuides(ctx, {
        earMid,
        shoulderMid,
        leftShoulder,
        rightShoulder,
        leftHip,
        rightHip,
        headForwardCVA,
        shoulderTiltDeg,
        pelvisTilt,
      })
    }

    const analysisText = `
姿勢分析結果（リアルタイム）:
• 頭部前方位 (CVA): ${headForwardCVA.toFixed(1)}度
• 肩の高さ差: ${shoulderHeightDiff.toFixed(1)}cm
• 肩の傾き: ${shoulderTiltDeg.toFixed(1)}度
• 骨盤傾斜: ${pelvisTilt.toFixed(1)}度
• 前方頭位オフセット: ${forwardHeadOffsetPct.toFixed(1)}%
• 体幹傾き（鉛直基準）: ${trunkTiltDeg.toFixed(1)}度
• 骨盤前後翻訳: ${pelvisTranslationPct.toFixed(1)}%

Kendall分類: ${kendall.label}
根拠: ${kendall.reason}

${getPostureAdvice(headForwardCVA, shoulderHeightDiff, pelvisTilt)}
    `
    
    setAnalysis(analysisText)
  }

  const calculateCVA = (leftEar: any, rightEar: any, leftShoulder: any, rightShoulder: any) => {
    const ear = midpoint(leftEar, rightEar)
    const c7 = midpoint(leftShoulder, rightShoulder)
    // 角度: 水平線とC7→耳の線のなす角
    const dx = ear.x - c7.x
    const dy = ear.y - c7.y
    const angleRad = Math.atan2(-dy, dx) // キャンバスyは下向きなので符号調整
    const deg = Math.abs(angleRad * (180 / Math.PI))
    return deg
  }

  const calculatePelvisTilt = (leftHip: any, rightHip: any) => {
    const deltaY = leftHip.y - rightHip.y
    const deltaX = leftHip.x - rightHip.x
    return Math.atan2(deltaY, deltaX) * (180 / Math.PI)
  }

  const calculateLineAngleDeg = (a: any, b: any) => {
    const dx = b.x - a.x
    const dy = b.y - a.y
    const rad = Math.atan2(dy, dx)
    return rad * (180 / Math.PI)
  }

  const distance = (a: any, b: any) => Math.hypot(b.x - a.x, b.y - a.y)
  const midpoint = (a: any, b: any) => ({ x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 })

  const drawGuides = (
    ctx: CanvasRenderingContext2D,
    params: {
      earMid: { x: number; y: number }
      shoulderMid: { x: number; y: number }
      leftShoulder: any
      rightShoulder: any
      leftHip: any
      rightHip: any
      headForwardCVA: number
      shoulderTiltDeg: number
      pelvisTilt: number
    }
  ) => {
    const { earMid, shoulderMid, leftShoulder, rightShoulder, leftHip, rightHip, headForwardCVA } = params

    // 垂直基準線（肩中点を通る）
    ctx.strokeStyle = '#3B82F6'
    ctx.lineWidth = 2
    ctx.setLineDash([6, 6])
    ctx.beginPath()
    ctx.moveTo(shoulderMid.x, 0)
    ctx.lineTo(shoulderMid.x, ctx.canvas.height)
    ctx.stroke()
    ctx.setLineDash([])

    // 肩ライン
    ctx.strokeStyle = '#10B981'
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.moveTo(leftShoulder.x, leftShoulder.y)
    ctx.lineTo(rightShoulder.x, rightShoulder.y)
    ctx.stroke()

    // 骨盤ライン
    ctx.strokeStyle = '#F59E0B'
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.moveTo(leftHip.x, leftHip.y)
    ctx.lineTo(rightHip.x, rightHip.y)
    ctx.stroke()

    // C7→耳のライン
    ctx.strokeStyle = '#EF4444'
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.moveTo(shoulderMid.x, shoulderMid.y)
    ctx.lineTo(earMid.x, earMid.y)
    ctx.stroke()

    // CVA角度アーク描画
    drawAngleArc(ctx, shoulderMid, { x: shoulderMid.x + 60, y: shoulderMid.y }, earMid, '#EF4444')

    // ラベル
    ctx.fillStyle = '#111827'
    ctx.font = '12px sans-serif'
    ctx.fillText(`CVA`, shoulderMid.x + 8, shoulderMid.y - 8)
  }

  const drawAngleArc = (
    ctx: CanvasRenderingContext2D,
    center: { x: number; y: number },
    p1: { x: number; y: number }, // 基準（水平右方向）
    p2: { x: number; y: number }, // 測定線先
    color = '#EF4444'
  ) => {
    const a1 = Math.atan2(-(p1.y - center.y), p1.x - center.x)
    const a2 = Math.atan2(-(p2.y - center.y), p2.x - center.x)
    let start = a1
    let end = a2
    if (end < start) {
      const tmp = start
      start = end
      end = tmp
    }
    ctx.beginPath()
    ctx.strokeStyle = color
    ctx.lineWidth = 2
    ctx.arc(center.x, center.y, 40, -start, -end, true) // y軸反転を考慮
    ctx.stroke()
  }

  // Kendall classification moved to shared lib (lib/kendall)

  const getPostureAdvice = (headForward: number, shoulderDiff: number, pelvisTilt: number) => {
    const issues = []
    
    if (headForward > 15) {
      issues.push('頭部の前方突出が確認されます。首のストレッチを行ってください。')
    }
    
    if (shoulderDiff > 2) {
      issues.push('肩の高さに左右差があります。姿勢を意識してください。')
    }
    
    if (Math.abs(pelvisTilt) > 5) {
      issues.push('骨盤の傾きが見られます。体幹の安定性を高めましょう。')
    }

    return issues.length > 0 ? issues.join('\n• ') : '良好な姿勢を保っています！'
  }

  const startCamera = async () => {
    if (!pose || !videoRef.current) return

    try {
      const cameraInstance = new Camera(videoRef.current, {
        onFrame: async () => {
          if (pose && videoRef.current) {
            await pose.send({ image: videoRef.current })
          }
        },
        width: 640,
        height: 480
      })

      await cameraInstance.start()
      setCamera(cameraInstance)
      setIsActive(true)
    } catch (error) {
      console.error('カメラ起動エラー:', error)
      alert('カメラにアクセスできませんでした。ブラウザの設定を確認してください。')
    }
  }

  const stopCamera = () => {
    if (camera) {
      camera.stop()
      setCamera(null)
      setIsActive(false)
      setLandmarks(null)
      setAnalysis('')
    }
  }

  const captureAnalysis = async () => {
    if (!landmarks || !canvasRef.current) return

    // キャンバスから画像データを取得
    const canvas = canvasRef.current
    canvas.toBlob(async (blob) => {
      if (!blob) return

      // 現在の分析データをPostureAnalysis形式に変換
      const analysisResult: PostureAnalysis = {
        id: `mediapipe_${Date.now()}`,
        timestamp: new Date(),
        type: 'static',
        imageUrl: URL.createObjectURL(blob),
        measurements: {
          headForwardAngle: parseFloat(analysis.match(/頭部前方位: ([\d.]+)度/)?.[1] || '0'),
          shoulderHeight: {
            left: 0,
            right: 0,
            difference: parseFloat(analysis.match(/肩の高さ差: ([\d.]+)cm/)?.[1] || '0')
          },
          spinalAlignment: {
            cervical: 0,
            thoracic: 0,
            lumbar: 0
          },
          pelvisPosition: {
            anterior: parseFloat(analysis.match(/骨盤傾斜: ([\d.]+)度/)?.[1] || '0'),
            posterior: 0,
            lateral: 0
          }
        },
        feedback: {
          overall: 'MediaPipeによるリアルタイム姿勢解析結果',
          areas: {
            head: '頭部の位置が分析されました',
            shoulders: '肩の位置とバランスが評価されました',
            spine: 'スパインアライメントが確認されました',
            pelvis: '骨盤の位置が測定されました'
          },
          severity: 'mild',
          futureRisk: 'リアルタイム解析により継続的な姿勢改善が可能です'
        },
        score: 75,
        recommendations: [
          {
            category: 'exercise',
            title: 'リアルタイム姿勢改善',
            description: 'MediaPipeの解析結果に基づく姿勢改善提案',
            priority: 'high'
          }
        ]
      }

      onAnalysisComplete?.(analysisResult)
    }, 'image/jpeg')
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg">
        <div className="p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-800">MediaPipe リアルタイム姿勢解析</h2>
          <p className="text-gray-600 mt-2">
            カメラを使用してリアルタイムで姿勢を分析し、ポーズランドマークを描画します
          </p>
        </div>

        <div className="p-6">
          <div className="grid lg:grid-cols-2 gap-6">
            {/* カメラビュー */}
            <div className="space-y-4">
              <div className="relative bg-black rounded-lg overflow-hidden">
                <video
                  ref={videoRef}
                  className="w-full h-auto"
                  autoPlay
                  playsInline
                  muted
                  style={{ display: isActive ? 'block' : 'none' }}
                />
                <canvas
                  ref={canvasRef}
                  className="absolute top-0 left-0 w-full h-full"
                  style={{ display: isActive ? 'block' : 'none' }}
                />
                {!isActive && (
                  <div className="aspect-video flex items-center justify-center text-white">
                    <div className="text-center">
                      <div className="text-6xl mb-4">📹</div>
                      <p>カメラを起動してください</p>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex space-x-4">
                {!isActive ? (
                  <button
                    onClick={startCamera}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    disabled={!pose}
                  >
                    📹 カメラ開始
                  </button>
                ) : (
                  <>
                    <button
                      onClick={stopCamera}
                      className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                    >
                      ⏹️ 停止
                    </button>
                    <button
                      onClick={() => setShowGuides(v => !v)}
                      className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                    >
                      {showGuides ? 'ガイド非表示' : 'ガイド表示'}
                    </button>
                    <button
                      onClick={captureAnalysis}
                      className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                      disabled={!landmarks}
                    >
                      📸 解析結果を保存
                    </button>
                  </>
                )}
              </div>
            </div>

            {/* 分析結果 */}
            <div className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="font-semibold text-gray-800 mb-4">リアルタイム分析</h3>
                {analysis ? (
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono">
                    {analysis}
                  </pre>
                ) : (
                  <p className="text-gray-500">
                    カメラを起動すると、リアルタイムで姿勢分析が表示されます
                  </p>
                )}
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-800 mb-2">MediaPipe解析の特徴</h4>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• 33個のポーズランドマークを検出</li>
                  <li>• リアルタイムで姿勢を分析</li>
                  <li>• ポーズの接続線とランドマークを描画</li>
                  <li>• 頭部前方位、肩バランス、骨盤傾斜を計算</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div className="p-6 bg-gray-50 border-t">
          <h3 className="font-semibold text-gray-800 mb-3">使用方法</h3>
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <div className="space-y-2">
              <h4 className="font-medium text-gray-700">1. カメラ許可</h4>
              <p className="text-gray-600">
                ブラウザのカメラアクセス許可を有効にしてください
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium text-gray-700">2. 姿勢確認</h4>
              <p className="text-gray-600">
                カメラに全身が映るように立ち、姿勢を確認
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium text-gray-700">3. 分析保存</h4>
              <p className="text-gray-600">
                良い解析結果が得られたら「保存」をクリック
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
