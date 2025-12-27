
/**
 * Color space conversion utilities
 * Stubs for sRGB and Display-P3 support
 */

export interface RGBColor {
  r: number
  g: number
  b: number
}

export interface P3Color {
  r: number
  g: number
  b: number
}

/**
 * Encode RGB values to sRGB color space
 * Stub implementation - to be replaced with proper conversion
 */
export function encodeSRGB(rgb: RGBColor): string {
  const r = Math.round(rgb.r * 255)
  const g = Math.round(rgb.g * 255)
  const b = Math.round(rgb.b * 255)
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
}

/**
 * Decode sRGB hex string to RGB values
 * Stub implementation - to be replaced with proper conversion
 */
export function decodeSRGB(hex: string): RGBColor {
  const clean = hex.replace('#', '')
  const r = parseInt(clean.substr(0, 2), 16) / 255
  const g = parseInt(clean.substr(2, 2), 16) / 255
  const b = parseInt(clean.substr(4, 2), 16) / 255
  return { r, g, b }
}

/**
 * Convert sRGB to Display-P3 color space
 * Stub implementation - to be replaced with proper matrix conversion
 */
export function srgbToP3(srgb: RGBColor): P3Color {
  // Stub: return same values for now
  return { ...srgb }
}

/**
 * Convert Display-P3 to sRGB color space
 * Stub implementation - to be replaced with proper matrix conversion
 */
export function p3ToSrgb(p3: P3Color): RGBColor {
  // Stub: return same values for now
  return { ...p3 }
}
