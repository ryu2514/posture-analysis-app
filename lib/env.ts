export const env = {
  OPENAI_API_KEY: process.env.OPENAI_API_KEY || '',
  NODE_ENV: process.env.NODE_ENV || 'development',
  GOOGLE_CLOUD_VISION_API_KEY: process.env.GOOGLE_CLOUD_VISION_API_KEY,
  MAX_FILE_SIZE: parseInt(process.env.MAX_FILE_SIZE || '10485760', 10),
  ALLOWED_FILE_TYPES: (process.env.ALLOWED_FILE_TYPES || 'image/jpeg,image/png,image/jpg').split(','),
  LOG_LEVEL: process.env.LOG_LEVEL || 'info',
  ANALYSIS_BACKEND: (process.env.ANALYSIS_BACKEND || 'mediapipe') as 'mediapipe' | 'openai',
} as const

export function validateEnv() {
  // Only require OPENAI_API_KEY when using OpenAI backend explicitly
  if (env.ANALYSIS_BACKEND === 'openai') {
    if (!env.OPENAI_API_KEY) {
      throw new Error('Missing required environment variables: OPENAI_API_KEY')
    }
  }
}

export function isValidFileType(mimeType: string): boolean {
  return env.ALLOWED_FILE_TYPES.includes(mimeType)
}

export function isValidFileSize(size: number): boolean {
  return size <= env.MAX_FILE_SIZE
}
