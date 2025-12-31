
import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Marshall Triangle',
  description: 'Interactive visualization of triadic balance between Privacy, Performance, and Personalization',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
