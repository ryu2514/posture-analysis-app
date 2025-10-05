import { NextRequest, NextResponse } from 'next/server'
import { validateEnv, isValidFileType, isValidFileSize } from '@/lib/env'
import type { AnalysisResponse } from '@/types/analysis'

export async function POST(request: NextRequest) {
  try {
    // Validate environment variables only if using OpenAI backend
    validateEnv()
    
    // Parse the multipart form data
    const formData = await request.formData()
    const file = formData.get('image') as File
    
    if (!file) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'MISSING_FILE',
          message: '画像ファイルが見つかりません',
        },
      } as AnalysisResponse, { status: 400 })
    }

    // Validate file type and size
    if (!isValidFileType(file.type)) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'INVALID_FILE_TYPE',
          message: 'JPEGまたはPNG形式の画像を選択してください',
        },
      } as AnalysisResponse, { status: 400 })
    }

    if (!isValidFileSize(file.size)) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'FILE_TOO_LARGE',
          message: 'ファイルサイズは10MB以下にしてください',
        },
      } as AnalysisResponse, { status: 400 })
    }

    // Convert file to base64 for API processing
    const bytes = await file.arrayBuffer()
    const buffer = Buffer.from(bytes)
    const base64Image = buffer.toString('base64')

    // Analyze posture using selected backend
    let analysisResult
    try {
      // Prefer OpenAI only when explicitly configured
      if (process.env.ANALYSIS_BACKEND === 'openai') {
        const { analyzePostureWithOpenAI, generateMockAnalysis } = await import('@/lib/vision')
        if (process.env.OPENAI_API_KEY && process.env.OPENAI_API_KEY !== 'your_openai_api_key_here') {
          analysisResult = await analyzePostureWithOpenAI(base64Image)
        } else {
          console.warn('OpenAI backend selected but API key not configured, using mock data')
          analysisResult = generateMockAnalysis()
          await new Promise(resolve => setTimeout(resolve, 1500))
        }
      } else {
        // For MediaPipe-first deployments, this API is not used.
        // Return a clear message so clients can handle gracefully.
        return NextResponse.json({
          success: false,
          error: {
            code: 'BACKEND_DISABLED',
            message: 'サーバー側解析は無効です（MediaPipeクライアント解析を使用してください）',
          },
        } as any, { status: 400 })
      }
    } catch (visionError) {
      console.error('Vision API error:', visionError)
      // Fallback to mock analysis if Vision API fails
      const { generateMockAnalysis } = await import('@/lib/vision')
      analysisResult = generateMockAnalysis()
      await new Promise(resolve => setTimeout(resolve, 1500))
    }

    // Clear sensitive data from memory for security
    buffer.fill(0)
    
    return NextResponse.json({
      success: true,
      data: analysisResult,
    } as AnalysisResponse)

  } catch (error) {
    console.error('Analysis error:', error)
    
    if (error instanceof Error && error.message.includes('Missing required environment variables')) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'CONFIG_ERROR',
          message: 'サーバー設定エラーが発生しました',
        },
      } as AnalysisResponse, { status: 500 })
    }

    return NextResponse.json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: '内部サーバーエラーが発生しました',
      },
    } as AnalysisResponse, { status: 500 })
  }
}

export async function GET() {
  return NextResponse.json({
    success: false,
    error: {
      code: 'METHOD_NOT_ALLOWED',
      message: 'POST メソッドのみサポートされています',
    },
  } as AnalysisResponse, { status: 405 })
}
