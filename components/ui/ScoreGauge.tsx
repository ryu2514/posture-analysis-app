interface ScoreGaugeProps {
  score: number // 0-100
  size?: 'sm' | 'md' | 'lg'
  label?: string
  severity?: 'normal' | 'mild' | 'moderate' | 'severe'
}

export function ScoreGauge({ score, size = 'md', label, severity }: ScoreGaugeProps) {
  const clampedScore = Math.max(0, Math.min(100, score))
  
  const sizeClasses = {
    sm: 'w-20 h-20',
    md: 'w-32 h-32',
    lg: 'w-40 h-40',
  }

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-lg',
    lg: 'text-xl',
  }

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-600'
    if (score >= 70) return 'text-yellow-600'
    if (score >= 50) return 'text-orange-600'
    return 'text-red-600'
  }

  const getStrokeColor = (score: number) => {
    if (score >= 85) return '#16a34a' // green-600
    if (score >= 70) return '#ca8a04' // yellow-600
    if (score >= 50) return '#ea580c' // orange-600
    return '#dc2626' // red-600
  }

  const getSeverityBadge = (severity?: string) => {
    if (!severity) return null
    
    const severityConfig = {
      normal: { bg: 'bg-green-100', text: 'text-green-800', label: '正常' },
      mild: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: '軽度' },
      moderate: { bg: 'bg-orange-100', text: 'text-orange-800', label: '中度' },
      severe: { bg: 'bg-red-100', text: 'text-red-800', label: '重度' },
    }

    const config = severityConfig[severity as keyof typeof severityConfig]
    if (!config) return null

    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
        {config.label}
      </span>
    )
  }

  // SVG circle parameters
  const center = size === 'sm' ? 40 : size === 'md' ? 64 : 80
  const radius = center - 8
  const circumference = 2 * Math.PI * radius
  const strokeDasharray = circumference
  const strokeDashoffset = circumference - (clampedScore / 100) * circumference

  return (
    <div className="flex flex-col items-center space-y-2">
      <div className={`relative ${sizeClasses[size]}`}>
        <svg
          className="transform -rotate-90"
          width="100%"
          height="100%"
          viewBox={`0 0 ${center * 2} ${center * 2}`}
        >
          {/* Background circle */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="6"
          />
          {/* Progress circle */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={getStrokeColor(clampedScore)}
            strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        
        {/* Score text in center */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className={`font-bold ${textSizeClasses[size]} ${getScoreColor(clampedScore)}`}>
              {Math.round(clampedScore)}
            </div>
            <div className="text-xs text-gray-500">/ 100</div>
          </div>
        </div>
      </div>
      
      {label && (
        <div className="text-center">
          <div className="text-sm font-medium text-gray-900">{label}</div>
          {getSeverityBadge(severity)}
        </div>
      )}
    </div>
  )
}