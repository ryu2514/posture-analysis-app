"use client"

import React from 'react'
import { PostureAnalysis, Recommendation } from '@/types/posture'

interface DetailedFeedbackProps {
  analysis: PostureAnalysis
}

export default function DetailedFeedback({ analysis }: DetailedFeedbackProps) {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'normal': return 'text-green-600 bg-green-100'
      case 'mild': return 'text-yellow-600 bg-yellow-100'
      case 'moderate': return 'text-orange-600 bg-orange-100'
      case 'severe': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    if (score >= 40) return 'text-orange-600'
    return 'text-red-600'
  }

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high': return '🔴'
      case 'medium': return '🟡'
      case 'low': return '🟢'
      default: return '⚪'
    }
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-8">
      {/* 総合スコアと概要 */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-800">姿勢解析結果</h2>
          <div className="text-right">
            <div className="text-sm text-gray-500">解析日時</div>
            <div className="text-gray-700">
              {analysis.timestamp.toLocaleString('ja-JP')}
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-6">
          <div className="text-center p-6 bg-gray-50 rounded-lg">
            <div className={`text-4xl font-bold mb-2 ${getScoreColor(analysis.score)}`}>
              {analysis.score}
            </div>
            <div className="text-sm text-gray-600">総合スコア</div>
            <div className="text-xs text-gray-500 mt-1">（100点満点）</div>
          </div>
          
          <div className="text-center p-6 bg-gray-50 rounded-lg">
            <div className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${getSeverityColor(analysis.feedback.severity)}`}>
              {analysis.feedback.severity === 'normal' && '正常'}
              {analysis.feedback.severity === 'mild' && '軽度'}
              {analysis.feedback.severity === 'moderate' && '中等度'}
              {analysis.feedback.severity === 'severe' && '重度'}
            </div>
            <div className="text-sm text-gray-600 mt-2">重症度</div>
          </div>
          
          <div className="text-center p-6 bg-gray-50 rounded-lg">
            <div className="text-2xl mb-2">
              {analysis.type === 'static' && '📏'}
              {analysis.type === 'fourDirection' && '🔄'}
              {analysis.type === 'seated' && '🪑'}
            </div>
            <div className="text-sm text-gray-600">解析種別</div>
            <div className="text-xs text-gray-500 mt-1">
              {analysis.type === 'static' && '静的姿勢'}
              {analysis.type === 'fourDirection' && '4方向解析'}
              {analysis.type === 'seated' && '座位姿勢'}
            </div>
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-800 mb-2">📋 総合評価</h3>
          <p className="text-blue-700 text-sm leading-relaxed">
            {analysis.feedback.overall}
          </p>
        </div>
      </div>

      {/* 詳細な部位別フィードバック */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-6">部位別詳細分析</h3>
        
        <div className="grid md:grid-cols-2 gap-6">
          {Object.entries(analysis.feedback.areas).map(([area, feedback]) => (
            <div key={area} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center mb-3">
                <div className="text-2xl mr-3">
                  {area === 'head' && '🧠'}
                  {area === 'shoulders' && '💪'}
                  {area === 'spine' && '🦴'}
                  {area === 'pelvis' && '🫗'}
                </div>
                <h4 className="font-semibold text-gray-800">
                  {area === 'head' && '頭部・頸部'}
                  {area === 'shoulders' && '肩・肩甲骨'}
                  {area === 'spine' && '脊柱・背骨'}
                  {area === 'pelvis' && '骨盤・腰部'}
                </h4>
              </div>
              <p className="text-sm text-gray-600 leading-relaxed">
                {feedback}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* 数値データ（4方向解析の場合） */}
      {analysis.type === 'fourDirection' && 'directions' in analysis.measurements && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-6">4方向計測データ</h3>
          
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries((analysis.measurements as any).directions).map(([direction, data]: [string, any]) => (
              <div key={direction} className="border border-gray-200 rounded-lg p-4">
                <h4 className="font-medium text-gray-700 mb-3 text-center">
                  {direction === 'front' && '正面'}
                  {direction === 'back' && '背面'}
                  {direction === 'leftSide' && '左側面'}
                  {direction === 'rightSide' && '右側面'}
                </h4>
                <div className="space-y-2 text-xs">
                  {data.headForwardAngle > 0 && (
                    <div>頭部前方位: {data.headForwardAngle.toFixed(1)}°</div>
                  )}
                  {data.shoulderHeight.difference > 0 && (
                    <div>肩の高さ差: {data.shoulderHeight.difference.toFixed(1)}cm</div>
                  )}
                  <div>胸椎角度: {data.spinalAlignment.thoracic.toFixed(1)}°</div>
                  <div>腰椎角度: {data.spinalAlignment.lumbar.toFixed(1)}°</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 将来のリスク */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">⚠️ 将来のリスク予測</h3>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800 text-sm leading-relaxed">
            {analysis.feedback.futureRisk}
          </p>
        </div>
      </div>

      {/* 改善提案 */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-6">🎯 個別改善プログラム</h3>
        
        <div className="space-y-6">
          {analysis.recommendations.map((recommendation, index) => (
            <RecommendationCard 
              key={index} 
              recommendation={recommendation} 
              index={index}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

function RecommendationCard({ recommendation, index }: { recommendation: Recommendation; index: number }) {
  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'exercise': return '🏃‍♀️'
      case 'ergonomics': return '🪑'
      case 'lifestyle': return '🌱'
      default: return '📋'
    }
  }

  const getCategoryName = (category: string) => {
    switch (category) {
      case 'exercise': return 'エクササイズ'
      case 'ergonomics': return '環境改善'
      case 'lifestyle': return '生活習慣'
      default: return 'その他'
    }
  }

  return (
    <div className="border border-gray-200 rounded-lg p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center">
          <div className="text-2xl mr-3">{getCategoryIcon(recommendation.category)}</div>
          <div>
            <h4 className="font-semibold text-gray-800">{recommendation.title}</h4>
            <div className="flex items-center space-x-2 mt-1">
              <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                {getCategoryName(recommendation.category)}
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center">
          <span className="mr-2">{getPriorityIcon(recommendation.priority)}</span>
          <span className="text-xs text-gray-500">
            {recommendation.priority === 'high' && '高優先度'}
            {recommendation.priority === 'medium' && '中優先度'}
            {recommendation.priority === 'low' && '低優先度'}
          </span>
        </div>
      </div>

      <p className="text-gray-600 text-sm mb-4 leading-relaxed">
        {recommendation.description}
      </p>

      {recommendation.exercises && recommendation.exercises.length > 0 && (
        <div className="mt-4">
          <h5 className="font-medium text-gray-700 mb-3">推奨エクササイズ</h5>
          <div className="space-y-3">
            {recommendation.exercises.map((exercise, exerciseIndex) => (
              <div key={exerciseIndex} className="bg-gray-50 rounded-lg p-4">
                <div className="font-medium text-gray-800 mb-2">{exercise.name}</div>
                <div className="text-sm text-gray-600 mb-3">{exercise.description}</div>
                <div className="flex space-x-4 text-xs text-gray-500">
                  <span>🔢 {exercise.sets} セット</span>
                  <span>🔄 {exercise.reps} 回</span>
                  {exercise.duration && <span>⏱️ {exercise.duration} 秒キープ</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function getPriorityIcon(priority: string) {
  switch (priority) {
    case 'high': return '🔴'
    case 'medium': return '🟡'
    case 'low': return '🟢'
    default: return '⚪'
  }
}