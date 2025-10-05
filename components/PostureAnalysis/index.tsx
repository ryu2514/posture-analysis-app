"use client"

import React, { useState } from 'react'
import StaticPostureAnalysis from './StaticPostureAnalysis'
import FourDirectionAnalysis from './FourDirectionAnalysis'
// import SeatedPostureAnalysis from './SeatedPostureAnalysis'
import DetailedFeedback from './DetailedFeedback'
import PostureReport from './PostureReport'
import MediaPipePoseAnalysis from '../MediaPipe/MediaPipePoseAnalysis'
import { PostureAnalysis } from '@/types/posture'

type AnalysisMode = 'selection' | 'static' | 'fourDirection' | 'seated' | 'mediapipe' | 'result' | 'report'

export default function PostureAnalysisHub() {
  const [mode, setMode] = useState<AnalysisMode>('selection')
  const [analysis, setAnalysis] = useState<PostureAnalysis | null>(null)

  const handleAnalysisComplete = (result: PostureAnalysis) => {
    setAnalysis(result)
    setMode('result')
  }

  const resetToSelection = () => {
    setMode('selection')
    setAnalysis(null)
  }

  const showReport = () => {
    setMode('report')
  }

  if (mode === 'selection') {
    return (
      <div className="min-h-screen">
        {/* Hero */}
        <header className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-b from-indigo-50/70 to-transparent pointer-events-none" />
          <div className="container-base pt-14 pb-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 text-white text-lg">姿</span>
                <span className="text-slate-700 font-semibold">Shisei Navi</span>
              </div>
              <span className="badge">MediaPipe クライアント解析</span>
            </div>
            <div className="mt-10 text-center">
              <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900 text-balance">
                姿勢を可視化し、ケアを加速する
              </h1>
              <p className="mt-4 text-lg text-slate-600 max-w-2xl mx-auto text-balance">
                シンプル操作で高精度な姿勢分析。現場導入しやすいワークフローと見やすいフィードバックを提供します。
              </p>
            </div>
          </div>
        </header>

        {/* Options */}
        <main className="container-base pb-16">
          <div className="grid md:grid-cols-3 gap-6 md:gap-8 mt-6">
            {/* 静的姿勢解析 */}
            <button onClick={() => setMode('static')} className="text-left card card-hover p-6">
              <div className="flex items-start gap-4">
                <div className="text-3xl">📏</div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-slate-900">静的姿勢解析</h3>
                  <p className="mt-1 text-sm text-slate-600">
                    正面/側面の写真で基本的な姿勢評価。頭部前方位、肩高差、脊柱アライメントを分析。
                  </p>
                  <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-600">
                    <span className="badge">CVA測定</span>
                    <span className="badge">肩の高さ左右差</span>
                    <span className="badge">脊柱アライメント</span>
                    <span className="badge">骨盤傾斜角</span>
                  </div>
                </div>
              </div>
              <div className="mt-6">
                <span className="btn-primary w-full">開始する</span>
              </div>
            </button>

            {/* 4方向姿勢解析 */}
            <button onClick={() => setMode('fourDirection')} className="text-left card card-hover p-6">
              <div className="flex items-start gap-4">
                <div className="text-3xl">🔄</div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-slate-900">4方向姿勢解析</h3>
                  <p className="mt-1 text-sm text-slate-600">
                    前後左右4方向の写真で包括的に評価。背骨のカーブや3Dバランスを詳細分析。
                  </p>
                  <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-600">
                    <span className="badge">360°評価</span>
                    <span className="badge">脊柱カーブ</span>
                    <span className="badge">多角比較</span>
                  </div>
                </div>
              </div>
              <div className="mt-6">
                <span className="btn-secondary w-full">開始する</span>
              </div>
            </button>

            {/* MediaPipe リアルタイム解析 */}
            <button onClick={() => setMode('mediapipe')} className="text-left card card-hover p-6">
              <div className="flex items-start gap-4">
                <div className="text-3xl">📹</div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-slate-900">MediaPipe 解析</h3>
                  <p className="mt-1 text-sm text-slate-600">
                    カメラを使ったリアルタイム解析。ランドマーク描画と即時フィードバック。
                  </p>
                  <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-600">
                    <span className="badge">リアルタイム</span>
                    <span className="badge">ブラウザ内処理</span>
                    <span className="badge">鍵不要</span>
                  </div>
                </div>
              </div>
              <div className="mt-6">
                <span className="btn-primary w-full">開始する</span>
              </div>
            </button>
          </div>

          {/* Highlights */}
          <section className="mt-14 grid md:grid-cols-4 gap-4 text-slate-700">
            <div className="card p-5 text-center">
              <div className="text-2xl mb-2">🤖</div>
              <h4 className="font-semibold">AI高精度解析</h4>
              <p className="text-sm text-slate-600 mt-1">必要に応じてAI解析に拡張可能</p>
            </div>
            <div className="card p-5 text-center">
              <div className="text-2xl mb-2">📊</div>
              <h4 className="font-semibold">詳細レポート</h4>
              <p className="text-sm text-slate-600 mt-1">印刷対応のレポート生成</p>
            </div>
            <div className="card p-5 text-center">
              <div className="text-2xl mb-2">🎯</div>
              <h4 className="font-semibold">個別改善提案</h4>
              <p className="text-sm text-slate-600 mt-1">エクササイズ提案に接続</p>
            </div>
            <div className="card p-5 text-center">
              <div className="text-2xl mb-2">⚡</div>
              <h4 className="font-semibold">即座の結果</h4>
              <p className="text-sm text-slate-600 mt-1">数秒で可視化・共有</p>
            </div>
          </section>
        </main>
      </div>
    )
  }

  if (mode === 'static') {
    return <StaticPostureAnalysis onAnalysisComplete={handleAnalysisComplete} />
  }

  if (mode === 'fourDirection') {
    return <FourDirectionAnalysis onAnalysisComplete={handleAnalysisComplete} />
  }

  if (mode === 'seated') {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-4xl mx-auto p-6 text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">座位姿勢解析</h2>
          <p className="text-gray-600 mb-4">この機能は現在メンテナンス中です。</p>
          <button
            onClick={resetToSelection}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            戻る
          </button>
        </div>
      </div>
    )
  }

  if (mode === 'mediapipe') {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white border-b px-6 py-4">
          <div className="flex justify-between items-center max-w-6xl mx-auto">
            <button
              onClick={resetToSelection}
              className="flex items-center text-gray-600 hover:text-gray-800 transition-colors"
            >
              ← 戻る
            </button>
          </div>
        </div>
        <MediaPipePoseAnalysis onAnalysisComplete={handleAnalysisComplete} />
      </div>
    )
  }

  if (mode === 'result' && analysis) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white border-b px-6 py-4">
          <div className="flex justify-between items-center max-w-6xl mx-auto">
            <button
              onClick={resetToSelection}
              className="flex items-center text-gray-600 hover:text-gray-800 transition-colors"
            >
              ← 戻る
            </button>
            <div className="flex space-x-4">
              <button
                onClick={showReport}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                📄 詳細レポート表示
              </button>
            </div>
          </div>
        </div>
        <DetailedFeedback analysis={analysis} />
      </div>
    )
  }

  if (mode === 'report' && analysis) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white border-b px-6 py-4 print:hidden">
          <div className="flex justify-between items-center max-w-6xl mx-auto">
            <button
              onClick={() => setMode('result')}
              className="flex items-center text-gray-600 hover:text-gray-800 transition-colors"
            >
              ← 解析結果に戻る
            </button>
          </div>
        </div>
        <PostureReport analysis={analysis} />
      </div>
    )
  }

  return null
}
