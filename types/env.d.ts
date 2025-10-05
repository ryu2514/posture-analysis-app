declare namespace NodeJS {
  interface ProcessEnv {
    OPENAI_API_KEY: string
    NODE_ENV: 'development' | 'production' | 'test'
    GOOGLE_CLOUD_VISION_API_KEY?: string
    MAX_FILE_SIZE: string
    ALLOWED_FILE_TYPES: string
    LOG_LEVEL: 'debug' | 'info' | 'warn' | 'error'
  }
}