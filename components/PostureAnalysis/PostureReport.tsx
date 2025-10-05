"use client"

import React, { forwardRef, useRef } from 'react'
import { PostureAnalysis } from '@/types/posture'
import QRCode from 'qrcode'

interface PostureReportProps {
  analysis: PostureAnalysis
  onPrint?: () => void
}

const PostureReport = forwardRef<HTMLDivElement, PostureReportProps>(
  ({ analysis, onPrint }, ref) => {
    const [qrCodeUrl, setQrCodeUrl] = React.useState<string>('')

    React.useEffect(() => {
      const generateQR = async () => {
        try {
          const reportUrl = `${window.location.origin}/report/${analysis.id}`
          const qr = await QRCode.toDataURL(reportUrl, {
            width: 120,
            margin: 1,
            color: {
              dark: '#000000',
              light: '#FFFFFF'
            }
          })
          setQrCodeUrl(qr)
        } catch (error) {
          console.error('QRコード生成エラー:', error)
        }
      }
      generateQR()
    }, [analysis.id])

    const handlePrint = () => {
      window.print()
      onPrint?.()
    }

    const getSeverityText = (severity: string) => {
      switch (severity) {
        case 'normal': return '正常'
        case 'mild': return '軽度'
        case 'moderate': return '中等度'
        case 'severe': return '重度'
        default: return '不明'
      }
    }

    const getAnalysisTypeText = (type: string) => {
      switch (type) {
        case 'static': return '静的姿勢解析'
        case 'fourDirection': return '4方向姿勢解析'
        case 'seated': return '座位姿勢解析'
        default: return '姿勢解析'
      }
    }

    return (
      <div className="bg-white">
        {/* 印刷ボタン（印刷時は非表示） */}
        <div className="print:hidden p-6 border-b">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-800">姿勢解析レポート</h2>
            <div className="space-x-4">
              <button
                onClick={handlePrint}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                🖨️ 印刷する
              </button>
              <button
                onClick={() => {
                  const url = URL.createObjectURL(new Blob([document.documentElement.outerHTML], { type: 'text/html' }))
                  const a = document.createElement('a')
                  a.href = url
                  a.download = `姿勢解析レポート_${analysis.timestamp.toISOString().split('T')[0]}.html`
                  a.click()
                  URL.revokeObjectURL(url)
                }}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                💾 保存する
              </button>
            </div>
          </div>
        </div>

        {/* レポート本体 */}
        <div ref={ref} className="p-8 print:p-6 print:text-black">
          {/* ヘッダー */}
          <div className="border-b-2 border-gray-800 pb-6 mb-8">
            <div className="flex justify-between items-start">
              <div>
                <h1 className="text-3xl font-bold text-gray-800 mb-2">姿勢分析レポート</h1>
                <p className="text-lg text-gray-600">{getAnalysisTypeText(analysis.type)}</p>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-500 mb-1">解析日時</div>
                <div className="font-medium text-gray-800">
                  {analysis.timestamp.toLocaleString('ja-JP', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
                <div className="text-sm text-gray-500 mt-2">ID: {analysis.id}</div>
              </div>
            </div>
          </div>

          {/* 総合評価セクション */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="text-center p-6 border-2 border-gray-200 rounded-lg">
              <div className="text-4xl font-bold text-blue-600 mb-2">{analysis.score}</div>
              <div className="text-sm text-gray-600 font-medium">総合スコア</div>
              <div className="text-xs text-gray-500">（100点満点）</div>
            </div>
            
            <div className="text-center p-6 border-2 border-gray-200 rounded-lg">
              <div className="text-2xl font-bold text-orange-600 mb-2">
                {getSeverityText(analysis.feedback.severity)}
              </div>
              <div className="text-sm text-gray-600 font-medium">重症度評価</div>
            </div>
            
            <div className="text-center p-6 border-2 border-gray-200 rounded-lg">
              <div className="text-2xl mb-2">
                {analysis.type === 'static' && '📏'}
                {analysis.type === 'fourDirection' && '🔄'}
                {analysis.type === 'seated' && '🪑'}
              </div>
              <div className="text-sm text-gray-600 font-medium">解析種別</div>
            </div>
          </div>

          {/* 総合評価コメント */}
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-800 mb-4">総合評価</h2>
            <div className="border-l-4 border-blue-500 pl-4 py-2 bg-blue-50 print:bg-gray-100">
              <p className="text-gray-700 leading-relaxed">{analysis.feedback.overall}</p>
            </div>
          </div>

          {/* 部位別詳細評価 */}
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-800 mb-4">部位別詳細評価</h2>
            <div className="space-y-4">
              {Object.entries(analysis.feedback.areas).map(([area, feedback]) => (
                <div key={area} className="border border-gray-200 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-800 mb-2">
                    {area === 'head' && '頭部・頸部'}
                    {area === 'shoulders' && '肩・肩甲骨'}
                    {area === 'spine' && '脊柱・背骨'}
                    {area === 'pelvis' && '骨盤・腰部'}
                  </h3>
                  <p className="text-gray-600 text-sm leading-relaxed">{feedback}</p>
                </div>
              ))}
            </div>
          </div>

          {/* 計測データ（4方向解析の場合） */}
          {analysis.type === 'fourDirection' && 'directions' in analysis.measurements && (
            <div className="mb-8">
              <h2 className="text-xl font-bold text-gray-800 mb-4">詳細計測データ</h2>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse border border-gray-300 text-sm">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="border border-gray-300 px-3 py-2 text-left">計測項目</th>
                      <th className="border border-gray-300 px-3 py-2 text-center">正面</th>
                      <th className="border border-gray-300 px-3 py-2 text-center">背面</th>
                      <th className="border border-gray-300 px-3 py-2 text-center">左側面</th>
                      <th className="border border-gray-300 px-3 py-2 text-center">右側面</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="border border-gray-300 px-3 py-2 font-medium">頭部前方位角度</td>
                      <td className="border border-gray-300 px-3 py-2 text-center">
                        {(analysis.measurements as any).directions.front.headForwardAngle.toFixed(1)}°
                      </td>
                      <td className="border border-gray-300 px-3 py-2 text-center">-</td>
                      <td className="border border-gray-300 px-3 py-2 text-center">
                        {(analysis.measurements as any).directions.leftSide.headForwardAngle.toFixed(1)}°
                      </td>
                      <td className="border border-gray-300 px-3 py-2 text-center">
                        {(analysis.measurements as any).directions.rightSide.headForwardAngle.toFixed(1)}°
                      </td>
                    </tr>
                    <tr className="bg-gray-50">
                      <td className="border border-gray-300 px-3 py-2 font-medium">胸椎角度</td>
                      <td className="border border-gray-300 px-3 py-2 text-center">
                        {(analysis.measurements as any).directions.front.spinalAlignment.thoracic.toFixed(1)}°
                      </td>
                      <td className="border border-gray-300 px-3 py-2 text-center">
                        {(analysis.measurements as any).directions.back.spinalAlignment.thoracic.toFixed(1)}°
                      </td>
                      <td className="border border-gray-300 px-3 py-2 text-center">
                        {(analysis.measurements as any).directions.leftSide.spinalAlignment.thoracic.toFixed(1)}°
                      </td>
                      <td className="border border-gray-300 px-3 py-2 text-center">
                        {(analysis.measurements as any).directions.rightSide.spinalAlignment.thoracic.toFixed(1)}°
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 改善提案 */}
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-800 mb-4">改善提案プログラム</h2>
            <div className="space-y-6">
              {analysis.recommendations.map((recommendation, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="font-semibold text-gray-800">{recommendation.title}</h3>
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                      {recommendation.priority === 'high' && '高優先度'}
                      {recommendation.priority === 'medium' && '中優先度'}
                      {recommendation.priority === 'low' && '低優先度'}
                    </span>
                  </div>
                  <p className="text-gray-600 text-sm mb-4 leading-relaxed">
                    {recommendation.description}
                  </p>

                  {recommendation.exercises && recommendation.exercises.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">推奨エクササイズ</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {recommendation.exercises.map((exercise, exerciseIndex) => (
                          <div key={exerciseIndex} className="bg-gray-50 print:bg-gray-100 rounded p-3">
                            <div className="font-medium text-gray-800 text-sm mb-1">
                              {exercise.name}
                            </div>
                            <div className="text-xs text-gray-600 mb-2">
                              {exercise.description}
                            </div>
                            <div className="text-xs text-gray-500">
                              {exercise.sets}セット × {exercise.reps}回
                              {exercise.duration && ` (${exercise.duration}秒キープ)`}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* 将来のリスク */}
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-800 mb-4">将来のリスク予測</h2>
            <div className="border-l-4 border-yellow-500 pl-4 py-2 bg-yellow-50 print:bg-gray-100">
              <p className="text-gray-700 leading-relaxed">{analysis.feedback.futureRisk}</p>
            </div>
          </div>

          {/* フッター */}
          <div className="border-t-2 border-gray-800 pt-6 mt-8">
            <div className="flex justify-between items-end">
              <div>
                <div className="text-sm text-gray-600 mb-2">
                  本レポートは AI による姿勢解析結果です。<br />
                  詳細な診断や治療については専門医にご相談ください。
                </div>
                <div className="text-xs text-gray-500">
                  Generated by 姿勢分析アプリ (Shisei Navi)
                </div>
              </div>
              
              {qrCodeUrl && (
                <div className="text-center">
                  <img src={qrCodeUrl} alt="QRコード" className="w-24 h-24 mx-auto mb-2" />
                  <div className="text-xs text-gray-500">
                    オンライン版はこちら
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 印刷用スタイル */}
        <style jsx>{`
          @media print {
            body { margin: 0; }
            .print\\:hidden { display: none !important; }
            .print\\:p-6 { padding: 1.5rem !important; }
            .print\\:text-black { color: black !important; }
            .print\\:bg-gray-100 { background-color: #f3f4f6 !important; }
            @page {
              margin: 2cm;
              size: A4;
            }
          }
        `}</style>
      </div>
    )
  }
)

PostureReport.displayName = 'PostureReport'

export default PostureReport