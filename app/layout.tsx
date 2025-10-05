import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: '姿勢分析アプリ | Shisei Navi',
  description: 'AI powered posture analysis application for health professionals',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className="min-h-screen bg-background text-foreground">
        {children}
      </body>
    </html>
  )
}