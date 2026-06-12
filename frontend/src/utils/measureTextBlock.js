/**
 * 编译层文本测量：预测 canvas text 元素换行后的高度。
 */
let measureCanvas = null

function getMeasureContext(fontFamily, fontSize, fontWeight = 'normal') {
  if (typeof document === 'undefined') {
    return null
  }
  if (!measureCanvas) {
    measureCanvas = document.createElement('canvas')
  }
  const ctx = measureCanvas.getContext('2d')
  if (!ctx) return null
  const weight = fontWeight === 'bold' || fontWeight === '600' ? 'bold' : 'normal'
  ctx.font = `${weight} ${fontSize}px ${fontFamily || 'sans-serif'}`
  return ctx
}

function wrapLines(content, maxWidth, ctx) {
  const text = String(content || '').trim()
  if (!text) return []
  if (!ctx || maxWidth <= 0) return [text]

  const lines = []
  const paragraphs = text.split('\n')
  for (const para of paragraphs) {
    if (!para) {
      lines.push('')
      continue
    }
    let current = ''
    for (const ch of para) {
      const trial = current + ch
      if (ctx.measureText(trial).width > maxWidth && current) {
        lines.push(current)
        current = ch
      } else {
        current = trial
      }
    }
    if (current) lines.push(current)
  }
  return lines.length ? lines : ['']
}

/**
 * @param {object} opts
 * @param {string} opts.content
 * @param {number} opts.width - 内容区宽度 px
 * @param {number} opts.fontSize
 * @param {number} [opts.lineHeight=1.5]
 * @param {string} [opts.fontFamily]
 * @param {string} [opts.fontWeight]
 * @param {number} [opts.verticalPadding=8]
 */
export function measureTextBlock({
  content,
  width,
  fontSize,
  lineHeight = 1.5,
  fontFamily = 'sans-serif',
  fontWeight = 'normal',
  verticalPadding = 8,
}) {
  const ctx = getMeasureContext(fontFamily, fontSize, fontWeight)
  const lines = wrapLines(content, Math.max(20, width - 4), ctx)
  const lineCount = Math.max(1, lines.length)
  const height = Math.ceil(lineCount * fontSize * lineHeight + verticalPadding)
  return { height, lineCount, lines }
}

export function measureTextBlocks(blocks) {
  return blocks.reduce((sum, b) => sum + measureTextBlock(b).height, 0)
}

/**
 * 单行或多行文本中最宽一行的像素宽度。
 */
export function measureTextWidth({
  content,
  fontSize,
  fontFamily = 'sans-serif',
  fontWeight = 'normal',
}) {
  const ctx = getMeasureContext(fontFamily, fontSize, fontWeight)
  if (!ctx) return 0
  const lines = String(content || '').split('\n')
  let max = 0
  for (const line of lines) {
    max = Math.max(max, ctx.measureText(line || ' ').width)
  }
  return Math.ceil(max)
}

/**
 * 根据文本内容自适应 text 元素的宽高（单行优先扩宽，多行优先增高）。
 * @returns {null | { width?: number, height?: number }}
 */
export function fitTextElementBox(
  element,
  content,
  canvasBounds,
  { minWidth = 48, minHeight = 24, horizontalPadding = 12, verticalPadding = 8 } = {},
) {
  if (element?.type !== 'text') return null
  const style = element.style || {}
  const fontSize = style.fontSize || 16
  const fontFamily = style.fontFamily || 'sans-serif'
  const fontWeight = style.fontWeight || 'normal'
  const lineHeight = style.lineHeight ?? 1.5
  const text = String(content ?? element.content ?? '')

  const maxCanvasW = canvasBounds
    ? Math.max(minWidth, canvasBounds.width - (element.x || 0))
    : 2000
  const naturalW = measureTextWidth({ content: text, fontSize, fontFamily, fontWeight }) + horizontalPadding
  const hasNewline = text.includes('\n')

  let width = element.width || minWidth
  if (!hasNewline && naturalW > width) {
    width = Math.min(maxCanvasW, Math.max(minWidth, naturalW))
  }

  const { height } = measureTextBlock({
    content: text,
    width,
    fontSize,
    lineHeight,
    fontFamily,
    fontWeight,
    verticalPadding,
  })
  const newHeight = Math.max(minHeight, height)

  const patch = {}
  if (width !== element.width) patch.width = width
  if (newHeight !== element.height) patch.height = newHeight
  return Object.keys(patch).length ? patch : null
}
