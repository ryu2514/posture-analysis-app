'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { isValidFileType, isValidFileSize } from '@/lib/env'

interface ImageUploadProps {
  onImageSelect: (file: File) => void
  onError: (error: string) => void
  isLoading?: boolean
}

export function ImageUpload({ onImageSelect, onError, isLoading = false }: ImageUploadProps) {
  const [preview, setPreview] = useState<string | null>(null)

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      if (rejectedFiles.length > 0) {
        const rejection = rejectedFiles[0]
        if (rejection.errors[0]?.code === 'file-too-large') {
          onError('ファイルサイズは10MB以下にしてください')
        } else if (rejection.errors[0]?.code === 'file-invalid-type') {
          onError('JPEGまたはPNG形式の画像を選択してください')
        } else {
          onError('無効なファイルです')
        }
        return
      }

      const file = acceptedFiles[0]
      if (!file) return

      // Double-check validations
      if (!isValidFileType(file.type)) {
        onError('JPEGまたはPNG形式の画像を選択してください')
        return
      }

      if (!isValidFileSize(file.size)) {
        onError('ファイルサイズは10MB以下にしてください')
        return
      }

      // Create preview
      const reader = new FileReader()
      reader.onload = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(file)

      onImageSelect(file)
    },
    [onImageSelect, onError]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false,
    disabled: isLoading,
  })

  const clearImage = () => {
    setPreview(null)
  }

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all
          ${
            isDragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }
          ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        {preview ? (
          <div className="space-y-4">
            <div className="relative inline-block">
              <img
                src={preview}
                alt="アップロード予定の画像"
                className="max-w-full max-h-64 mx-auto rounded-lg shadow-md"
              />
              {!isLoading && (
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    clearImage()
                  }}
                  className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors"
                  aria-label="画像を削除"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
            {!isLoading && (
              <p className="text-sm text-gray-600">
                別の画像を選択する場合は、ここをクリックまたはドラッグ&ドロップしてください
              </p>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex justify-center">
              <svg
                className="w-12 h-12 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
            </div>
            <div>
              <p className="text-lg font-medium text-gray-900">
                {isDragActive ? '画像をドロップしてください' : '画像をアップロード'}
              </p>
              <p className="text-sm text-gray-600 mt-2">
                クリックして選択 または ドラッグ&ドロップ
              </p>
              <p className="text-xs text-gray-500 mt-1">
                JPEGまたはPNG形式 / 最大10MB
              </p>
            </div>
          </div>
        )}

        {isLoading && (
          <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center rounded-lg">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        )}
      </div>
    </div>
  )
}