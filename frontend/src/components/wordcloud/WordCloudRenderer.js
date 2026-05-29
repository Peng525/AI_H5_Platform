import WordCloud from 'wordcloud'
import { getTheme } from '../../constants/designThemes.js'
import { densityToGridSize, resolveWordCloudShape, rotationOptions } from '../../constants/wordCloudShapes.js'
import { toWordCloudList } from '../../utils/parseSurveyData.js'

function pickColors(content, themeId) {
  if (content.colorMode === 'custom' && content.colors?.length) {
    return content.colors
  }
  const theme = getTheme(themeId || 'zjy-minimal')
  return [
    theme.colors.accent,
    theme.colors.text,
    theme.colors.accentMuted || theme.colors.accent,
    '#156082',
    '#404753',
    '#E91E8C',
    '#07C160',
  ].filter(Boolean)
}

export function renderWordCloud(canvas, content, themeId = 'zjy-minimal') {
  if (!canvas || !content) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const w = canvas.width
  const h = canvas.height
  const words = content.words || []
  const list = toWordCloudList(words)
  if (!list.length) {
    ctx.clearRect(0, 0, w, h)
    ctx.fillStyle = content.backgroundColor || '#ffffff'
    ctx.globalAlpha = content.backgroundAlpha ?? 1
    ctx.fillRect(0, 0, w, h)
    ctx.globalAlpha = 1
    ctx.fillStyle = '#999'
    ctx.font = '14px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('请添加关键词', w / 2, h / 2)
    return
  }

  const colors = pickColors(content, themeId)
  const rot = rotationOptions(content.rotation || 'random')
  const shape = resolveWordCloudShape(content.shapeId || 'cloud')
  const maxW = Math.max(...list.map((x) => x[1]), 1)
  const maxFont = content.maxFontSize || 80
  const minFont = content.minFontSize || 12

  ctx.clearRect(0, 0, w, h)
  ctx.fillStyle = content.backgroundColor || '#ffffff'
  ctx.globalAlpha = content.backgroundAlpha ?? 1
  ctx.fillRect(0, 0, w, h)
  ctx.globalAlpha = 1

  WordCloud(canvas, {
    list,
    gridSize: densityToGridSize(content.density || 'normal', w),
    weightFactor: (size) => Math.max(minFont, (size / maxW) * maxFont),
    fontFamily:
      content.fontFamily === 'system'
        ? '"Microsoft YaHei", "PingFang SC", sans-serif'
        : content.fontFamily,
    color: () => colors[Math.floor(Math.random() * colors.length)],
    rotateRatio: rot.rotateRatio,
    minRotation: rot.minRotation,
    maxRotation: rot.maxRotation,
    backgroundColor: 'transparent',
    shrinkToFit: true,
    drawOutOfBound: false,
    shape,
    minSize: content.minFontSize || 12,
    origin: [w / 2, h / 2],
  })
}

export async function renderWordCloudWithMask(canvas, content, maskUrl, themeId) {
  if (!maskUrl) {
    renderWordCloud(canvas, content, themeId)
    return
  }
  const img = new Image()
  img.crossOrigin = 'anonymous'
  await new Promise((resolve, reject) => {
    img.onload = resolve
    img.onerror = reject
    img.src = maskUrl
  })
  const w = canvas.width
  const h = canvas.height
  const off = document.createElement('canvas')
  off.width = w
  off.height = h
  const octx = off.getContext('2d')
  octx.drawImage(img, 0, 0, w, h)

  const colors = pickColors(content, themeId)
  const rot = rotationOptions(content.rotation || 'random')
  const list = toWordCloudList(content.words || [])

  WordCloud(canvas, {
    list,
    gridSize: densityToGridSize(content.density || 'normal', w),
    weightFactor: (size) => size,
    fontFamily: '"Microsoft YaHei", "PingFang SC", sans-serif',
    color: () => colors[Math.floor(Math.random() * colors.length)],
    rotateRatio: rot.rotateRatio,
    minRotation: rot.minRotation,
    maxRotation: rot.maxRotation,
    backgroundColor: content.backgroundColor || '#ffffff',
    shrinkToFit: true,
    drawMask: (ctx) => {
      ctx.drawImage(off, 0, 0, w, h)
    },
    minSize: content.minFontSize || 12,
  })
}
