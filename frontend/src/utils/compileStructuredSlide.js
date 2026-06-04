/**
 * 结构化幻灯片 → canvas_elements（流式 Y 排版 + 文本测量）
 */
import { getTheme, getThemeMargins, getThemeTypeScale, isWebViewport } from '../constants/designThemes.js'
import { CANVAS_Z } from '../composables/useSlideCanvas.js'
import { measureTextBlock } from './measureTextBlock.js'

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

function shapeEl(id, x, y, w, h, style, z = CANVAS_Z.CONTENT_BASE) {
  return { id, type: 'shape', x, y, width: w, height: h, zIndex: z, content: '', style }
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
    content: name || 'circle',
    style: { color: color || '#156082', background: 'transparent' },
  }
}

function chartPlaceholderEl(x, y, w, h, colors) {
  const bgId = uid('ph')
  const iconId = uid('phi')
  const labelId = uid('phl')
  return [
    {
      id: bgId,
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
    iconEl(iconId, x + w / 2 - 24, y + h / 2 - 36, 48, 'analytics', colors.textMuted, CANVAS_Z.BACKGROUND + 1),
    textEl(
      labelId,
      x,
      y + h / 2 + 20,
      w,
      32,
      '图表占位',
      {
        fontSize: 14,
        color: colors.textMuted,
        textAlign: 'center',
        fontFamily: 'inherit',
      },
      CANVAS_Z.BACKGROUND + 1
    ),
  ]
}

function layoutCtx(viewportId, themeId) {
  const theme = getTheme(themeId)
  const scale = getThemeTypeScale(themeId, viewportId)
  const margin = getThemeMargins(themeId, viewportId)
  const web = isWebViewport(viewportId)
  const W = web ? 1280 : 375
  const H = web ? 720 : 812
  const { colors, fonts } = theme
  return { theme, scale, margin, web, W, H, colors, fonts }
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

function buildCover(c, st) {
  const { scale, margin, colors, fonts, H } = c
  const y0 = Math.round(H * 0.32)
  return [
    shapeEl(uid('bar'), margin.x + margin.contentWidth / 2 - (c.web ? 60 : 40), y0 + (c.web ? 100 : 88), c.web ? 120 : 80, 3, {
      background: colors.accent,
      borderRadius: 2,
    }),
    textEl(uid('t'), margin.x, y0, margin.contentWidth, c.web ? 80 : 64, st.title || '主标题', {
      fontSize: scale.display,
      fontWeight: 'bold',
      color: colors.text,
      fontFamily: fonts.display,
      textAlign: 'center',
    }),
    textEl(uid('s'), margin.x, y0 + (c.web ? 96 : 76), margin.contentWidth, c.web ? 48 : 40, st.subtitle || '', {
      fontSize: scale.body,
      color: colors.textMuted,
      fontFamily: fonts.body,
      textAlign: 'center',
    }),
  ]
}

function buildSection(c, st) {
  const { scale, margin, colors, fonts, H } = c
  let y = Math.round(H * 0.28)
  const els = [
    shapeEl(uid('bar'), margin.x, y, 4, c.web ? 120 : 100, { background: colors.accent, borderRadius: 2 }),
  ]
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
    const t2 = measuredText(margin.x + 16, y, margin.contentWidth - 16, body, {
      fontSize: scale.body,
      color: colors.textMuted,
      fontFamily: fonts.body,
    })
    els.push(t2.el)
  }
  return els
}

function buildGrid2x2(c, st) {
  const { scale, margin, colors, fonts } = c
  const modules = (st.modules || []).slice(0, 4)
  while (modules.length < 4) modules.push({ title: '模块', body: '内容', icon: 'circle' })

  const gap = c.web ? 20 : 12
  const headerH = c.web ? 56 : 44
  let y = c.web ? 100 : 88
  const els = []

  if (st.title) {
    els.push(
      textEl(uid('h'), margin.x, y - headerH, margin.contentWidth, headerH, st.title, {
        fontSize: scale.h2,
        fontWeight: '600',
        color: colors.text,
        fontFamily: fonts.display,
      })
    )
  }
  if (st.headline) {
    const hl = measuredText(margin.x, y - headerH - (c.web ? 48 : 40), margin.contentWidth, st.headline, {
      fontSize: scale.h1,
      fontWeight: 'bold',
      color: colors.accent,
      fontFamily: fonts.display,
    })
    els.push(hl.el)
  }

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
      const bodyH = measureTextBlock({
        content: mod.body || '',
        width: innerW,
        fontSize: scale.caption,
        fontFamily: fonts.body,
      }).height
      return pad * 2 + iconSize + 8 + titleH + 6 + bodyH
    })
    const rowH = Math.max(...cellHeights, c.web ? 140 : 120)

    rowMods.forEach((mod, col) => {
      const x = margin.x + col * (colW + gap)
      els.push(
        shapeEl(uid('card'), x, y, colW, rowH, {
          background: colors.bgMuted,
          borderRadius: 12,
          border: `1px solid ${colors.textMuted}33`,
        })
      )
      els.push(iconEl(uid('ic'), x + pad, y + pad, iconSize, mod.icon || 'circle', colors.accent))
      let cy = y + pad + iconSize + 8
      const tTitle = measuredText(x + pad, cy, colW - pad * 2, mod.title || '', {
        fontSize: scale.body,
        fontWeight: '600',
        color: colors.text,
        fontFamily: fonts.display,
      })
      els.push(tTitle.el)
      cy += tTitle.height + 6
      const tBody = measuredText(x + pad, cy, colW - pad * 2, mod.body || '', {
        fontSize: scale.caption,
        color: colors.textMuted,
        fontFamily: fonts.body,
      })
      els.push(tBody.el)
    })
    y += rowH + gap
  }
  return els
}

function buildCardsRow(c, st) {
  const { scale, margin, colors, fonts } = c
  const modules = (st.modules || []).slice(0, 4)
  const count = Math.max(modules.length, 3)
  const gap = c.web ? 16 : 10
  const cardW = Math.floor((margin.contentWidth - gap * (count - 1)) / count)
  let y = c.web ? 120 : 100
  const els = []

  if (st.title) {
    els.push(
      textEl(uid('h'), margin.x, y - 52, margin.contentWidth, 44, st.title, {
        fontSize: scale.h2,
        fontWeight: '600',
        color: colors.text,
        fontFamily: fonts.display,
      })
    )
  }

  const heights = modules.map((mod) => {
    const innerW = cardW - 24
    return (
      24 +
      28 +
      8 +
      measureTextBlock({ content: mod.title || '', width: innerW, fontSize: scale.body, fontWeight: '600' }).height +
      measureTextBlock({ content: mod.body || '', width: innerW, fontSize: scale.caption }).height
    )
  })
  const cardH = Math.max(...heights, c.web ? 180 : 150)

  modules.forEach((mod, i) => {
    const x = margin.x + i * (cardW + gap)
    els.push(
      shapeEl(uid('card'), x, y, cardW, cardH, {
        background: '#ffffff',
        borderRadius: 12,
        border: `1px solid ${colors.textMuted}44`,
      })
    )
    els.push(iconEl(uid('ic'), x + 12, y + 12, 28, mod.icon || 'star', colors.accent))
    let cy = y + 48
    const tt = measuredText(x + 12, cy, cardW - 24, mod.title || '', {
      fontSize: scale.body,
      fontWeight: '600',
      color: colors.text,
      fontFamily: fonts.display,
    })
    els.push(tt.el)
    cy += tt.height + 6
    const tb = measuredText(x + 12, cy, cardW - 24, mod.body || '', {
      fontSize: scale.caption,
      color: colors.textMuted,
      fontFamily: fonts.body,
    })
    els.push(tb.el)
  })
  return els
}

function buildSplitLr(c, st) {
  const { scale, margin, colors, fonts, H } = c
  const gap = c.web ? 40 : 16
  const leftW = Math.floor((margin.contentWidth - gap) * 0.52)
  const rightW = margin.contentWidth - gap - leftW
  let y = c.web ? 100 : 88
  const els = []
  const leftMod = st.modules?.[0] || { title: st.title, body: st.subtitle || '' }

  if (st.title && st.title !== leftMod.title) {
    els.push(
      textEl(uid('ht'), margin.x, y - 48, margin.contentWidth, 40, st.title, {
        fontSize: scale.h2,
        fontWeight: '600',
        color: colors.text,
        fontFamily: fonts.display,
      })
    )
  }

  const lt = measuredText(margin.x, y, leftW, leftMod.title || st.title || '', {
    fontSize: scale.h2,
    fontWeight: '600',
    color: colors.text,
    fontFamily: fonts.display,
  })
  els.push(lt.el)
  let cy = y + lt.height + 12
  const lb = measuredText(margin.x, cy, leftW, leftMod.body || st.subtitle || '', {
    fontSize: scale.body,
    color: colors.textMuted,
    fontFamily: fonts.body,
  })
  els.push(lb.el)

  const phY = y
  const phH = Math.min(c.web ? 360 : 280, H - phY - 80)
  const phX = margin.x + leftW + gap
  els.push(...chartPlaceholderEl(phX, phY, rightW, phH, colors))
  return els
}

function buildStatHero(c, st) {
  const { scale, margin, colors, fonts, H } = c
  const mod = st.modules?.[0] || {}
  const y0 = Math.round(H * 0.28)
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
  const y0 = Math.round(H * 0.32)
  const stepW = Math.floor(margin.contentWidth / 3)
  const els = []
  if (st.title) {
    els.push(
      textEl(uid('h'), margin.x, y0 - 64, margin.contentWidth, 40, st.title, {
        fontSize: scale.h2,
        fontWeight: '600',
        color: colors.text,
        fontFamily: fonts.display,
        textAlign: 'center',
      })
    )
  }
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
      textEl(uid('l'), margin.x + i * stepW, y0 + (c.web ? 120 : 100), stepW, c.web ? 64 : 48, label, {
        fontSize: scale.caption,
        color: colors.textMuted,
        fontFamily: fonts.body,
        textAlign: 'center',
      })
    )
  })
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

export function compileStructuredSlide(structured, viewportId = 'web-1280', themeId = 'zjy-minimal') {
  if (!structured?.template) return []
  resetCompileIds()
  const c = layoutCtx(viewportId, themeId)
  const fn = BUILDERS[structured.template]
  if (!fn) return []
  return fn(c, structured)
}

export function resolveSlideStructured(slide) {
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

export function shouldCompileSlide(slide) {
  if (!slide) return false
  const hasCanvas = Array.isArray(slide.canvas_elements) && slide.canvas_elements.length > 0
  if (hasCanvas) return false
  return !!resolveSlideStructured(slide)
}

export function compileSlideIfNeeded(slide, viewportId, themeId) {
  const structured = resolveSlideStructured(slide)
  if (!structured) return slide?.canvas_elements || []
  return compileStructuredSlide(structured, viewportId, themeId)
}
