'use client'

import { useState } from 'react'
import { ImageUpload } from './ui/ImageUpload'
import { Alert } from './ui/Alert'

interface UploadFormProps {
  onAnalyze: (file: File) => Promise<void>
}

export function UploadForm({ onAnalyze }: UploadFormProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleImageSelect = (file: File) => {
    setSelectedFile(file)
    setError(null)
  }

  const handleError = (errorMessage: string) => {
    setError(errorMessage)
    setSelectedFile(null)
  }

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError('画像を選択してください')
      return
    }

    try {
      setIsAnalyzing(true)
      setError(null)
      await onAnalyze(selectedFile)
    } catch (err) {
      setError(err instanceof Error ? err.message : '分析中にエラーが発生しました')
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">姿勢分析</h2>
        
        <div className="space-y-6">
          <ImageUpload
            onImageSelect={handleImageSelect}
            onError={handleError}
            isLoading={isAnalyzing}
          />

          {error && (
            <Alert
              type="error"
              message={error}
              onClose={() => setError(null)}
            />
          )}

          {selectedFile && (
            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className={`
                  flex-1 py-3 px-6 rounded-lg font-medium transition-all
                  ${
                    isAnalyzing
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-blue-600 hover:bg-blue-700 active:bg-blue-800'
                  }
                  text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                `}
              >
                {isAnalyzing ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    分析中...
                  </span>
                ) : (
                  '姿勢を分析する'
                )}
              </button>
              
              <button
                onClick={() => {
                  setSelectedFile(null)
                  setError(null)
                }}
                disabled={isAnalyzing}
                className="px-6 py-3 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                クリア
              </button>
            </div>
          )}
        </div>

        <div className="mt-8 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-2">撮影のコツ</h3>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• 全身が写るように2.5m程度離れて撮影</li>
            <li>• 側面（横向き）での撮影が推奨</li>
            <li>• 背景はシンプルで明るい場所</li>
            <li>• 耳珠（耳の穴の前の突起）が見えるように</li>
          </ul>
        </div>
      </div>
    </div>
  )
}