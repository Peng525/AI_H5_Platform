/**
 * PPT严格模板 — 幻灯片编译引擎
 * 将 structured={template_type, variant, title, points/cards/items, ...}
 * 编译为 canvas_elements[] 供前端渲染
 *
 * 基于「中汽研_商务」模板 1280×720 画布坐标系
 */

import { getTheme, getThemeMargins, getThemeTypeScale } from '../constants/designThemes.js'
import { getLayoutCanvasSize } from '../constants/editorPresets.js'
import { CANVAS_Z } from '../constants/canvasLayers.js'
import { normalizeMaterialIconName } from './materialIcons.js'
import { measureTextBlock } from './measureTextBlock.js'
import { assignIcons } from './matchIcon.js'
import {
  PPT_CANVAS,
  COVER,
  TOC,
  CONTENT,
  computeGridLayout,
  PPT_COLORS,
  PPT_FONTS,
} from '../constants/pptTemplateLayout.js'

// ── 状态 ──
/** 全局字体缩放系数 — 解决 1280→848px 缩小时字体过小问题 */
const FONT_SCALE = 1.3

let _uid = 0

export function resetPptCompileIds() {
  _uid = 0
}

function uid(prefix = 'pt') {
  _uid += 1
  return `ppt_${prefix}_${_uid}`
}

// ── 工具函数 ──

function layoutCtx(viewportId, themeId) {
  const theme = getTheme(themeId)
  const scale = getThemeTypeScale(themeId, viewportId)
  const margin = getThemeMargins(themeId, viewportId)
  const { width: W, height: H } = getLayoutCanvasSize(viewportId)
  // 计算与1280×720的比例
  const sx = W / PPT_CANVAS.width
  const sy = H / PPT_CANVAS.height
  const fs = Math.min(sx, sy) * FONT_SCALE
  return { theme, scale, margin, W, H, sx, sy, fs, colors: PPT_COLORS, fonts: PPT_FONTS }
}

/** 按比例缩放坐标值 */
function scaleVal(v, s) {
  return Math.round(v * s)
}

/** 缩放矩形 */
function scaleRect(rect, sx, sy) {
  return {
    x: Math.round(rect.x * sx),
    y: Math.round(rect.y * sy),
    w: Math.round(rect.w * sx),
    h: Math.round(rect.h * sy),
  }
}

function textEl(id, x, y, w, h, content, style = {}, z = CANVAS_Z.CONTENT_BASE) {
  return {
    id,
    type: 'text',
    x,
    y,
    width: w,
    height: h,
    zIndex: z,
    content: String(content || ''),
    style: {
      background: 'transparent',
      color: PPT_COLORS.text,
      fontSize: 16,
      fontWeight: 'normal',
      fontFamily: PPT_FONTS.body,
      lineHeight: 1.35,
      textAlign: 'left',
      ...style,
    },
  }
}

function shapeEl(id, x, y, w, h, style = {}, z = CANVAS_Z.BACKGROUND) {
  return {
    id,
    type: 'shape',
    x,
    y,
    width: w,
    height: h,
    zIndex: z,
    content: '',
    style: { background: PPT_COLORS.primary, borderRadius: 0, ...style },
  }
}

function iconEl(id, x, y, size, name, color, z = CANVAS_Z.CONTENT_BASE + 1) {
  return {
    id,
    type: 'icon',
    x,
    y,
    width: size,
    height: size,
    zIndex: z,
    content: normalizeMaterialIconName(name),
    style: { background: 'transparent', color: color || PPT_COLORS.accent },
  }
}

function fitText(x, y, boxW, boxH, content, baseStyle, zIdx = CANVAS_Z.CONTENT_BASE) {
  const str = String(content || '').trim()
  if (!str || boxW <= 0 || boxH <= 0) {
    return textEl(uid('t'), x, y, Math.max(boxW, 1), Math.min(Math.max(boxH, 1), 16), str, baseStyle, zIdx)
  }
  let fontSize = baseStyle.fontSize || 16
  const minFontSize = baseStyle.minFontSize ?? 10
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
      return textEl(uid('t'), x, y, boxW, m.height, str, { ...baseStyle, fontSize }, zIdx)
    }
    fontSize -= 1
  }
  const truncated = str.length > 80 ? `${str.slice(0, 77)}…` : str
  return textEl(uid('t'), x, y, boxW, Math.min(boxH, 18), truncated, { ...baseStyle, fontSize: minFontSize }, zIdx)
}

// ── 通用背景元素 ──

/** 内容页公用头部：顶部彩条 + 页眉渐变区 + 章节徽章 + 页面标题 + 分隔线 */
function addContentHeader(els, c, slide, pageNum = 0) {
  const { sx, sy, W } = c
  // 顶部彩条
  els.push(shapeEl(uid('top'), 0, 0, W, Math.round(6 * sy),
    { background: PPT_COLORS.primary, borderRadius: 0 },
    CANVAS_Z.BACKGROUND + 10))

  // 头部背景渐变
  const hdr = scaleRect(CONTENT.headerBg, sx, sy)
  els.push(shapeEl(uid('hbg'), hdr.x, hdr.y, hdr.w, hdr.h,
    { background: '#F3F4F6', borderRadius: 0 },
    CANVAS_Z.BACKGROUND + 5))

  // 章节徽章
  const badge = scaleRect(CONTENT.chapterBadge, sx, sy)
  els.push(shapeEl(uid('badge'), badge.x, badge.y, badge.w, badge.h,
    { background: PPT_COLORS.primary, borderRadius: 4 },
    CANVAS_Z.BACKGROUND + 8))

  // 页码（徽章内居中）
  const numPos = scaleRect(CONTENT.chapterNum, sx, sy)
  els.push(textEl(uid('pn'), numPos.x - 20, numPos.y - 12, badge.w, badge.h,
    String(pageNum || ''), {
      fontSize: Math.round(24 * fs),
      fontWeight: 'bold',
      color: PPT_COLORS.white,
      fontFamily: PPT_FONTS.number,
      textAlign: 'center',
    }, CANVAS_Z.CONTENT_BASE + 1))

  // 页面标题
  const title = scaleRect(CONTENT.pageTitle, sx, sy)
  els.push(fitText(title.x, title.y, title.w, title.h,
    slide.title || '', {
      fontSize: Math.round(24 * fs),
      fontWeight: 'bold',
      color: PPT_COLORS.text,
      fontFamily: PPT_FONTS.display,
      lineHeight: 1.2,
    }))

  // 头部分隔线
  const hline = scaleRect(CONTENT.headerLine, sx, sy)
  els.push(shapeEl(uid('hline'), hline.x, hline.y, hline.w, hline.h,
    { background: '#E5E7EB', borderRadius: 0 },
    CANVAS_Z.BACKGROUND + 6))
}

/** 内容页公用底部：底栏 + 页码 */
function addContentFooter(els, c, pageNum = 0) {
  const { sx, sy, W } = c
  const fb = scaleRect(CONTENT.footerBar, sx, sy)
  els.push(shapeEl(uid('fbar'), fb.x, fb.y, fb.w, fb.h,
    { background: PPT_COLORS.primary, borderRadius: 0 },
    CANVAS_Z.BACKGROUND + 10))

  const pn = scaleRect(CONTENT.pageNum, sx, sy)
  els.push(textEl(uid('fpn'), pn.x - 30, pn.y, pn.w, pn.h,
    String(pageNum), {
      fontSize: Math.round(14 * fs),
      color: PPT_COLORS.textLight,
      fontFamily: PPT_FONTS.number,
      textAlign: 'right',
    }))
}

// ── 封面页 builder ──

function buildTitlePage(c, slide) {
  const { sx, sy, W } = c
  const els = []

  // 全屏深蓝背景
  els.push(shapeEl(uid('cov'), 0, 0, W, c.H,
    { background: '#001F4D', borderRadius: 0 },
    CANVAS_Z.BACKGROUND - 1))

  // 顶部亮色条
  els.push(shapeEl(uid('tbar'), 0, 0, W, Math.round(6 * sy),
    { background: PPT_COLORS.accent, borderRadius: 0 },
    CANVAS_Z.BACKGROUND + 10))

  // 主标题
  const t = scaleRect(COVER.title, sx, sy)
  els.push(fitText(t.x, t.y, t.w, t.h,
    slide.title || '演示标题', {
      fontSize: Math.round(48 * fs),
      fontWeight: 'bold',
      color: PPT_COLORS.white,
      fontFamily: PPT_FONTS.display,
      lineHeight: 1.15,
    }))

  // 装饰横线
  const bar = scaleRect(COVER.accentBar, sx, sy)
  els.push(shapeEl(uid('abar'), bar.x, bar.y, bar.w, bar.h,
    { background: PPT_COLORS.accentRed, borderRadius: 3 },
    CANVAS_Z.CONTENT_BASE))

  // 副标题
  if (slide.subtitle) {
    const st = scaleRect(COVER.subtitle, sx, sy)
    els.push(fitText(st.x, st.y, st.w, st.h,
      slide.subtitle, {
        fontSize: Math.round(24 * fs),
        fontWeight: 'normal',
        color: 'rgba(255,255,255,0.9)',
        fontFamily: PPT_FONTS.body,
        lineHeight: 1.3,
      }))
  }

  // 作者日期区
  if (slide.author) {
    const al = scaleRect(COVER.authorLabel, sx, sy)
    els.push(fitText(al.x, al.y, al.w, al.h,
      '汇报人 / 部门', {
        fontSize: Math.round(14 * fs),
        color: 'rgba(255,255,255,0.7)',
        fontFamily: PPT_FONTS.body,
      }))
    const av = scaleRect(COVER.authorValue, sx, sy)
    els.push(fitText(av.x, av.y, av.w, av.h,
      slide.author, {
        fontSize: Math.round(20 * fs),
        fontWeight: 'bold',
        color: PPT_COLORS.white,
        fontFamily: PPT_FONTS.display,
      }))
  }
  if (slide.date) {
    const dl = scaleRect(COVER.dateLabel, sx, sy)
    els.push(fitText(dl.x, dl.y, dl.w, dl.h,
      '日期', {
        fontSize: Math.round(14 * fs),
        color: 'rgba(255,255,255,0.7)',
        fontFamily: PPT_FONTS.body,
      }))
    const dv = scaleRect(COVER.dateValue, sx, sy)
    els.push(fitText(dv.x, dv.y, dv.w, dv.h,
      slide.date, {
        fontSize: Math.round(20 * fs),
        fontWeight: 'bold',
        color: PPT_COLORS.white,
        fontFamily: PPT_FONTS.number,
      }))
  }

  return els
}

// ── 目录页 builder ──

function buildTocPage(c, slide) {
  const { sx, sy, W } = c
  const els = []

  // 浅灰背景
  els.push(shapeEl(uid('bg'), 0, 0, W, c.H,
    { background: PPT_COLORS.bgLight, borderRadius: 0 },
    CANVAS_Z.BACKGROUND - 1))

  // 顶部彩条
  els.push(shapeEl(uid('tbar'), 0, 0, W, Math.round(6 * sy),
    { background: PPT_COLORS.primary, borderRadius: 0 },
    CANVAS_Z.BACKGROUND + 10))

  // 背景数字
  const bn = scaleRect(TOC.bgNumber, sx, sy)
  els.push(textEl(uid('bn'), bn.x, bn.y, bn.w, bn.h,
    '目录', {
      fontSize: Math.round(48 * fs),
      fontWeight: 'bold',
      color: '#E0E0E0',
      fontFamily: PPT_FONTS.number,
    }))

  // 标题文字
  const tt = scaleRect(TOC.title, sx, sy)
  els.push(fitText(tt.x, tt.y, tt.w, tt.h,
    slide.title || '目录 CONTENTS', {
      fontSize: Math.round(30 * fs),
      fontWeight: 'bold',
      color: PPT_COLORS.primary,
      fontFamily: PPT_FONTS.display,
      lineHeight: 1.2,
    }))

  // 分隔线
  const div = scaleRect(TOC.divider, sx, sy)
  els.push(shapeEl(uid('div'), div.x, div.y, div.w, div.h,
    { background: '#D1D5DB', borderRadius: 0 },
    CANVAS_Z.BACKGROUND + 6))

  // 目录项
  const items = slide.items || slide.points || []
  const itemLeft = scaleRect(TOC.itemLeft, sx, sy)
  const itemRight = scaleRect(TOC.itemRight, sx, sy)
  const rowGap = scaleVal(TOC.rowGap, sy)
  const card = TOC.card

  items.forEach((item, i) => {
    const isLeft = i % 2 === 0
    const base = isLeft ? itemLeft : itemRight
    const row = Math.floor(i / 2)
    const ox = base.x
    const oy = base.y + row * rowGap
    const bw = base.w
    const bh = base.h

    // 卡片背景（带阴影模拟）
    els.push(shapeEl(uid('toc_bg'), ox + 3, oy + 3, bw, bh,
      { background: 'rgba(0,0,0,0.05)', borderRadius: 4 },
      CANVAS_Z.BACKGROUND + 4))
    els.push(shapeEl(uid('toc_card'), ox, oy, bw, bh,
      { background: PPT_COLORS.white, borderRadius: 4, border: 'none' },
      CANVAS_Z.BACKGROUND + 5))

    // 左侧色条
    const barW = scaleVal(card.accentBar.w, sx)
    els.push(shapeEl(uid('toc_bar'), ox, oy, barW, bh,
      { background: PPT_COLORS.primary, borderRadius: 2 },
      CANVAS_Z.BACKGROUND + 6))

    // 序号
    const num = item.num || String(i + 1).padStart(2, '0')
    els.push(textEl(uid('toc_n'), ox + scaleVal(card.number.x, sx), oy + scaleVal(card.number.y, sy),
      scaleVal(card.number.w, sx), scaleVal(card.number.h, sy),
      num, {
        fontSize: Math.round(40 * fs),
        fontWeight: 'bold',
        color: PPT_COLORS.watermark,
        fontFamily: PPT_FONTS.number,
      }))

    // 标题
    els.push(fitText(ox + scaleVal(card.title.x, sx), oy + scaleVal(card.title.y, sy),
      scaleVal(card.title.w, sx), scaleVal(card.title.h, sy),
      item.title || '', {
        fontSize: Math.round(20 * fs),
        fontWeight: 'bold',
        color: PPT_COLORS.text,
        fontFamily: PPT_FONTS.display,
        lineHeight: 1.2,
      }))
  })

  return els
}

// ── 要点页 builder ──

function buildPointsPage(c, slide) {
  const { sx, sy } = c
  const els = []
  const points = assignIcons(slide.points || [])  // 🆕 自动匹配图标
  const variant = Math.min(points.length, 5)
  const bodyArea = scaleRect(CONTENT.body, sx, sy)

  addContentHeader(els, c, slide)
  addContentFooter(els, c, slide)

  const { cellW, cellH, gap, positions } = computeGridLayout(variant, bodyArea)

  for (let i = 0; i < variant; i++) {
    const point = points[i]
    const pos = positions[i]
    if (!pos) continue

    const pad = Math.round(16 * fs)
    const iconSize = Math.round(22 * fs)

    els.push(shapeEl(uid('pcard'), pos.x, pos.y, cellW, cellH, {
      background: PPT_COLORS.bgLight,
      border: `1px solid rgba(107,114,128,0.2)`,
      borderRadius: 10,
    }))

    els.push(iconEl(uid('pic'), pos.x + pad, pos.y + pad, iconSize,
      point.icon || 'circle', PPT_COLORS.accent))

    const textX = pos.x + pad + iconSize + 12
    const textW = cellW - pad * 2 - iconSize - 12
    const textY = pos.y + pad
    const textH = cellH - pad * 2

    els.push(fitText(textX, textY, textW, textH,
      point.text || point.title || point.body || '', {
        fontSize: Math.round(15 * fs),
        color: PPT_COLORS.textMuted,
        fontFamily: PPT_FONTS.body,
        lineHeight: 1.45,
      }))
  }

  return els
}

// ── 卡片页 builder ──

function buildCardsPage(c, slide) {
  const { sx, sy } = c
  const els = []
  const cards = assignIcons(slide.cards || [])  // 🆕 自动匹配图标
  const variant = Math.min(cards.length, 4)
  const bodyArea = scaleRect(CONTENT.body, sx, sy)

  // 头部和底部
  addContentHeader(els, c, slide)
  addContentFooter(els, c, slide)

  // 计算网格布局
  const { cellW, cellH, gap, positions } = computeGridLayout(variant, bodyArea)

  // 渲染卡片
  for (let i = 0; i < Math.min(variant, cards.length); i++) {
    const card = cards[i]
    const pos = positions[i]
    if (!pos) continue

    const pad = Math.round(20 * fs)
    const iconSize = Math.round(28 * fs)
    const titleH = Math.round(cellH * 0.18)
    const bodyH = Math.max(40, cellH - pad * 2 - iconSize - 16 - titleH - 16)

    // 卡片背景
    els.push(shapeEl(uid('ccard'), pos.x, pos.y, cellW, cellH, {
      background: PPT_COLORS.white,
      border: `1px solid rgba(107,114,128,0.15)`,
      borderRadius: 12,
    }))

    // 图标
    els.push(iconEl(uid('cic'), pos.x + pad, pos.y + pad, iconSize,
      card.icon || 'star', PPT_COLORS.accent))

    // 卡片标题
    let cy = pos.y + pad + iconSize + 12
    els.push(fitText(pos.x + pad, cy, cellW - pad * 2, titleH,
      card.title || '', {
        fontSize: Math.round(18 * fs),
        fontWeight: '600',
        color: PPT_COLORS.text,
        fontFamily: PPT_FONTS.display,
        lineHeight: 1.2,
      }))

    // 卡片正文
    cy += titleH + 8
    els.push(fitText(pos.x + pad, cy, cellW - pad * 2, bodyH,
      card.body || '', {
        fontSize: Math.round(13 * fs),
        color: PPT_COLORS.textMuted,
        fontFamily: PPT_FONTS.body,
        lineHeight: 1.4,
      }))
  }

  return els
}

// ── 图文混排 builder（image_text_left / image_text_right）──

function imageEl(id, x, y, w, h, url, z = CANVAS_Z.CONTENT_BASE) {
  return {
    id,
    type: 'image',
    x,
    y,
    width: w,
    height: h,
    zIndex: z,
    content: String(url || ''),
    style: { background: '#F3F6FA', objectFit: 'cover', borderRadius: 12 },
  }
}

function buildImageText(c, slide, imageOnLeft) {
  const { sx, sy } = c
  const els = []
  const bodyArea = scaleRect(CONTENT.body, sx, sy)
  const gap = Math.round(24 * fs)
  const imageW = Math.round(bodyArea.w * 0.44)
  const contentW = bodyArea.w - imageW - gap
  const imageX = imageOnLeft ? bodyArea.x : bodyArea.x + contentW + gap
  const contentX = imageOnLeft ? bodyArea.x + imageW + gap : bodyArea.x

  // 头部和底部
  addContentHeader(els, c, slide)
  addContentFooter(els, c, slide)

  // ── 图片区域 ──
  const imgH = bodyArea.h
  if (slide.image_url) {
    els.push(imageEl(uid('img'), imageX, bodyArea.y, imageW, imgH, slide.image_url))
  } else {
    // 占位区（无图片时显示）
    els.push(shapeEl(uid('imgph'), imageX, bodyArea.y, imageW, imgH, {
      background: PPT_COLORS.bgLight,
      border: `1px dashed ${PPT_COLORS.textLight}`,
      borderRadius: 12,
    }))
    const phIconSize = Math.round(36 * fs)
    els.push(iconEl(uid('phi'), imageX + Math.round((imageW - phIconSize) / 2),
      bodyArea.y + Math.round(imgH / 2) - phIconSize - 8,
      phIconSize, 'image', PPT_COLORS.textLight))
    els.push(fitText(imageX + 20, bodyArea.y + Math.round(imgH / 2) + 8,
      imageW - 40, 40, slide.image_topic || '配图区', {
        fontSize: Math.round(14 * fs),
        color: PPT_COLORS.textLight,
        fontFamily: PPT_FONTS.body,
        textAlign: 'center',
      }))
  }

  // ── 内容区域 ──
  const content = slide.content_type === 'cards'
    ? (assignIcons(slide.cards || []))
    : (assignIcons(slide.points || []))
  const variant = Math.min(content.length, slide.content_type === 'cards' ? 3 : 4)

  const pad = Math.round(14 * fs)
  const iconSize = Math.round(20 * fs)
  const gap2 = Math.round(12 * fs)
  const itemH = Math.min(Math.round(imgH / Math.max(variant, 1)) - gap2, Math.round(imgH * 0.38))

  for (let i = 0; i < variant; i++) {
    const item = content[i]
    const iy = bodyArea.y + i * (itemH + gap2)

    // 紧凑卡片背景
    els.push(shapeEl(uid('icard'), contentX, iy, contentW, itemH, {
      background: PPT_COLORS.white,
      border: `1px solid rgba(107,114,128,0.12)`,
      borderRadius: 8,
    }))

    els.push(iconEl(uid('ici'), contentX + pad, iy + pad, iconSize,
      item.icon || 'circle', PPT_COLORS.accent))

    const textX = contentX + pad + iconSize + 10
    const textW = contentW - pad * 2 - iconSize - 10

    if (slide.content_type === 'cards' && item.title) {
      // 卡片模式：标题 + 正文
      const titleH = Math.round(itemH * 0.35)
      els.push(fitText(textX, iy + pad, textW, titleH, item.title, {
        fontSize: Math.round(16 * fs),
        fontWeight: '600',
        color: PPT_COLORS.text,
        fontFamily: PPT_FONTS.display,
        lineHeight: 1.2,
      }))
      els.push(fitText(textX, iy + pad + titleH + 4, textW, itemH - pad * 2 - titleH - 4,
        item.body || '', {
          fontSize: Math.round(12 * fs),
          color: PPT_COLORS.textMuted,
          fontFamily: PPT_FONTS.body,
          lineHeight: 1.3,
        }))
    } else {
      // 要点模式：单行文本
      els.push(fitText(textX, iy + pad, textW, itemH - pad * 2,
        item.text || item.title || '', {
          fontSize: Math.round(14 * fs),
          color: PPT_COLORS.text,
          fontFamily: PPT_FONTS.body,
          lineHeight: 1.4,
        }))
    }
  }

  return els
}

function buildImageTextLeft(c, slide) {
  return buildImageText(c, slide, true)
}

function buildImageTextRight(c, slide) {
  return buildImageText(c, slide, false)
}

// ── 注册与导出 ──

const BUILDERS = {
  title_page: buildTitlePage,
  toc: buildTocPage,
  points: buildPointsPage,
  cards: buildCardsPage,
  image_text_left: buildImageTextLeft,
  image_text_right: buildImageTextRight,
}

/** 判断是否是PPT严格约束模板 */
export function isPptConstrainedTemplate(templateType) {
  return templateType && [
    'title_page', 'toc', 'points', 'cards',
    'image_text_left', 'image_text_right',
  ].includes(templateType)
}

/** 编译PPT严格模板slide → canvas_elements */
export function compilePptConstrainedSlide(slide, viewportId = 'web-wide-1024', themeId = 'zjy-minimal') {
  const st = slide?.structured || slide || {}
  const templateType = st.template_type
  if (!isPptConstrainedTemplate(templateType)) return []

  resetPptCompileIds()
  const c = layoutCtx(viewportId, themeId)
  const fn = BUILDERS[templateType]
  return fn ? fn(c, st) : []
}
