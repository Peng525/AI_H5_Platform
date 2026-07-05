/**
 * 结构化幻灯片 → canvas_elements（流式 Y 排版 + 文本测量）
 */
import { getTheme, getThemeMargins, getThemeTypeScale, isWebViewport } from '../constants/designThemes.js'
import { getLayoutCanvasSize, isWideWebViewport, WIDE_VIEWPORT_RATIO } from '../constants/editorPresets.js'
import { CANVAS_Z } from '../constants/canvasLayers.js'
import { measureTextBlock, truncateLines } from './measureTextBlock.js'
import { normalizeMaterialIconName } from './materialIcons.js'
import { compileFixedDeckSlide, resolveFixedSlide } from './compileFixedDeckSlide.js'

/** builder 行为变更时递增，触发 structured 页强制重编译 */
export const STRUCTURED_COMPILE_VERSION = 8

let _uid = 0
export function resetCompileIds() {
  _uid = 0
}

function uid(prefix = 'el') {
  _uid += 1
  return `${prefix}_${_uid}`
}

function textEl(id, x, y, w, h, content, style, z = CANVAS_Z.CONTENT_BASE) {
  return {
    id,
    type: 'text',
    x,
    y,
    width: w,
    height: h,
    zIndex: z,
    content: content || '',
    style: { background: 'transparent', textAlign: 'left', lineHeight: 1.5, ...style },
  }
}

function shapeEl(id, x, y, w, h, style = {}, z = CANVAS_Z.CONTENT_BASE) {
  return { id, type: 'shape', x, y, width: w, height: h, zIndex: z, content: '', style: { background: '#005daa', ...style } }
}

function iconEl(id, x, y, size, name, color, z = CANVAS_Z.CONTENT_BASE) {
  return {
    id,
    type: 'icon',
    x,
    y,
    width: size,
    height: size,
    zIndex: z,
    content: normalizeMaterialIconName(name),
    style: { color: color || '#156082', background: 'transparent' },
  }
}

function chartPlaceholderEl(x, y, w, h, colors) {
  return [
    {
      id: uid('ph'),
      type: 'chartPlaceholder',
      x,
      y,
      width: w,
      height: h,
      zIndex: CANVAS_Z.BACKGROUND,
      content: '',
      meta: { role: 'chart_placeholder', chartType: 'bar' },
      style: {
        background: colors.bgMuted,
        borderRadius: 12,
        border: `2px dashed ${colors.textMuted}`,
      },
    },
  ]
}

function layoutCtx(viewportId, themeId) {
  const theme = getTheme(themeId)
  const scale = getThemeTypeScale(themeId, viewportId)
  const margin = getThemeMargins(themeId, viewportId)
  const web = isWebViewport(viewportId)
  const { width: W, height: H } = getLayoutCanvasSize(viewportId)
  const { colors, fonts } = theme
  return { theme, scale, margin, web, wide: isWideWebViewport(viewportId), W, H, colors, fonts }
}

function measuredText(x, y, w, content, style, z) {
  const m = measureTextBlock({
    content,
    width: w,
    fontSize: style.fontSize || 16,
    lineHeight: style.lineHeight ?? 1.5,
    fontFamily: style.fontFamily,
    fontWeight: style.fontWeight,
  })
  return {
    el: textEl(uid('t'), x, y, w, m.height, content, style, z),
    height: m.height,
  }
}

/** 页眉：headline → title → subtitle 顺序堆叠 */
function stackPageHeader(c, st, startY, opts = {}) {
  const { scale, margin, colors, fonts } = c
  const x = opts.x ?? margin.x
  const w = opts.width ?? margin.contentWidth
  const gap = opts.gap ?? (c.wide ? 4 : 6)
  const includeSubtitle = opts.includeSubtitle !== false
  const els = []
  let y = startY

  if (st.headline) {
    const hl = measuredText(x, y, w, st.headline, {
      fontSize: opts.headlineSize ?? scale.h2,
      fontWeight: 'bold',
      color: colors.accent,
      fontFamily: fonts.display,
      lineHeight: 1.2,
      ...(opts.headlineStyle || {}),
    })
    els.push(hl.el)
    y += hl.height + gap
  }
  if (st.title) {
    const tt = measuredText(x, y, w, st.title, {
      fontSize: opts.titleSize ?? scale.h2,
      fontWeight: '600',
      color: colors.text,
      fontFamily: fonts.display,
      lineHeight: 1.25,
      ...(opts.titleStyle || {}),
    })
    els.push(tt.el)
    y += tt.height + gap
  }
  if (includeSubtitle && st.subtitle) {
    const sub = measuredText(x, y, w, st.subtitle, {
      fontSize: scale.body,
      color: colors.textMuted,
      fontFamily: fonts.body,
      lineHeight: 1.45,
    })
    els.push(sub.el)
    y += sub.height + gap
  }
  return { elements: els, nextY: y }
}

/** 在固定框内适配文本：缩字号 → 截断 */
function fitTextInBox(x, y, boxW, boxH, content, baseStyle, z = CANVAS_Z.CONTENT_BASE) {
  const text = String(content || '').trim()
  if (!text || boxW <= 0 || boxH <= 0) {
    return textEl(uid('t'), x, y, Math.max(boxW, 1), Math.min(boxH, 16), text, baseStyle, z)
  }
  let fontSize = baseStyle.fontSize || 16
  const minFontSize = baseStyle.minFontSize ?? 10
  const lineHeight = baseStyle.lineHeight ?? 1.3
  const verticalPadding = 4

  while (fontSize >= minFontSize) {
    const m = measureTextBlock({
      content: text,
      width: boxW,
      fontSize,
      lineHeight,
      fontFamily: baseStyle.fontFamily,
      fontWeight: baseStyle.fontWeight,
      verticalPadding,
    })
    if (m.height <= boxH) {
      return textEl(uid('t'), x, y, boxW, m.height, text, { ...baseStyle, fontSize }, z)
    }
    fontSize -= 1
  }

  const style = { ...baseStyle, fontSize: minFontSize }
  const probe = measureTextBlock({
    content: text,
    width: boxW,
    fontSize: minFontSize,
    lineHeight,
    fontFamily: baseStyle.fontFamily,
    fontWeight: baseStyle.fontWeight,
    verticalPadding,
  })
  const maxLines = Math.max(1, Math.floor((boxH - verticalPadding) / (minFontSize * lineHeight)))
  const truncated = truncateLines(probe.lines, maxLines).join('\n')
  const m = measureTextBlock({
    content: truncated,
    width: boxW,
    fontSize: minFontSize,
    lineHeight,
    fontFamily: baseStyle.fontFamily,
    fontWeight: baseStyle.fontWeight,
    verticalPadding,
  })
  return textEl(uid('t'), x, y, boxW, Math.min(boxH, m.height), truncated, style, z)
}

function cardSurface(colors) {
  return colors.bgMuted
}

function cardBorderStyle(colors) {
  return {
    borderRadius: 10,
    border: `1px solid ${colors.textMuted}33`,
  }
}

function appendGridCard(els, c, x, y, colW, rowH, mod, opts = {}) {
  const { scale, colors, fonts } = c
  const pad = opts.pad ?? 8
  const iconSize = opts.iconSize ?? 16
  const border = cardBorderStyle(colors)
  els.push(
    shapeEl(uid('card'), x, y, colW, rowH, {
      background: cardSurface(colors),
      borderRadius: opts.borderRadius ?? border.borderRadius,
      border: border.border,
    })
  )
  els.push(iconEl(uid('ic'), x + pad, y + pad, iconSize, mod.icon || 'circle', colors.accent))
  let cy = y + pad + iconSize + 4
  const innerW = colW - pad * 2
  const titleMaxH = Math.max(16, Math.round(rowH * 0.3))
  const titleEl = fitTextInBox(x + pad, cy, innerW, titleMaxH, mod.title || '', {
    fontSize: scale.caption,
    fontWeight: '600',
    color: colors.text,
    fontFamily: fonts.display,
    lineHeight: 1.2,
  })
  els.push(titleEl)
  cy += titleEl.height + 4
  const bodyMaxH = Math.max(12, y + rowH - pad - cy)
  const bodyEl = fitTextInBox(x + pad, cy, innerW, bodyMaxH, mod.body || '', {
    fontSize: Math.max(9, scale.caption - 2),
    minFontSize: 9,
    color: colors.textMuted,
    fontFamily: fonts.body,
    lineHeight: 1.3,
  })
  els.push(bodyEl)
}

function imageEl(id, x, y, w, h, url, z = CANVAS_Z.BACKGROUND) {
  return {
    id,
    type: 'image',
    x,
    y,
    width: w,
    height: h,
    zIndex: z,
    content: url || '',
    style: { background: 'transparent', objectFit: 'cover' },
  }
}

function resolveCoverImageUrl(st) {
  if (st.image_intent !== 'cover_bg') return ''
  return String(st.image_url || '').trim()
}

function resolveSceneImageUrl(mod) {
  const intent = mod?.image_intent || (mod?.role === 'scene_image' ? 'scene' : '')
  if (intent !== 'scene') return ''
  return String(mod?.image_url || '').trim()
}

function resolveRoadmapImageUrl(st) {
  if (st.image_intent !== 'roadmap') return ''
  return String(st.image_url || '').trim()
}

function buildCoverClassic(c, st, opts = {}) {
  const { scale, margin, colors, fonts, H } = c
  const y0 = opts.startY ?? Math.round(H * 0.2)
  const textW = opts.width ?? margin.contentWidth
  const x = opts.x ?? margin.x
  const z = opts.z ?? CANVAS_Z.CONTENT_BASE
  const els = []
  els.push(
    shapeEl(
      uid('bar'),
      x + textW / 2 - (c.web ? 60 : 40),
      y0 + (c.web ? 100 : 88),
      c.web ? 120 : 80,
      3,
      { background: colors.accent, borderRadius: 2 },
      z
    )
  )
  const titleMaxH = Math.round(H * 0.28)
  els.push(
    fitTextInBox(x, y0, textW, titleMaxH, st.title || '主标题', {
      fontSize: scale.display,
      fontWeight: 'bold',
      color: colors.text,
      fontFamily: fonts.display,
      textAlign: 'center',
      lineHeight: 1.25,
    }, z)
  )
  const subtitle = st.subtitle || st.modules?.[0]?.body || ''
  if (subtitle) {
    const subY = y0 + (c.web ? 96 : 76)
    const subMaxH = Math.max(24, H - subY - 24)
    els.push(
      fitTextInBox(x, subY, textW, subMaxH, subtitle, {
        fontSize: scale.body,
        color: colors.textMuted,
        fontFamily: fonts.body,
        textAlign: 'center',
        lineHeight: 1.45,
      }, z)
    )
  }
  return els
}

function buildCover(c, st) {
  const { W, H, margin, colors } = c
  const els = []
  const coverUrl = resolveCoverImageUrl(st)
  if (coverUrl) {
    els.push(imageEl(uid('img'), 0, 0, W, H, coverUrl, CANVAS_Z.BACKGROUND - 1))
    els.push(
      shapeEl(uid('ov'), 0, 0, W, H, { background: 'rgba(0,0,0,0.38)', borderRadius: 0 }, CANVAS_Z.BACKGROUND)
    )
  }
  els.push(...buildCoverClassic(c, st, { z: CANVAS_Z.CONTENT_BASE + 2 }))
  return els
}

function buildSectionWide(c, st) {
  const { scale, margin, colors, fonts, H } = c
  const topPad = 20
  const barH = Math.min(48, Math.round(H * 0.12))
  const els = []

  if (st.headline) {
    const header = stackPageHeader(c, st, topPad, { includeSubtitle: false, titleSize: scale.h2 })
    els.push(...header.elements)
    let y = header.nextY + 8
    const body = st.modules?.[0]?.body || st.subtitle || ''
    if (body) {
      const maxBodyH = Math.max(40, H - y - 16)
      els.push(
        fitTextInBox(margin.x, y, margin.contentWidth, maxBodyH, body, {
          fontSize: scale.body,
          color: colors.textMuted,
          fontFamily: fonts.body,
          lineHeight: 1.45,
        })
      )
    }
    return els
  }

  let y = topPad
  els.push(shapeEl(uid('bar'), margin.x, y, 4, barH, { background: colors.accent, borderRadius: 2 }))
  const t1 = measuredText(margin.x + 14, y, margin.contentWidth - 14, st.title || '章节', {
    fontSize: scale.h2,
    fontWeight: 'bold',
    color: colors.text,
    fontFamily: fonts.display,
    lineHeight: 1.25,
  })
  els.push(t1.el)
  y += Math.max(t1.height, barH) + 10
  const body = st.modules?.[0]?.body || st.subtitle || ''
  if (body) {
    const maxBodyH = Math.max(40, H - y - 16)
    els.push(
      fitTextInBox(margin.x + 14, y, margin.contentWidth - 14, maxBodyH, body, {
        fontSize: scale.body,
        color: colors.textMuted,
        fontFamily: fonts.body,
        lineHeight: 1.45,
      })
    )
  }
  return els
}

function buildSection(c, st) {
  if (c.wide || c.H < 500) {
    return buildSectionWide(c, st)
  }
  const { scale, margin, colors, fonts, H } = c
  const topY = Math.round(H * 0.12)
  const els = []

  if (st.headline) {
    const header = stackPageHeader(c, st, topY, { titleSize: scale.h1 })
    els.push(...header.elements)
    let y = header.nextY + 8
    const body = st.modules?.[0]?.body || (st.subtitle && !st.title ? st.subtitle : '')
    if (body) {
      const maxBodyH = Math.max(40, H - y - 16)
      els.push(
        fitTextInBox(margin.x, y, margin.contentWidth, maxBodyH, body, {
          fontSize: scale.body,
          color: colors.textMuted,
          fontFamily: fonts.body,
        })
      )
    }
    return els
  }

  let y = Math.round(H * 0.18)
  els.push(shapeEl(uid('bar'), margin.x, y, 4, c.web ? 120 : 100, { background: colors.accent, borderRadius: 2 }))
  const t1 = measuredText(margin.x + 16, y, margin.contentWidth - 16, st.title || '章节', {
    fontSize: scale.h1,
    fontWeight: 'bold',
    color: colors.text,
    fontFamily: fonts.display,
  })
  els.push(t1.el)
  y += t1.height + 12
  const body = st.modules?.[0]?.body || st.subtitle || ''
  if (body) {
    const maxBodyH = Math.max(40, H - y - 16)
    els.push(
      fitTextInBox(margin.x + 16, y, margin.contentWidth - 16, maxBodyH, body, {
        fontSize: scale.body,
        color: colors.textMuted,
        fontFamily: fonts.body,
      })
    )
  }
  return els
}

function buildGrid2x2Wide(c, st) {
  const { margin, H } = c
  const modules = [...(st.modules || [])].slice(0, 4)
  while (modules.length < 4) modules.push({ title: '模块', body: '内容', icon: 'circle' })

  const gap = 10
  const topPad = 12
  const bottomPad = 10
  const els = []

  const header = stackPageHeader(c, st, topPad, {
    titleSize: c.scale.body,
    gap: 4,
    includeSubtitle: false,
  })
  els.push(...header.elements)
  const gridY = header.nextY + 6

  const colW = Math.floor((margin.contentWidth - gap) / 2)
  const availH = H - gridY - bottomPad
  const rowH = Math.max(68, Math.floor((availH - gap) / 2))

  for (let row = 0; row < 2; row++) {
    for (let col = 0; col < 2; col++) {
      const mod = modules[row * 2 + col]
      const x = margin.x + col * (colW + gap)
      const y = gridY + row * (rowH + gap)
      appendGridCard(els, c, x, y, colW, rowH, mod, { pad: 8, iconSize: 16 })
    }
  }
  return els
}

function buildGrid2x2(c, st) {
  if (c.wide || c.H < 500) {
    return buildGrid2x2Wide(c, st)
  }
  const { scale, margin, colors, fonts } = c
  const modules = [...(st.modules || [])].slice(0, 4)
  while (modules.length < 4) modules.push({ title: '模块', body: '内容', icon: 'circle' })

  const gap = c.web ? 20 : 12
  const topPad = c.web ? 56 : 48
  const els = []

  const header = stackPageHeader(c, st, topPad, {
    titleSize: scale.h2,
    headlineSize: scale.h1,
    includeSubtitle: false,
  })
  els.push(...header.elements)
  let y = header.nextY + (c.web ? 16 : 12)

  const colW = Math.floor((margin.contentWidth - gap) / 2)
  const pad = c.web ? 16 : 12
  const iconSize = c.web ? 28 : 22

  for (let row = 0; row < 2; row++) {
    const rowMods = [modules[row * 2], modules[row * 2 + 1]]
    const cellHeights = rowMods.map((mod) => {
      const innerW = colW - pad * 2
      const titleH = measureTextBlock({
        content: mod.title || '',
        width: innerW,
        fontSize: scale.body,
        fontWeight: '600',
        fontFamily: fonts.display,
      }).height
      const bodyProbe = measureTextBlock({
        content: mod.body || '',
        width: innerW,
        fontSize: scale.caption,
        fontFamily: fonts.body,
      }).height
      return pad * 2 + iconSize + 8 + titleH + 6 + Math.min(bodyProbe, 80)
    })
    const rowH = Math.max(...cellHeights, c.web ? 140 : 120)

    rowMods.forEach((mod, col) => {
      appendGridCard(els, c, margin.x + col * (colW + gap), y, colW, rowH, mod, {
        pad,
        iconSize,
        borderRadius: 12,
      })
    })
    y += rowH + gap
  }
  return els
}

function buildCardsRow(c, st) {
  const { scale, margin, colors, fonts, H } = c
  const modules = [...(st.modules || [])].slice(0, 4)
  const count = Math.max(modules.length, 2)
  const gap = c.wide ? 12 : c.web ? 16 : 10
  const topPad = c.wide ? 12 : c.web ? 56 : 48
  const els = []

  const header = stackPageHeader(c, st, topPad, {
    titleSize: scale.h2,
    includeSubtitle: false,
    gap: c.wide ? 4 : 6,
  })
  els.push(...header.elements)
  let y = header.nextY + (c.wide ? 8 : 12)

  const cardW = Math.max(140, Math.floor((margin.contentWidth - gap * (count - 1)) / count))
  const maxCardH = Math.max(100, H - y - 16)
  const iconSize = c.wide ? 22 : 28
  const pad = 12
  const border = cardBorderStyle(colors)

  const cardHeights = modules.map((mod) => {
    const innerW = cardW - pad * 2
    const titleH = measureTextBlock({
      content: mod.title || '',
      width: innerW,
      fontSize: scale.body,
      fontWeight: '600',
      fontFamily: fonts.display,
    }).height
    const bodyProbe = measureTextBlock({
      content: mod.body || '',
      width: innerW,
      fontSize: scale.caption,
      fontFamily: fonts.body,
    }).height
    return pad + iconSize + 12 + titleH + 6 + Math.min(bodyProbe, maxCardH * 0.55)
  })
  const cardH = Math.min(Math.max(...cardHeights, c.wide ? 120 : c.web ? 160 : 130), maxCardH)

  modules.forEach((mod, i) => {
    const x = margin.x + i * (cardW + gap)
    els.push(
      shapeEl(uid('card'), x, y, cardW, cardH, {
        background: cardSurface(colors),
        borderRadius: border.borderRadius,
        border: border.border,
      })
    )
    els.push(iconEl(uid('ic'), x + pad, y + pad, iconSize, mod.icon || 'star', colors.accent))
    let cy = y + pad + iconSize + 8
    const innerW = cardW - pad * 2
    const titleMaxH = Math.round(cardH * 0.28)
    const titleEl = fitTextInBox(x + pad, cy, innerW, titleMaxH, mod.title || '', {
      fontSize: scale.body,
      fontWeight: '600',
      color: colors.text,
      fontFamily: fonts.display,
      lineHeight: 1.25,
    })
    els.push(titleEl)
    cy += titleEl.height + 6
    const bodyMaxH = y + cardH - pad - cy
    const bodyEl = fitTextInBox(x + pad, cy, innerW, bodyMaxH, mod.body || '', {
      fontSize: scale.caption,
      minFontSize: 9,
      color: colors.textMuted,
      fontFamily: fonts.body,
      lineHeight: 1.35,
    })
    els.push(bodyEl)
  })
  return els
}

function buildSplitLr(c, st) {
  const { scale, margin, colors, fonts, H } = c
  const gap = c.wide ? 12 : c.web ? 40 : 16
  const rightPad = c.wide ? 8 : 0
  const bottomPad = c.wide ? 12 : 16
  const topPad = c.wide ? 12 : c.web ? 56 : 48
  const els = []
  const leftMod = st.modules?.[0] || { title: st.title, body: st.subtitle || '' }
  const rightMod = st.modules?.[1] || {}

  const pageTitle = st.title && st.title !== leftMod.title ? st.title : ''
  const headerSt = pageTitle
    ? { ...st, title: pageTitle, headline: st.headline, subtitle: '' }
    : { headline: st.headline, title: '', subtitle: '' }

  const sceneUrl = resolveSceneImageUrl(rightMod)
  const useChartPlaceholder =
    rightMod.role === 'chart_placeholder' && !rightMod.image_url && !rightMod.image_prompt
  const hasRightImage = !!sceneUrl && !useChartPlaceholder

  const leftW = hasRightImage || useChartPlaceholder
    ? Math.floor((margin.contentWidth - gap) * 0.52)
    : margin.contentWidth
  const rightW = margin.contentWidth - gap - leftW - rightPad

  const header = stackPageHeader(c, headerSt, topPad, {
    includeSubtitle: false,
    width: leftW,
    x: margin.x,
  })
  els.push(...header.elements)
  let y = header.nextY + (c.wide ? 8 : 12)

  const titleMaxH = Math.round((H - y - bottomPad) * (hasRightImage || useChartPlaceholder ? 0.22 : 0.18))
  const lt = fitTextInBox(margin.x, y, leftW, titleMaxH, leftMod.title || st.title || '', {
    fontSize: scale.h2,
    fontWeight: '600',
    color: colors.text,
    fontFamily: fonts.display,
    lineHeight: 1.25,
  })
  els.push(lt)
  let cy = y + lt.height + 10
  const lbMaxH = Math.max(40, H - cy - bottomPad - (hasRightImage || useChartPlaceholder ? 0 : 0))
  const lb = fitTextInBox(margin.x, cy, leftW, lbMaxH, leftMod.body || st.subtitle || '', {
    fontSize: scale.body,
    color: colors.textMuted,
    fontFamily: fonts.body,
    lineHeight: 1.45,
  })
  els.push(lb)

  if (hasRightImage || useChartPlaceholder) {
    const phY = y
    const phH = Math.max(80, H - phY - bottomPad)
    const phX = margin.x + leftW + gap
    if (useChartPlaceholder) {
      els.push(...chartPlaceholderEl(phX, phY, rightW, phH, colors))
    } else {
      els.push(imageEl(uid('rimg'), phX, phY, rightW, phH, sceneUrl, CANVAS_Z.BACKGROUND))
    }
  } else if (rightMod.title || rightMod.body) {
    cy += lb.height + 12
    const rt = fitTextInBox(margin.x, cy, margin.contentWidth, 48, rightMod.title || '', {
      fontSize: scale.body,
      fontWeight: '600',
      color: colors.text,
      fontFamily: fonts.display,
      lineHeight: 1.25,
    })
    els.push(rt)
    cy += rt.height + 6
    const rbMaxH = Math.max(32, H - cy - bottomPad)
    els.push(
      fitTextInBox(margin.x, cy, margin.contentWidth, rbMaxH, rightMod.body || '', {
        fontSize: scale.caption,
        minFontSize: 9,
        color: colors.textMuted,
        fontFamily: fonts.body,
        lineHeight: 1.4,
      })
    )
  }
  return els
}

function buildStatHero(c, st) {
  const { scale, margin, colors, fonts, H } = c
  const mod = st.modules?.[0] || {}
  const y0 = Math.round(H * 0.22)
  const els = []
  if (st.title) {
    els.push(
      textEl(uid('h'), margin.x, y0 - 56, margin.contentWidth, 44, st.title, {
        fontSize: scale.h2,
        fontWeight: '600',
        color: colors.text,
        fontFamily: fonts.display,
        textAlign: 'center',
      })
    )
  }
  els.push(
    textEl(uid('n'), margin.x, y0, margin.contentWidth, c.web ? 100 : 80, mod.stat || st.headline || '86%', {
      fontSize: c.web ? scale.display + 12 : scale.display + 8,
      fontWeight: 'bold',
      color: colors.accent,
      fontFamily: fonts.display,
      textAlign: 'center',
    })
  )
  const desc = mod.desc || mod.body || st.subtitle || ''
  els.push(
    textEl(uid('d'), margin.x, y0 + (c.web ? 108 : 88), margin.contentWidth, c.web ? 48 : 40, desc, {
      fontSize: scale.body,
      color: colors.textMuted,
      fontFamily: fonts.body,
      textAlign: 'center',
    })
  )
  return els
}

function buildSteps(c, st) {
  const { scale, margin, colors, fonts, H } = c
  const steps = (st.modules || []).slice(0, 3)
  while (steps.length < 3) steps.push({ title: `步骤 ${steps.length + 1}`, body: '' })
  const topPad = c.wide ? 12 : Math.round(H * 0.14)
  const els = []
  const roadmapUrl = resolveRoadmapImageUrl(st)
  const roadmapH = roadmapUrl ? Math.max(72, Math.round(H * 0.26)) : 0
  const bottomReserve = roadmapUrl ? roadmapH + 16 : 16

  const header = stackPageHeader(c, st, topPad, {
    titleSize: scale.h2,
    includeSubtitle: false,
    titleStyle: { textAlign: 'center' },
    headlineStyle: { textAlign: 'center' },
  })
  if (header.elements.length) {
    els.push(
      ...header.elements.map((el) => ({
        ...el,
        style: { ...el.style, textAlign: 'center' },
      }))
    )
  }
  const y0 = header.nextY + (c.wide ? 12 : 24)
  const stepW = Math.floor(margin.contentWidth / 3)
  const labelMaxH = Math.max(40, H - y0 - (c.web ? 120 : 100) - bottomReserve)
  steps.forEach((s, i) => {
    const x = margin.x + i * stepW + stepW / 2 - (c.web ? 28 : 22)
    els.push(shapeEl(uid('c'), x, y0, c.web ? 56 : 44, c.web ? 56 : 44, { background: colors.accent, borderRadius: 999 }))
    els.push(
      textEl(uid('n'), margin.x + i * stepW, y0 + (c.web ? 64 : 52), stepW, c.web ? 28 : 24, String(i + 1), {
        fontSize: scale.body,
        color: colors.onAccent,
        fontFamily: fonts.body,
        textAlign: 'center',
        fontWeight: 'bold',
      }, CANVAS_Z.CONTENT_BASE + 1)
    )
    const label = s.title || s.body || `步骤 ${i + 1}`
    els.push(
      fitTextInBox(margin.x + i * stepW, y0 + (c.web ? 120 : 100), stepW, labelMaxH, label, {
        fontSize: scale.caption,
        minFontSize: 9,
        color: colors.textMuted,
        fontFamily: fonts.body,
        textAlign: 'center',
        lineHeight: 1.3,
      })
    )
  })
  if (roadmapUrl) {
    const imgY = H - roadmapH - 12
    els.push(imageEl(uid('rdm'), margin.x, imgY, margin.contentWidth, roadmapH, roadmapUrl, CANVAS_Z.BACKGROUND))
  }
  return els
}

function buildQuote(c, st) {
  const { scale, margin, colors, fonts, H } = c
  const y0 = Math.round(H * 0.3)
  const quote = st.quote || st.modules?.[0]?.quote || st.headline || '「金句」'
  const author = st.author || st.modules?.[0]?.author || ''
  return [
    textEl(uid('q'), margin.x, y0, margin.contentWidth, c.web ? 120 : 100, quote, {
      fontSize: scale.h2,
      color: colors.text,
      fontFamily: fonts.display,
      textAlign: 'center',
      fontWeight: '500',
    }),
    textEl(uid('a'), margin.x, y0 + (c.web ? 128 : 108), margin.contentWidth, c.web ? 36 : 32, author, {
      fontSize: scale.caption,
      color: colors.textMuted,
      fontFamily: fonts.body,
      textAlign: 'center',
    }),
  ]
}

function buildClosing(c, st) {
  const { scale, margin, colors, fonts, H } = c
  const y0 = Math.round(H * 0.34)
  const contact = st.contact || st.modules?.[0]?.contact || st.subtitle || ''
  return [
    textEl(uid('t'), margin.x, y0, margin.contentWidth, c.web ? 64 : 52, st.title || '谢谢', {
      fontSize: scale.display,
      fontWeight: 'bold',
      color: colors.text,
      fontFamily: fonts.display,
      textAlign: 'center',
    }),
    textEl(uid('c'), margin.x, y0 + (c.web ? 76 : 60), margin.contentWidth, c.web ? 48 : 40, contact, {
      fontSize: scale.body,
      color: colors.accent,
      fontFamily: fonts.body,
      textAlign: 'center',
    }),
  ]
}

const BUILDERS = {
  cover: buildCover,
  section: buildSection,
  split_lr: buildSplitLr,
  grid_2x2: buildGrid2x2,
  cards_row: buildCardsRow,
  stat_hero: buildStatHero,
  steps: buildSteps,
  quote: buildQuote,
  closing: buildClosing,
}

export function compileStructuredSlide(structured, viewportId = 'web-wide-1024', themeId = 'zjy-minimal') {
  if (resolveFixedSlide(structured)) return compileFixedDeckSlide(structured, viewportId, themeId)
  if (!structured?.template) return []
  resetCompileIds()
  const c = layoutCtx(viewportId, themeId)
  const fn = BUILDERS[structured.template]
  if (!fn) return []
  return fn(c, structured)
}

export function resolveSlideStructured(slide) {
  if (resolveFixedSlide(slide)) return resolveFixedSlide(slide)
  if (slide?.structured?.template) return slide.structured
  if (slide?.layout && BUILDERS[slide.layout]) {
    return {
      template: slide.layout,
      title: slide.title || '',
      subtitle: slide.subtitle || '',
      modules: (slide.bullets || []).map((b, i) => ({
        icon: ['target', 'lightbulb', 'analytics', 'groups'][i % 4],
        title: `要点 ${i + 1}`,
        body: String(b),
      })),
    }
  }
  return null
}

export function elementsOutOfBounds(elements, viewportId) {
  if (!elements?.length) return false
  const { width: W, height: H } = getLayoutCanvasSize(viewportId)
  return elements.some((el) => {
    const x = el.x ?? 0
    const y = el.y ?? 0
    const w = el.width ?? 0
    const h = el.height ?? 0
    return x < -2 || y < -2 || x + w > W + 2 || y + h > H + 2
  })
}

export function clampElementsToViewport(elements, viewportId) {
  if (!elements?.length) return elements || []
  const { width: W, height: H } = getLayoutCanvasSize(viewportId)
  const edge = 2
  const maxW = Math.max(1, W - edge * 2)
  const maxH = Math.max(1, H - edge * 2)
  return elements.map((el) => {
    let x = el.x ?? 0
    let y = el.y ?? 0
    let w = el.width ?? 0
    let h = el.height ?? 0
    if (x < edge) x = edge
    if (y < edge) y = edge
    if (w <= 0) w = 1
    if (h <= 0) h = 1
    if (w > maxW) w = maxW
    if (h > maxH) h = maxH
    if (x + w > W - edge) w = Math.max(1, W - edge - x)
    if (y + h > H - edge) h = Math.max(1, H - edge - y)
    if (x + w > W - edge) x = Math.max(edge, W - edge - w)
    if (y + h > H - edge) y = Math.max(edge, H - edge - h)
    return { ...el, x, y, width: w, height: h }
  })
}

/** 宽屏视口下元素仍挤在左侧（mobile 坐标未重编译） */
export function elementsLookMobileOnWideCanvas(elements, viewportId) {
  if (!elements?.length || !isWideWebViewport(viewportId)) return false
  const { width: W } = getLayoutCanvasSize(viewportId)
  const threshold = W * 0.45
  const maxRight = Math.max(...elements.map((el) => (el.x ?? 0) + (el.width ?? 0)))
  return maxRight < threshold
}

export function shouldCompileSlide(slide, viewportId) {
  if (!slide) return false
  const structured = resolveSlideStructured(slide)
  if (!structured) return false
  if (slide._compileVersion !== STRUCTURED_COMPILE_VERSION) return true
  const hasCanvas = Array.isArray(slide.canvas_elements) && slide.canvas_elements.length > 0
  if (!hasCanvas) return true
  if (!slide._compiledViewportId) return true
  if (slide._compiledViewportId !== viewportId) return true
  if (elementsLookMobileOnWideCanvas(slide.canvas_elements, viewportId)) return true
  if (elementsOutOfBounds(slide.canvas_elements, viewportId)) return true
  return false
}

function applyCompiledSlide(slide, elements, viewportId) {
  slide.canvas_elements = elements
  slide._compiledViewportId = viewportId
  slide._compileVersion = STRUCTURED_COMPILE_VERSION
  return elements
}

export function compileSlideIfNeeded(slide, viewportId, themeId) {
  const structured = resolveSlideStructured(slide)
  if (!structured) return slide?.canvas_elements || []
  const elements = clampElementsToViewport(
    compileStructuredSlide(structured, viewportId, themeId),
    viewportId
  )
  return applyCompiledSlide(slide, elements, viewportId)
}

export function ensureSlideCompiled(slide, viewportId, themeId) {
  if (!slide) return []
  const cached = slide.canvas_elements
  if (
    Array.isArray(cached) &&
    cached.length &&
    slide._compiledViewportId === viewportId &&
    slide._compileVersion === STRUCTURED_COMPILE_VERSION &&
    !elementsOutOfBounds(cached, viewportId) &&
    !elementsLookMobileOnWideCanvas(cached, viewportId)
  ) {
    return clampElementsToViewport(cached, viewportId)
  }
  if (!shouldCompileSlide(slide, viewportId)) {
    return clampElementsToViewport(cached || [], viewportId)
  }
  const structured = resolveSlideStructured(slide)
  if (!structured) return clampElementsToViewport(cached || [], viewportId)
  const elements = clampElementsToViewport(
    compileStructuredSlide(structured, viewportId, themeId),
    viewportId
  )
  return applyCompiledSlide(slide, elements, viewportId)
}

/** 批量 lazy compile（reveal 完成或跳过后调用） */
export function compileRemainingSlides(slides, viewportId, themeId, skipFirst = false) {
  for (let i = 0; i < (slides || []).length; i++) {
    if (skipFirst && i === 0) continue
    ensureSlideCompiled(slides[i], viewportId, themeId)
  }
}
