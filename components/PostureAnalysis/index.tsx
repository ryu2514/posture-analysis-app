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
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-6xl mx-auto p-6">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-800 mb-4">
              AI姿勢解析システム
            </h1>
            <p className="text-xl text-gray-600 mb-2">
              Sportip Pro類似機能 - 理学療法士向け専門ツール
            </p>
            <p className="text-gray-500">
              写真から高精度な姿勢分析を行い、個人に最適化された改善プログラムを提供します
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* 静的姿勢解析 */}
            <div 
              className="bg-white rounded-lg shadow-lg p-8 cursor-pointer hover:shadow-xl transition-all transform hover:-translate-y-1"
              onClick={() => setMode('static')}
            >
              <div className="text-center">
                <div className="text-6xl mb-4">📏</div>
                <h3 className="text-xl font-bold text-gray-800 mb-3">静的姿勢解析</h3>
                <p className="text-gray-600 text-sm mb-6 leading-relaxed">
                  正面または側面からの写真で基本的な姿勢評価を行います。
                  頭部前方位、肩の高さ差、脊柱アライメントを分析。
                </p>
                <div className="space-y-2 text-xs text-gray-500">
                  <div>✓ 頭部前方位（CVA）測定</div>
                  <div>✓ 肩の高さ左右差評価</div>
                  <div>✓ 脊柱アライメント分析</div>
                  <div>✓ 骨盤傾斜角度測定</div>
                </div>
                <button className="mt-6 w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors">
                  開始する
                </button>
              </div>
            </div>

            {/* 4方向姿勢解析 */}
            <div 
              className="bg-white rounded-lg shadow-lg p-8 cursor-pointer hover:shadow-xl transition-all transform hover:-translate-y-1"
              onClick={() => setMode('fourDirection')}
            >
              <div className="text-center">
                <div className="text-6xl mb-4">🔄</div>
                <h3 className="text-xl font-bold text-gray-800 mb-3">4方向姿勢解析</h3>
                <p className="text-gray-600 text-sm mb-6 leading-relaxed">
                  前後左右4方向から撮影した写真で包括的な姿勢評価。
                  背骨のカーブや3D的な姿勢バランスを詳細分析。
                </p>
                <div className="space-y-2 text-xs text-gray-500">
                  <div>✓ 360度姿勢バランス評価</div>
                  <div>✓ 脊柱カーブ詳細測定</div>
                  <div>✓ 背骨アーチ推定</div>
                  <div>✓ 多角度からの比較分析</div>
                </div>
                <button className="mt-6 w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition-colors">
                  開始する
                </button>
              </div>
            </div>


            {/* MediaPipe リアルタイム解析 */}
            <div 
              className="bg-white rounded-lg shadow-lg p-8 cursor-pointer hover:shadow-xl transition-all transform hover:-translate-y-1"
              onClick={() => setMode('mediapipe')}
            >
              <div className="text-center">
                <div className="text-6xl mb-4">📹</div>
                <h3 className="text-xl font-bold text-gray-800 mb-3">MediaPipe 解析</h3>
                <p className="text-gray-600 text-sm mb-6 leading-relaxed">
                  カメラを使用したリアルタイム姿勢解析。
                  ポーズランドマークの描画と即座の姿勢フィードバック。
                </p>
                <div className="space-y-2 text-xs text-gray-500">
                  <div>✓ リアルタイムポーズ検出</div>
                  <div>✓ 33個のランドマーク描画</div>
                  <div>✓ 即座の姿勢フィードバック</div>
                  <div>✓ 解析結果の保存機能</div>
                </div>
                <button className="mt-6 w-full bg-red-600 text-white py-2 rounded-lg hover:bg-red-700 transition-colors">
                  開始する
                </button>
              </div>
            </div>
          </div>

          {/* システムの特徴 */}
          <div className="mt-16">
            <h2 className="text-2xl font-bold text-gray-800 text-center mb-8">システムの特徴</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl mb-3">🤖</div>
                <h4 className="font-semibold text-gray-800 mb-2">AI高精度解析</h4>
                <p className="text-sm text-gray-600">
                  OpenAI Vision APIを使用した高精度な画像解析
                </p>
              </div>
              <div className="text-center">
                <div className="text-3xl mb-3">📊</div>
                <h4 className="font-semibold text-gray-800 mb-2">詳細レポート</h4>
                <p className="text-sm text-gray-600">
                  印刷対応・QRコード付きの詳細分析レポート
                </p>
              </div>
              <div className="text-center">
                <div className="text-3xl mb-3">🎯</div>
                <h4 className="font-semibold text-gray-800 mb-2">個別改善提案</h4>
                <p className="text-sm text-gray-600">
                  個人に最適化されたエクササイズプログラム
                </p>
              </div>
              <div className="text-center">
                <div className="text-3xl mb-3">⚡</div>
                <h4 className="font-semibold text-gray-800 mb-2">即座の結果</h4>
                <p className="text-sm text-gray-600">
                  写真アップロード後、数秒で解析完了
                </p>
              </div>
            </div>
          </div>
        </div>
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