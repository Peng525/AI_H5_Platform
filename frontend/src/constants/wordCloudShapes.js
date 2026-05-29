/** 文字云形状预设 */

export const WORD_CLOUD_SHAPES = [
  { id: 'cloud', label: '云朵', icon: 'cloud' },
  { id: 'circle', label: '圆形', icon: 'circle' },
  { id: 'heart', label: '心形', icon: 'favorite' },
  { id: 'tree', label: '圣诞树', icon: 'park' },
  { id: 'star', label: '星形', icon: 'star' },
  { id: 'diamond', label: '菱形', icon: 'diamond' },
]

export function getWordCloudShape(id) {
  return WORD_CLOUD_SHAPES.find((s) => s.id === id) || WORD_CLOUD_SHAPES[0]
}

function treeShape(theta) {
  const t = theta % (Math.PI * 2)
  const layer = Math.abs(Math.sin(t * 2))
  const base = 0.35 + layer * 0.45
  const trunk = Math.abs(Math.cos(t)) > 0.85 ? 0.25 : base
  return Math.min(1, trunk)
}

export function resolveWordCloudShape(shapeId) {
  switch (shapeId) {
    case 'circle':
      return 'circle'
    case 'heart':
      return 'cardioid'
    case 'star':
      return 'star'
    case 'diamond':
      return 'diamond'
    case 'tree':
      return treeShape
    case 'cloud':
    default:
      return (theta) => {
        const t = theta % (Math.PI * 2)
        return 0.55 + 0.35 * Math.abs(Math.cos(t * 1.5))
      }
  }
}

export function densityToGridSize(density, canvasW) {
  const base = Math.max(4, Math.round(canvasW / 80))
  if (density === 'tight') return Math.max(2, base - 2)
  if (density === 'loose') return base + 4
  return base
}

export function rotationOptions(rotation) {
  switch (rotation) {
    case 'horizontal':
      return { minRotation: 0, maxRotation: 0, rotateRatio: 0 }
    case 'vertical':
      return { minRotation: Math.PI / 2, maxRotation: Math.PI / 2, rotateRatio: 1 }
    case 'mixed':
      return { minRotation: 0, maxRotation: Math.PI / 2, rotateRatio: 0.5 }
    case 'random':
    default:
      return { minRotation: -Math.PI / 4, maxRotation: Math.PI / 4, rotateRatio: 0.3 }
  }
}
