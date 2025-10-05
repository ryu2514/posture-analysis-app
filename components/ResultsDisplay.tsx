import { ScoreGauge } from './ui/ScoreGauge'
import type { PostureAnalysis } from '@/types/analysis'

interface ResultsDisplayProps {
  results: PostureAnalysis
  onNewAnalysis: () => void
}

export function ResultsDisplay({ results, onNewAnalysis }: ResultsDisplayProps) {
  const { score, metrics, recommendations } = results

  return (
    <div className="w-full max-w-4xl mx-auto space-y-8">
      {/* Overall Score */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">総合姿勢スコア</h2>
          <p className="text-gray-600">0点〜100点で評価されます</p>
        </div>
        
        <div className="flex justify-center">
          <ScoreGauge
            score={score}
            size="lg"
            label="総合スコア"
          />
        </div>
        
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            {score >= 85 && '優秀な姿勢です！この状態を維持しましょう。'}
            {score >= 70 && score < 85 && '良好な姿勢ですが、さらなる改善の余地があります。'}
            {score >= 50 && score < 70 && '姿勢に問題があります。改善に取り組みましょう。'}
            {score < 50 && '姿勢に重大な問題があります。専門家への相談をお勧めします。'}
          </p>
        </div>
      </div>

      {/* Detailed Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Head Forward Position */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="text-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">頭部前方位</h3>
            <p className="text-sm text-gray-600">CVA角度の評価</p>
          </div>
          
          <div className="flex justify-center mb-4">
            <ScoreGauge
              score={metrics.headForwardPosition.score}
              size="md"
              severity={metrics.headForwardPosition.severity}
            />
          </div>
          
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">測定角度:</span>
              <span className="font-medium">{metrics.headForwardPosition.angle}°</span>
            </div>
            <div className="text-xs text-gray-500">
              正常範囲: 45-55°
            </div>
          </div>
        </div>

        {/* Shoulder Height */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="text-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">肩の高さ</h3>
            <p className="text-sm text-gray-600">左右差の評価</p>
          </div>
          
          <div className="flex justify-center mb-4">
            <ScoreGauge
              score={metrics.shoulderHeight.score}
              size="md"
              severity={metrics.shoulderHeight.severity}
            />
          </div>
          
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">左右差:</span>
              <span className="font-medium">{metrics.shoulderHeight.difference}px</span>
            </div>
            <div className="text-xs text-gray-500">
              理想値: 5px以下の差
            </div>
          </div>
        </div>

        {/* Spine Alignment */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="text-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">脊柱アライメント</h3>
            <p className="text-sm text-gray-600">姿勢バランス</p>
          </div>
          
          <div className="flex justify-center mb-4">
            <ScoreGauge
              score={metrics.spineAlignment.score}
              size="md"
              severity={metrics.spineAlignment.severity}
            />
          </div>
          
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">偏位角度:</span>
              <span className="font-medium">{metrics.spineAlignment.deviation}°</span>
            </div>
            <div className="text-xs text-gray-500">
              理想値: 5°以下の偏位
            </div>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">改善提案</h3>
        <div className="space-y-3">
          {recommendations.map((recommendation, index) => (
            <div key={index} className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">
                {index + 1}
              </div>
              <p className="text-gray-700">{recommendation}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button
          onClick={onNewAnalysis}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          新しい分析を行う
        </button>
        
        <button
          onClick={() => window.print()}
          className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
        >
          結果を印刷
        </button>
      </div>

      {/* Disclaimer */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">免責事項</h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>
                この分析結果は参考値であり、医学的診断ではありません。
                姿勢に関する問題がある場合は、理学療法士などの専門家にご相談ください。
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}