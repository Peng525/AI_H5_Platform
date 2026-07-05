import { getTheme, getThemeMargins, getThemeTypeScale } from '../constants/designThemes.js'
import { getLayoutCanvasSize, isWideWebViewport } from '../constants/editorPresets.js'
import { CANVAS_Z } from '../constants/canvasLayers.js'
import { normalizeMaterialIconName } from './materialIcons.js'
import { measureTextBlock } from './measureTextBlock.js'

export const FIXED_LAYOUT_VERSION = 2

export const FIXED_LAYOUT_IDS = {
  COVER: 'cover_title',
  TOC: 'toc',
  CHAPTER: 'chapter_divider',
  ROADMAP_BOTTOM: 'roadmap_bottom',
  SCENE_LEFT: 'scene_left',
  CHART_LEFT: 'chart_left',
  KEY_POINTS: 'key_points',
  CLOSING: 'closing',
}

const VALID_FIXED_LAYOUTS = new Set(Object.values(FIXED_LAYOUT_IDS))

let _id = 0

function resetIds() {
  _id = 0
}

function uid(prefix) {
  _id += 1
  return `fx_${prefix}_${_id}`
}

function ctx(viewportId, themeId) {
  const theme = getTheme(themeId)
  const scale = getThemeTypeScale(themeId, viewportId)
  const margin = getThemeMargins(themeId, viewportId)
  const { width: W, height: H } = getLayoutCanvasSize(viewportId)
  return {
    theme,
    scale,
    margin,
    W,
    H,
    wide: isWideWebViewport(viewportId),
    colors: theme.colors,
    fonts: theme.fonts,
  }
}

function text(x, y, width, height, content, style = {}, zIndex = CANVAS_Z.CONTENT_BASE) {
  return {
    id: uid('t'),
    type: 'text',
    x,
    y,
    width,
    height,
    zIndex,
    content: String(content || ''),
    style: {
      background: 'transparent',
      color: '#0E2841',
      fontSize: 16,
      fontWeight: 'normal',
      fontFamily: '"Microsoft YaHei", "PingFang SC", sans-serif',
      lineHeight: 1.35,
      textAlign: 'left',
      ...style,
    },
  }
}

function shape(x, y, width, height, style = {}, zIndex = CANVAS_Z.CONTENT_BASE) {
  return {
    id: uid('s'),
    type: 'shape',
    x,
    y,
    width,
    height,
    zIndex,
    content: '',
    style: { background: '#E8E8E8', borderRadius: 12, ...style },
  }
}

function icon(x, y, size, name, color) {
  return {
    id: uid('ic'),
    type: 'icon',
    x,
    y,
    width: size,
    height: size,
    zIndex: CANVAS_Z.CONTENT_BASE + 1,
    content: normalizeMaterialIconName(name),
    style: { background: 'transparent', color },
  }
}

function image(x, y, width, height, url) {
  return {
    id: uid('img'),
    type: 'image',
    x,
    y,
    width,
    height,
    zIndex: CANVAS_Z.CONTENT_BASE,
    content: String(url || ''),
    style: { background: '#F3F6FA', objectFit: 'cover', borderRadius: 14 },
  }
}

function chart(x, y, width, height, chartDef, colors) {
  const values = Array.isArray(chartDef?.values) && chartDef.values.length
    ? chartDef.values.map((v) => Number(v) || 0)
    : [30, 55, 82]
  const labels = Array.isArray(chartDef?.labels) && chartDef.labels.length
    ? chartDef.labels.map((v) => String(v).slice(0, 16))
    : values.map((_, i) => `指标 ${i + 1}`)
  return {
    id: uid('chart'),
    type: 'chart',
    x,
    y,
    width,
    height,
    zIndex: CANVAS_Z.CONTENT_BASE,
    content: {
      chartType: chartDef?.type === 'pie' || chartDef?.chartType === 'pie' ? 'pie' : 'bar',
      title: String(chartDef?.title || ''),
      labels,
      values,
    },
    style: {
      background: '#FFFFFF',
      borderRadius: 14,
      chartColor: colors.accent,
    },
  }
}

function normalizePoints(slide, max = 4) {
  const raw = slide.points || slide.modules || slide.blocks || slide.steps || []
  const list = Array.isArray(raw) ? raw : []
  const points = list
    .map((item) => {
      if (typeof item === 'string') return { title: item, body: '' }
      return {
        icon: item.icon || 'circle',
        title: String(item.title || item.label || item.name || '').slice(0, 36),
        body: String(item.body || item.desc || item.description || '').slice(0, 90),
      }
    })
    .filter((item) => item.title || item.body)
    .slice(0, max)
  if (points.length) return points

  return [
    slide.insight,
    slide.body,
    slide.subtitle,
    slide.title,
  ]
    .filter(Boolean)
    .flatMap((value) => String(value).split(/[。；;.\n]/))
    .map((value) => value.trim())
    .filter(Boolean)
    .slice(0, max)
    .map((value, index) => ({
      icon: ['target', 'bolt', 'trending_up', 'database'][index % 4],
      title: value.slice(0, 36),
      body: '',
    }))
}

function ensurePointCount(points, count, fallbackTitle = '关键内容') {
  const out = [...points]
  while (out.length < count) {
    out.push({
      icon: ['target', 'bolt', 'trending_up'][out.length % 3],
      title: out.length === 0 ? fallbackTitle : `步骤 ${out.length + 1}`,
      body: '',
    })
  }
  return out
}

function fitTextInFixed(x, y, boxW, boxH, content, baseStyle, zIndex = CANVAS_Z.CONTENT_BASE) {
  const str = String(content || '').trim()
  if (!str || boxW <= 0 || boxH <= 0) {
    return text(x, y, Math.max(boxW, 1), Math.min(Math.max(boxH, 1), 16), str, baseStyle, zIndex)
  }
  let fontSize = baseStyle.fontSize || 16
  const minFontSize = baseStyle.minFontSize ?? 11
  const lineHeight = baseStyle.lineHeight ?? 1.3
  while (fontSize >= minFontSize) {
    const m = measureTextBlock({
      content: str,
      width: boxW,
      fontSize,
      lineHeight,
      fontFamily: baseStyle.fontFamily,
      fontWeight: baseStyle.fontWeight,
      verticalPadding: 4,
    })
    if (m.height <= boxH) {
      return text(x, y, boxW, m.height, str, { ...baseStyle, fontSize }, zIndex)
    }
    fontSize -= 1
  }
  const truncated = str.length > 96 ? `${str.slice(0, 93)}…` : str
  const m = measureTextBlock({
    content: truncated,
    width: boxW,
    fontSize: minFontSize,
    lineHeight,
    fontFamily: baseStyle.fontFamily,
    fontWeight: baseStyle.fontWeight,
    verticalPadding: 4,
  })
  return text(x, y, boxW, Math.min(boxH, m.height), truncated, { ...baseStyle, fontSize: minFontSize }, zIndex)
}

function tocLayout(c, requested = 6) {
  const startY = c.H <= 480 ? Math.round(c.H * 0.26) : 138
  const available = Math.max(40, c.H - startY - 12)
  const rowH = c.H <= 480
    ? Math.max(34, Math.floor(available / Math.max(requested, 1)))
    : 54
  const maxRows = c.H <= 480
    ? Math.max(1, Math.floor(available / rowH))
    : requested
  return { startY, rowH, maxRows: Math.min(maxRows, requested) }
}

function addHeader(els, c, slide, y = 36, opts = {}) {
  const title = slide.title || ''
  const kicker = slide.kicker || slide.headline || ''
  let cy = y
  if (kicker) {
    els.push(fitTextInFixed(c.margin.x, cy, c.margin.contentWidth, 26, kicker, {
      fontSize: 18,
      fontWeight: 'bold',
      color: c.colors.accent,
      fontFamily: c.fonts.display,
    }))
    cy += 28
  }
  const titleH = opts.titleH || 42
  els.push(fitTextInFixed(c.margin.x, cy, c.margin.contentWidth, titleH, title, {
    fontSize: opts.titleSize || 26,
    fontWeight: 'bold',
    color: c.colors.text,
    fontFamily: c.fonts.display,
    lineHeight: 1.2,
    textAlign: opts.align || 'left',
  }))
  if (slide.subtitle || slide.insight) {
    els.push(fitTextInFixed(
      c.margin.x,
      cy + titleH + 6,
      c.margin.contentWidth,
      44,
      slide.subtitle || slide.insight,
      {
        fontSize: 15,
        color: c.colors.textMuted,
        fontFamily: c.fonts.body,
        lineHeight: 1.35,
        textAlign: opts.align || 'left',
      },
    ))
  }
}

function buildCover(c, slide) {
  const titleW = Math.round(c.W * 0.72)
  const titleX = Math.round((c.W - titleW) / 2)
  const titleY = Math.round(c.H * 0.25)
  return [
    text(titleX, titleY, titleW, 58, slide.title, {
      fontSize: 32,
      fontWeight: 'bold',
      color: c.colors.text,
      fontFamily: c.fonts.display,
      lineHeight: 1.18,
      textAlign: 'center',
    }),
    text(titleX, titleY + 88, titleW, 48, slide.subtitle || slide.insight || '', {
      fontSize: 16,
      color: c.colors.textMuted,
      fontFamily: c.fonts.body,
      textAlign: 'center',
      lineHeight: 1.35,
    }),
  ]
}

function buildToc(c, slide) {
  const els = []
  addHeader(els, c, { ...slide, title: slide.title || '目录' }, 34)
  const layout = tocLayout(c, 6)
  const items = normalizePoints(slide, layout.maxRows)
  items.forEach((item, i) => {
    const y = layout.startY + i * layout.rowH
    els.push(shape(c.margin.x, y, 34, 34, { background: c.colors.accent, borderRadius: 999 }))
    els.push(text(c.margin.x, y + 5, 34, 24, String(i + 1), {
      fontSize: 14,
      fontWeight: 'bold',
      color: c.colors.onAccent,
      textAlign: 'center',
      fontFamily: c.fonts.display,
    }, CANVAS_Z.CONTENT_BASE + 1))
    els.push(fitTextInFixed(c.margin.x + 52, y + 4, c.margin.contentWidth - 52, Math.max(24, layout.rowH - 8), item.title, {
      fontSize: c.H <= 480 ? 16 : 19,
      fontWeight: '600',
      color: c.colors.text,
      fontFamily: c.fonts.display,
    }))
  })
  return els
}

function buildChapter(c, slide) {
  return [
    shape(c.margin.x, Math.round(c.H * 0.28), 5, 100, { background: c.colors.accent, borderRadius: 4 }),
    text(c.margin.x + 24, Math.round(c.H * 0.25), c.margin.contentWidth - 24, 62, slide.title, {
      fontSize: 30,
      fontWeight: 'bold',
      color: c.colors.text,
      fontFamily: c.fonts.display,
      lineHeight: 1.18,
    }),
    text(c.margin.x + 24, Math.round(c.H * 0.25) + 78, c.margin.contentWidth - 24, 62, slide.subtitle || slide.insight || '', {
      fontSize: 17,
      color: c.colors.textMuted,
      fontFamily: c.fonts.body,
      lineHeight: 1.4,
    }),
  ]
}

function buildRoadmapBottom(c, slide) {
  const els = []
  addHeader(els, c, slide, 26, { align: 'center', titleSize: 24, titleH: 36 })
  const visualW = Math.round(c.margin.contentWidth * 0.66)
  const visualH = 112
  const visualX = Math.round((c.W - visualW) / 2)
  const visualY = Math.round(c.H * 0.58)
  if (slide.image_url) {
    els.push(image(visualX, visualY, visualW, visualH, slide.image_url))
  } else {
    const steps = ensurePointCount(normalizePoints(slide, 4), 3, slide.title || '路线图')
    const count = Math.max(steps.length, 3)
    const gap = visualW / count
    steps.forEach((step, i) => {
      const cx = visualX + Math.round(gap * i + gap / 2)
      els.push(shape(cx - 24, visualY + 10, 48, 48, { background: c.colors.accent, borderRadius: 999 }))
      els.push(text(cx - 24, visualY + 23, 48, 24, String(i + 1), {
        fontSize: 16,
        fontWeight: 'bold',
        color: c.colors.onAccent,
        textAlign: 'center',
        fontFamily: c.fonts.display,
      }, CANVAS_Z.CONTENT_BASE + 1))
      els.push(text(cx - gap / 2 + 6, visualY + 72, gap - 12, 34, step.title, {
        fontSize: 13,
        color: c.colors.textMuted,
        textAlign: 'center',
        fontFamily: c.fonts.body,
        lineHeight: 1.25,
      }))
    })
  }
  return els
}

function buildLeftVisual(c, slide, kind) {
  const els = []
  addHeader(els, c, slide, 30)
  const top = 146
  const leftX = c.margin.x
  const leftW = Math.round(c.margin.contentWidth * 0.42)
  const leftH = c.H - top - 42
  const rightX = leftX + leftW + 36
  const rightW = c.margin.x + c.margin.contentWidth - rightX
  if (kind === 'chart') {
    els.push(chart(leftX, top, leftW, leftH, slide.chart || {}, c.colors))
  } else if (slide.image_url) {
    els.push(image(leftX, top, leftW, leftH, slide.image_url))
  } else {
    els.push(shape(leftX, top, leftW, leftH, {
      background: c.colors.bgMuted,
      border: `1px solid ${c.colors.textMuted}33`,
      borderRadius: 14,
    }))
    els.push(icon(leftX + 24, top + 24, 28, 'image', c.colors.accent))
    els.push(text(leftX + 24, top + 68, leftW - 48, 44, slide.visual_label || '情景视觉区', {
      fontSize: 20,
      fontWeight: '600',
      color: c.colors.text,
      fontFamily: c.fonts.display,
      lineHeight: 1.2,
    }, CANVAS_Z.CONTENT_BASE + 1))
    els.push(text(leftX + 24, top + 120, leftW - 48, 96, slide.image_prompt || slide.body || slide.insight || '', {
      fontSize: 13,
      color: c.colors.textMuted,
      fontFamily: c.fonts.body,
      lineHeight: 1.35,
    }, CANVAS_Z.CONTENT_BASE + 1))
  }
  const narrativeTitle = slide.insight || slide.subtitle || slide.title || '核心洞察'
  const narrativeBody = slide.body || slide.description || slide.subtitle || slide.insight || slide.title || ''
  els.push(text(rightX, top + 8, rightW, 42, narrativeTitle, {
    fontSize: 22,
    fontWeight: 'bold',
    color: c.colors.text,
    fontFamily: c.fonts.display,
    lineHeight: 1.2,
  }))
  els.push(text(rightX, top + 64, rightW, 88, narrativeBody, {
    fontSize: 15,
    color: c.colors.textMuted,
    fontFamily: c.fonts.body,
    lineHeight: 1.45,
  }))
  return els
}

function buildKeyPoints(c, slide) {
  const els = []
  addHeader(els, c, slide, 30)
  const points = ensurePointCount(normalizePoints(slide, 3), 3, slide.title || '关键内容')
  const gap = 14
  const startY = c.H <= 480 ? Math.round(c.H * 0.38) : 166
  const cardH = Math.max(72, Math.min(130, c.H - startY - 20))
  const cardW = Math.floor((c.margin.contentWidth - gap * (points.length - 1 || 2)) / Math.max(points.length, 3))
  points.forEach((point, i) => {
    const x = c.margin.x + i * (cardW + gap)
    els.push(shape(x, startY, cardW, cardH, {
      background: c.colors.bgMuted,
      border: `1px solid ${c.colors.textMuted}33`,
      borderRadius: 12,
    }))
    els.push(icon(x + 18, startY + 18, 20, point.icon || 'circle', c.colors.accent))
    els.push(fitTextInFixed(x + 18, startY + 48, cardW - 36, Math.min(36, cardH * 0.28), point.title, {
      fontSize: 17,
      fontWeight: '600',
      color: c.colors.text,
      fontFamily: c.fonts.display,
      lineHeight: 1.2,
    }))
    els.push(fitTextInFixed(x + 18, startY + 84, cardW - 36, Math.max(28, cardH - 96), point.body, {
      fontSize: 12,
      color: c.colors.textMuted,
      fontFamily: c.fonts.body,
      lineHeight: 1.3,
    }))
  })
  return els
}

function buildClosing(c, slide) {
  return [
    text(c.margin.x, Math.round(c.H * 0.28), c.margin.contentWidth, 56, slide.title || '谢谢', {
      fontSize: 34,
      fontWeight: 'bold',
      color: c.colors.text,
      textAlign: 'center',
      fontFamily: c.fonts.display,
    }),
    text(c.margin.x, Math.round(c.H * 0.28) + 76, c.margin.contentWidth, 56, slide.subtitle || slide.insight || slide.contact || '', {
      fontSize: 17,
      color: c.colors.accent,
      textAlign: 'center',
      fontFamily: c.fonts.body,
      lineHeight: 1.35,
    }),
  ]
}

const BUILDERS = {
  [FIXED_LAYOUT_IDS.COVER]: buildCover,
  [FIXED_LAYOUT_IDS.TOC]: buildToc,
  [FIXED_LAYOUT_IDS.CHAPTER]: buildChapter,
  [FIXED_LAYOUT_IDS.ROADMAP_BOTTOM]: buildRoadmapBottom,
  [FIXED_LAYOUT_IDS.SCENE_LEFT]: (c, slide) => buildLeftVisual(c, slide, 'scene'),
  [FIXED_LAYOUT_IDS.CHART_LEFT]: (c, slide) => buildLeftVisual(c, slide, 'chart'),
  [FIXED_LAYOUT_IDS.KEY_POINTS]: buildKeyPoints,
  [FIXED_LAYOUT_IDS.CLOSING]: buildClosing,
}

export function isFixedLayoutId(layoutId) {
  return VALID_FIXED_LAYOUTS.has(String(layoutId || ''))
}

export function resolveFixedSlide(slide) {
  const st = slide?.structured || slide || {}
  const layoutId = st.layout_id || st.fixed_layout || st.layout
  if (!isFixedLayoutId(layoutId)) return null
  return { ...st, layout_id: layoutId }
}

export function compileFixedDeckSlide(slide, viewportId = 'web-wide-1024', themeId = 'zjy-minimal') {
  const fixed = resolveFixedSlide(slide)
  if (!fixed) return []
  resetIds()
  const c = ctx(viewportId, themeId)
  const fn = BUILDERS[fixed.layout_id]
  return fn ? fn(c, fixed) : []
}
