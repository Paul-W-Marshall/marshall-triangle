
'use client'

import { useEffect, useRef, useState } from 'react'

export default function TriangleCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 })

  useEffect(() => {
    const handleResize = () => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight,
      })
    }

    // Set initial dimensions
    handleResize()

    // Add event listener
    window.addEventListener('resize', handleResize)

    // Cleanup
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    canvas.width = dimensions.width
    canvas.height = dimensions.height

    // Clear canvas
    ctx.clearRect(0, 0, dimensions.width, dimensions.height)

    // Draw simple vertical gradient as placeholder
    const gradient = ctx.createLinearGradient(0, 0, 0, dimensions.height)
    gradient.addColorStop(0, '#ff0066')
    gradient.addColorStop(0.5, '#00ff66')
    gradient.addColorStop(1, '#0066ff')

    // Create triangle shape
    const centerX = dimensions.width / 2
    const centerY = dimensions.height / 2
    const size = Math.min(dimensions.width, dimensions.height) * 0.4

    ctx.beginPath()
    ctx.moveTo(centerX, centerY - size)
    ctx.lineTo(centerX - size * 0.866, centerY + size * 0.5)
    ctx.lineTo(centerX + size * 0.866, centerY + size * 0.5)
    ctx.closePath()

    ctx.fillStyle = gradient
    ctx.fill()

    // Add subtle border
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)'
    ctx.lineWidth = 2
    ctx.stroke()
  }, [dimensions])

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full"
      style={{ width: dimensions.width, height: dimensions.height }}
    />
  )
}
