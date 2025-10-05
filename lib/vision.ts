import OpenAI from 'openai'
import { env } from './env'

const openai = new OpenAI({
  apiKey: env.OPENAI_API_KEY,
})

export interface PostureAnalysisPrompt {
  imageData: string // base64 encoded image
}

export async function analyzePostureWithOpenAI(
  imageData: string
): Promise<any> {
  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [
        {
          role: 'system',
          content: `あなたは理学療法士の専門家です。提供された側面（横向き）の人体画像を分析し、姿勢評価を行ってください。

以下の項目を JSON 形式で分析し、返してください：

1. 頭部前方位（Forward Head Posture）:
   - CVA（Craniovertebral Angle）の推定角度（度）
   - 正常値は約45-55度。30度以下は重度の前方頭位
   - 重症度: normal, mild, moderate, severe

2. 肩の高さの左右差:
   - 左右の肩峰の高さの違い（ピクセル単位）
   - 左肩と右肩の相対的な位置

3. 脊柱アライメント:
   - 垂直線からの偏位（度）
   - 前後方向の姿勢バランス

4. 全体スコア（0-100）と改善提案

必ず以下のJSON形式で回答してください：
{
  "score": 75,
  "metrics": {
    "headForwardPosition": {
      "angle": 35,
      "score": 65,
      "severity": "mild"
    },
    "shoulderHeight": {
      "leftHeight": 150,
      "rightHeight": 155,
      "difference": 5,
      "score": 85,
      "severity": "normal"
    },
    "spineAlignment": {
      "deviation": 8,
      "score": 80,
      "severity": "mild"
    }
  },
  "recommendations": [
    "顎を引いて頭の位置を正しく保ちましょう",
    "肩甲骨を寄せる意識で胸を開きましょう"
  ]
}`
        },
        {
          role: 'user',
          content: [
            {
              type: 'text',
              text: 'この画像の姿勢を分析してください。側面から撮影された全身画像です。'
            },
            {
              type: 'image_url',
              image_url: {
                url: `data:image/jpeg;base64,${imageData}`,
                detail: 'high'
              }
            }
          ]
        }
      ],
      max_tokens: 1000,
      temperature: 0.1,
    })

    const content = response.choices[0]?.message?.content
    if (!content) {
      throw new Error('No analysis result received from OpenAI')
    }

    // Extract JSON from the response
    const jsonMatch = content.match(/\{[\s\S]*\}/)
    if (!jsonMatch) {
      throw new Error('Invalid JSON format in OpenAI response')
    }

    const analysisResult = JSON.parse(jsonMatch[0])
    return analysisResult

  } catch (error) {
    console.error('OpenAI Vision API error:', error)
    
    if (error instanceof Error) {
      if (error.message.includes('API key')) {
        throw new Error('OpenAI APIキーが無効です')
      } else if (error.message.includes('quota')) {
        throw new Error('OpenAI APIの利用制限に達しました')
      } else if (error.message.includes('Invalid JSON')) {
        throw new Error('分析結果の解析に失敗しました')
      }
    }
    
    throw new Error('姿勢分析に失敗しました')
  }
}

// Fallback analysis function for when OpenAI API is not available
export function generateMockAnalysis(): any {
  return {
    score: Math.floor(Math.random() * 30) + 70, // 70-100
    metrics: {
      headForwardPosition: {
        angle: Math.floor(Math.random() * 20) + 30, // 30-50
        score: Math.floor(Math.random() * 30) + 60, // 60-90
        severity: ['normal', 'mild', 'moderate'][Math.floor(Math.random() * 3)]
      },
      shoulderHeight: {
        leftHeight: 150,
        rightHeight: 150 + Math.floor(Math.random() * 10) - 5, // ±5px
        difference: Math.floor(Math.random() * 10),
        score: Math.floor(Math.random() * 20) + 80, // 80-100
        severity: ['normal', 'mild'][Math.floor(Math.random() * 2)]
      },
      spineAlignment: {
        deviation: Math.floor(Math.random() * 10) + 2, // 2-12 degrees
        score: Math.floor(Math.random() * 25) + 70, // 70-95
        severity: ['normal', 'mild', 'moderate'][Math.floor(Math.random() * 3)]
      }
    },
    recommendations: [
      '顎を引いて頭の位置を正しく保ちましょう',
      '肩甲骨を寄せる意識で胸を開きましょう',
      '定期的なストレッチで姿勢改善を心がけましょう',
      '背筋を伸ばして座る習慣をつけましょう'
    ].slice(0, Math.floor(Math.random() * 2) + 2)
  }
}