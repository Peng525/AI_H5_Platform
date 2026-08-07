/**
 * SVG → canvas_elements 转换器（策略A）
 * 将 SVG 字符串渲染为背景图片 + 提取文字叠加层
 *
 * 策略A（当前）：SVG作为整页背景图 + DOMParser提取<text>元素 → 透明text叠加
 * 策略B（未来）：完整解析SVG → shape/text/image 独立canvas_elements
 */

import { CANVAS_Z } from '../constants/canvasLayers.js'

/** 默认画布尺寸（16:9），可通过参数覆盖 */
const DEFAULT_W = 1280
const DEFAULT_H = 720

let _idCounter = 0
function uid(prefix = 'sv') {
  _idCounter += 1
  return `orch_${prefix}_${_idCounter}`
}

/**
 * SVG字符串 → Base64 Data URL
 */
export function svgToDataUrl(svgString) {
  const encoded = btoa(unescape(encodeURIComponent(svgString)))
  return `data:image/svg+xml;base64,${encoded}`
}

/**
 * 从SVG字符串中提取 <text> 元素，生成 canvas_elements text 叠加层
 *
 * @param {string} svgString - SVG代码
 * @returns {Array} canvas_elements[] (仅text类型)
 */
export function extractTextElements(svgString, canvasW = DEFAULT_W, canvasH = DEFAULT_H) {
  if (!svgString || typeof svgString !== 'string') return []

  const elements = []

  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(svgString, 'image/svg+xml')
    const textNodes = doc.querySelectorAll('text')

    textNodes.forEach((node, index) => {
      const content = (node.textContent || '').trim()
      // 跳过空白/装饰性元素
      if (!content || content === '|' || content === '·' || content === '•') return

      // 解析坐标
      const x = parseFloat(node.getAttribute('x') || '80')
      const y = parseFloat(node.getAttribute('y') || '60')

      // 解析样式
      const style = node.getAttribute('style') || ''
      const fontSizeStr = node.getAttribute('font-size')
        || (style.match(/font-size:\s*([^;]+)/) || [])[1]
        || '18'
      const fontSize = parseFloat(fontSizeStr) || 18

      const fill = node.getAttribute('fill')
        || (style.match(/fill:\s*([^;]+)/) || [])[1]
        || '#1f2937'

      const fontWeight = node.getAttribute('font-weight')
        || (style.match(/font-weight:\s*([^;]+)/) || [])[1]
        || 'normal'

      const textAnchor = node.getAttribute('text-anchor') || 'start'
      let textAlign = 'left'
      if (textAnchor === 'middle') textAlign = 'center'
      else if (textAnchor === 'end') textAlign = 'right'

      // 跳过太小的文字（可能是页码装饰等）
      if (fontSize < 8) return

      // 估算文字宽高
      const estWidth = content.length * fontSize * 0.6
      const estHeight = fontSize * 1.5

      // 调整Y坐标：SVG的y是baseline，Canvas用top-left
      const adjustedY = y - fontSize * 0.85

      elements.push({
        id: uid('text'),
        type: 'text',
        x: Math.max(0, x),
        y: Math.max(0, adjustedY),
        width: Math.min(estWidth, canvasW - x - 20),
        height: estHeight,
        zIndex: CANVAS_Z.CONTENT_BASE + 1 + index,
        content: content,
        style: {
          background: 'transparent',
          color: fill,
          fontSize: fontSize,
          fontWeight: fontWeight,
          fontFamily: '"Microsoft YaHei", "PingFang SC", sans-serif',
          textAlign: textAlign,
          lineHeight: 1.3,
        },
      })
    })
  } catch (err) {
    console.warn('[svgToElements] DOMParser failed, falling back to regex:', err)
    // 正则回退
    return _extractTextElementsRegex(svgString, canvasW, canvasH)
  }

  return elements
}

/**
 * 正则回退：从SVG提取<text>元素
 */
function _extractTextElementsRegex(svgString, canvasW = DEFAULT_W, canvasH = DEFAULT_H) {
  const elements = []
  const textTagRe = /<text\b([^>]*)>(.*?)<\/text>/gi
  const attrRe = /(\w[\w-]*)\s*=\s*"([^"]*)"/g

  let match
  let index = 0
  while ((match = textTagRe.exec(svgString)) !== null) {
    const attrsStr = match[1]
    const content = match[2].replace(/<[^>]+>/g, '').trim()
    if (!content || content.length < 2) continue

    // 解析属性
    const attrs = {}
    let am
    while ((am = attrRe.exec(attrsStr)) !== null) {
      attrs[am[1]] = am[2]
    }

    const x = parseFloat(attrs.x || '80')
    const y = parseFloat(attrs.y || '60')
    const fontSize = parseFloat(attrs['font-size'] || '18')
    const fill = attrs.fill || '#1f2937'
    const fontWeight = attrs['font-weight'] || 'normal'
    const textAnchor = attrs['text-anchor'] || 'start'

    let textAlign = 'left'
    if (textAnchor === 'middle') textAlign = 'center'
    else if (textAnchor === 'end') textAlign = 'right'

    if (fontSize < 8) continue

    const estWidth = content.length * fontSize * 0.6
    const estHeight = fontSize * 1.5

    elements.push({
      id: uid('text'),
      type: 'text',
      x: Math.max(0, x),
      y: Math.max(0, y - fontSize * 0.85),
      width: Math.min(estWidth, canvasW - x - 20),
      height: estHeight,
      zIndex: CANVAS_Z.CONTENT_BASE + 1 + index,
      content: content,
      style: {
        background: 'transparent',
        color: fill,
        fontSize: fontSize,
        fontWeight: fontWeight,
        fontFamily: '"Microsoft YaHei", "PingFang SC", sans-serif',
        textAlign: textAlign,
        lineHeight: 1.3,
      },
    })
    index++
  }

  return elements
}

/**
 * 完整策略A：SVG → canvas_elements（背景图 + 文字叠加层）
 *
 * @param {string} svgString - SVG代码
 * @param {number} pageNum - 页码（用于生成唯一ID）
 * @returns {Array} 完整的 canvas_elements[]
 */
export function svgToCanvasElements(svgString, pageNum = 1, canvasW = DEFAULT_W, canvasH = DEFAULT_H) {
  const elements = []

  // 1. 背景图（SVG渲染为整页图片）
  const dataUrl = svgToDataUrl(svgString)
  elements.push({
    id: uid(`bg_${pageNum}`),
    type: 'image',
    x: 0,
    y: 0,
    width: canvasW,
    height: canvasH,
    zIndex: 1,
    content: dataUrl,
    style: { background: 'transparent', objectFit: 'fill' },
  })

  // 2. 文字叠加层
  const textOverlays = extractTextElements(svgString, canvasW, canvasH)
  elements.push(...textOverlays)

  return elements
}
