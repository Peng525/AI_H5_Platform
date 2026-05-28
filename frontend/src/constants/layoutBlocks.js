/**
 * 页面版式块：商务 8 + 叙事 6
 * buildBlock(blockId, viewportId, themeId) -> canvas_elements[]
 */
import {
  getTheme,
  getThemeMargins,
  getThemeTypeScale,
  isWebViewport,
} from './designThemes.js'

let _uid = 0
function uid(prefix = 'el') {
  _uid += 1
  return `${prefix}_${_uid}`
}

export function resetLayoutBlockIds() {
  _uid = 0
}

function text(id, x, y, w, h, content, style, z = 2) {
  return { id, type: 'text', x, y, width: w, height: h, zIndex: z, content, style: { background: 'transparent', textAlign: 'left', ...style } }
}

function shape(id, x, y, w, h, style, z = 1) {
  return { id, type: 'shape', x, y, width: w, height: h, zIndex: z, content: '', style }
}

function icon(id, x, y, size, name, style, z = 2) {
  return { id, type: 'icon', x, y, width: size, height: size, zIndex: z, content: name, style }
}

function ctx(themeId, viewportId) {
  const theme = getTheme(themeId)
  const scale = getThemeTypeScale(themeId, viewportId)
  const margin = getThemeMargins(themeId, viewportId)
  const web = isWebViewport(viewportId)
  const W = web ? 1280 : 375
  const H = web ? 692 : 785
  const { colors, fonts } = theme
  const cx = margin.x + margin.contentWidth / 2
  return { theme, scale, margin, web, W, H, colors, fonts, cx }
}

export const BUSINESS_LAYOUT_BLOCKS = [
  { id: 'cover-minimal', label: '封面', icon: 'title' },
  { id: 'section-title', label: '章节页', icon: 'view_headline' },
  { id: 'bullets-three', label: '三要点', icon: 'format_list_bulleted' },
  { id: 'two-column', label: '双栏', icon: 'view_column' },
  { id: 'stat-highlight', label: '数据强调', icon: 'pin' },
  { id: 'quote-center', label: '引用', icon: 'format_quote' },
  { id: 'steps-horizontal', label: '三步流程', icon: 'linear_scale' },
  { id: 'closing-minimal', label: '致谢', icon: 'favorite' },
]

export const STORY_LAYOUT_BLOCKS = [
  { id: 'story-cover', label: '叙事封面', icon: 'auto_stories' },
  { id: 'question-hook', label: '开篇提问', icon: 'help' },
  { id: 'icon-list-four', label: '四项清单', icon: 'checklist' },
  { id: 'big-stat-one', label: '数据洞察', icon: 'analytics' },
  { id: 'case-card', label: '案例卡片', icon: 'article' },
  { id: 'values-four', label: '价值观', icon: 'volunteer_activism' },
]

const BLOCK_BUILDERS = {
  'cover-minimal': (c, copy = {}) => {
    const { scale, margin, colors, fonts, cx, H } = c
    const y0 = Math.round(H * 0.32)
    return [
      shape(uid('bar'), cx - (c.web ? 60 : 40), y0 + (c.web ? 100 : 88), c.web ? 120 : 80, 3, { background: colors.accent, borderRadius: 2 }),
      text(uid('t'), margin.x, y0, margin.contentWidth, c.web ? 80 : 64, copy.title || '主标题', {
        fontSize: scale.display, fontWeight: 'bold', color: colors.text, fontFamily: fonts.display, textAlign: 'center', lineHeight: 1.2,
      }),
      text(uid('s'), margin.x, y0 + (c.web ? 96 : 76), margin.contentWidth, c.web ? 48 : 40, copy.subtitle || '副标题 / 一句话说明', {
        fontSize: scale.body, color: colors.textMuted, fontFamily: fonts.body, textAlign: 'center', lineHeight: 1.5,
      }),
    ]
  },

  'section-title': (c, copy = {}) => {
    const { scale, margin, colors, fonts, H } = c
    const y0 = Math.round(H * 0.28)
    return [
      shape(uid('bar'), margin.x, y0, 4, c.web ? 120 : 100, { background: colors.accent, borderRadius: 2 }),
      text(uid('t'), margin.x + 16, y0, margin.contentWidth - 16, c.web ? 56 : 48, copy.title || '章节标题', {
        fontSize: scale.h1, fontWeight: 'bold', color: colors.text, fontFamily: fonts.display,
      }),
      text(uid('b'), margin.x + 16, y0 + (c.web ? 68 : 56), margin.contentWidth - 16, c.web ? 80 : 72, copy.body || '本章导语，用一两句话概括内容。', {
        fontSize: scale.body, color: colors.textMuted, fontFamily: fonts.body, lineHeight: 1.6,
      }),
    ]
  },

  'bullets-three': (c, copy = {}) => {
    const { scale, margin, colors, fonts, H } = c
    const items = copy.items || ['核心观点一', '核心观点二', '核心观点三']
    const y0 = Math.round(H * 0.22)
    const els = [
      text(uid('h'), margin.x, y0 - (c.web ? 56 : 48), margin.contentWidth, c.web ? 44 : 36, copy.title || '要点概览', {
        fontSize: scale.h2, fontWeight: '600', color: colors.text, fontFamily: fonts.display,
      }),
    ]
    items.forEach((item, i) => {
      const y = y0 + i * (c.web ? 88 : 72)
      els.push(shape(uid('dot'), margin.x, y + 8, c.web ? 12 : 10, c.web ? 12 : 10, { background: colors.accent, borderRadius: 999 }))
      els.push(text(uid('b'), margin.x + (c.web ? 28 : 22), y, margin.contentWidth - 28, c.web ? 64 : 56, item, {
        fontSize: scale.body, color: colors.text, fontFamily: fonts.body, lineHeight: 1.5,
      }))
    })
    return els
  },

  'two-column': (c, copy = {}) => {
    const { scale, margin, colors, fonts, H } = c
    const gap = c.web ? 48 : 16
    const colW = Math.floor((margin.contentWidth - gap) / 2)
    const y0 = Math.round(H * 0.24)
    return [
      text(uid('l1'), margin.x, y0, colW, c.web ? 40 : 32, copy.leftTitle || '左侧标题', { fontSize: scale.h2, fontWeight: '600', color: colors.text, fontFamily: fonts.display }),
      text(uid('l2'), margin.x, y0 + (c.web ? 48 : 40), colW, c.web ? 120 : 100, copy.leftBody || '左侧说明文字。', { fontSize: scale.body, color: colors.textMuted, fontFamily: fonts.body, lineHeight: 1.55 }),
      text(uid('r1'), margin.x + colW + gap, y0, colW, c.web ? 40 : 32, copy.rightTitle || '右侧标题', { fontSize: scale.h2, fontWeight: '600', color: colors.text, fontFamily: fonts.display }),
      text(uid('r2'), margin.x + colW + gap, y0 + (c.web ? 48 : 40), colW, c.web ? 120 : 100, copy.rightBody || '右侧说明文字。', { fontSize: scale.body, color: colors.textMuted, fontFamily: fonts.body, lineHeight: 1.55 }),
    ]
  },

  'stat-highlight': (c, copy = {}) => {
    const { scale, margin, colors, fonts, cx, H } = c
    const y0 = Math.round(H * 0.3)
    return [
      text(uid('n'), margin.x, y0, margin.contentWidth, c.web ? 100 : 80, copy.stat || '86%', {
        fontSize: c.web ? scale.display + 12 : scale.display + 8, fontWeight: 'bold', color: colors.accent, fontFamily: fonts.display, textAlign: 'center',
      }),
      text(uid('d'), margin.x, y0 + (c.web ? 108 : 88), margin.contentWidth, c.web ? 48 : 40, copy.desc || '数据说明 / 同比提升', {
        fontSize: scale.body, color: colors.textMuted, fontFamily: fonts.body, textAlign: 'center', lineHeight: 1.5,
      }),
      shape(uid('ln'), cx - (c.web ? 40 : 28), y0 + (c.web ? 168 : 140), c.web ? 80 : 56, 2, { background: colors.bgMuted, borderRadius: 1 }),
    ]
  },

  'quote-center': (c, copy = {}) => {
    const { scale, margin, colors, fonts, H } = c
    const y0 = Math.round(H * 0.3)
    return [
      text(uid('q'), margin.x, y0, margin.contentWidth, c.web ? 120 : 100, copy.quote || '「简约不是少，而是刚刚好。」', {
        fontSize: scale.h2, color: colors.text, fontFamily: fonts.display, textAlign: 'center', lineHeight: 1.5, fontWeight: '500',
      }),
      text(uid('a'), margin.x, y0 + (c.web ? 128 : 108), margin.contentWidth, c.web ? 36 : 32, copy.author || '— 来源 / 署名', {
        fontSize: scale.caption, color: colors.textMuted, fontFamily: fonts.body, textAlign: 'center',
      }),
    ]
  },

  'steps-horizontal': (c, copy = {}) => {
    const { scale, margin, colors, fonts, H } = c
    const steps = copy.steps || ['步骤一', '步骤二', '步骤三']
    const y0 = Math.round(H * 0.32)
    const stepW = Math.floor(margin.contentWidth / 3)
    const els = [
      text(uid('h'), margin.x, y0 - (c.web ? 64 : 52), margin.contentWidth, c.web ? 40 : 32, copy.title || '流程', {
        fontSize: scale.h2, fontWeight: '600', color: colors.text, fontFamily: fonts.display, textAlign: 'center',
      }),
    ]
    steps.forEach((s, i) => {
      const x = margin.x + i * stepW + stepW / 2 - (c.web ? 28 : 22)
      els.push(shape(uid('c'), x, y0, c.web ? 56 : 44, c.web ? 56 : 44, { background: colors.accent, borderRadius: 999 }))
      els.push(text(uid('n'), margin.x + i * stepW, y0 + (c.web ? 64 : 52), stepW, c.web ? 28 : 24, String(i + 1), {
        fontSize: scale.body, color: colors.onAccent, fontFamily: fonts.body, textAlign: 'center', fontWeight: 'bold',
      }, 3))
      els.push(text(uid('l'), margin.x + i * stepW, y0 + (c.web ? 120 : 100), stepW, c.web ? 48 : 40, s, {
        fontSize: scale.caption, color: colors.textMuted, fontFamily: fonts.body, textAlign: 'center', lineHeight: 1.4,
      }))
    })
    return els
  },

  'closing-minimal': (c, copy = {}) => {
    const { scale, margin, colors, fonts, cx, H } = c
    const y0 = Math.round(H * 0.34)
    return [
      text(uid('t'), margin.x, y0, margin.contentWidth, c.web ? 64 : 52, copy.title || '谢谢', {
        fontSize: scale.display, fontWeight: 'bold', color: colors.text, fontFamily: fonts.display, textAlign: 'center',
      }),
      text(uid('c'), margin.x, y0 + (c.web ? 76 : 60), margin.contentWidth, c.web ? 48 : 40, copy.contact || 'contact@example.com', {
        fontSize: scale.body, color: colors.accent, fontFamily: fonts.body, textAlign: 'center',
      }),
      shape(uid('ln'), cx - (c.web ? 48 : 32), y0 + (c.web ? 140 : 112), c.web ? 96 : 64, 2, { background: colors.accent, borderRadius: 1 }),
    ]
  },

  'story-cover': (c, copy = {}) => {
    const { scale, margin, colors, fonts, H, W } = c
    const y0 = Math.round(H * 0.28)
    return [
      shape(uid('blob'), c.web ? W - 200 : W - 120, c.web ? 40 : 60, c.web ? 160 : 100, c.web ? 160 : 100, { background: colors.bgMuted, borderRadius: 999 }),
      shape(uid('blob2'), c.web ? 40 : 20, c.web ? H - 180 : H - 160, c.web ? 120 : 80, c.web ? 120 : 80, { background: colors.bgMuted, borderRadius: 999 }),
      text(uid('t'), margin.x, y0, margin.contentWidth, c.web ? 100 : 80, copy.title || '故事标题', {
        fontSize: scale.display, fontWeight: 'bold', color: colors.text, fontFamily: fonts.display, textAlign: 'center', lineHeight: 1.25,
      }),
      text(uid('s'), margin.x, y0 + (c.web ? 108 : 88), margin.contentWidth, c.web ? 48 : 40, copy.subtitle || '副标题', {
        fontSize: scale.body, color: colors.textMuted, fontFamily: fonts.body, textAlign: 'center',
      }),
    ]
  },

  'question-hook': (c, copy = {}) => {
    const { scale, margin, colors, fonts, H } = c
    const y0 = Math.round(H * 0.3)
    return [
      text(uid('q'), margin.x, y0, margin.contentWidth, c.web ? 140 : 120, copy.question || '他们期待什么样的志愿服务？', {
        fontSize: scale.h1, fontWeight: 'bold', color: colors.text, fontFamily: fonts.display, textAlign: 'center', lineHeight: 1.35,
      }),
      text(uid('h'), margin.x, y0 + (c.web ? 148 : 128), margin.contentWidth, c.web ? 36 : 32, copy.hint || '上滑继续 ↓', {
        fontSize: scale.caption, color: colors.accent, fontFamily: fonts.body, textAlign: 'center',
      }),
    ]
  },

  'icon-list-four': (c, copy = {}) => {
    const { scale, margin, colors, fonts, H } = c
    const items = copy.items || [
      { icon: 'school', text: '技能提升' },
      { icon: 'favorite', text: '有意义的体验' },
      { icon: 'emoji_objects', text: '有趣有挑战' },
      { icon: 'groups', text: '组织靠谱' },
    ]
    const y0 = Math.round(H * 0.18)
    const rowH = c.web ? 100 : 88
    const els = [
      text(uid('h'), margin.x, y0, margin.contentWidth, c.web ? 40 : 32, copy.title || '四个关键词', {
        fontSize: scale.h2, fontWeight: '600', color: colors.text, fontFamily: fonts.display,
      }),
    ]
    items.forEach((item, i) => {
      const y = y0 + (c.web ? 56 : 48) + i * rowH
      els.push(shape(uid('bg'), margin.x, y, margin.contentWidth, rowH - 12, { background: colors.bgMuted, borderRadius: 12 }))
      els.push(icon(uid('ic'), margin.x + 16, y + (c.web ? 22 : 18), c.web ? 48 : 40, item.icon, { color: colors.accent, background: 'transparent' }))
      els.push(text(uid('tx'), margin.x + (c.web ? 80 : 68), y + (c.web ? 24 : 20), margin.contentWidth - 80, c.web ? 48 : 40, item.text, {
        fontSize: scale.body, color: colors.text, fontFamily: fonts.body, lineHeight: 1.4,
      }))
    })
    return els
  },

  'big-stat-one': (c, copy = {}) => {
    const { scale, margin, colors, fonts, H } = c
    const y0 = Math.round(H * 0.28)
    return [
      text(uid('n'), margin.x, y0, margin.contentWidth, c.web ? 120 : 96, copy.stat || '73%', {
        fontSize: c.web ? 72 : 56, fontWeight: 'bold', color: colors.accent, fontFamily: fonts.display, textAlign: 'center',
      }),
      text(uid('d'), margin.x, y0 + (c.web ? 128 : 100), margin.contentWidth, c.web ? 80 : 72, copy.desc || '大学生希望志愿服务能真正带来成长', {
        fontSize: scale.body, color: colors.text, fontFamily: fonts.body, textAlign: 'center', lineHeight: 1.55,
      }),
    ]
  },

  'case-card': (c, copy = {}) => {
    const { scale, margin, colors, fonts, H } = c
    const y0 = Math.round(H * 0.22)
    const cardH = c.web ? 280 : 240
    return [
      shape(uid('card'), margin.x, y0, margin.contentWidth, cardH, { background: colors.bgMuted, borderRadius: 16 }),
      text(uid('t'), margin.x + 24, y0 + 24, margin.contentWidth - 48, c.web ? 48 : 40, copy.title || '案例：志愿组织活动', {
        fontSize: scale.h2, fontWeight: '600', color: colors.text, fontFamily: fonts.display,
      }),
      text(uid('b'), margin.x + 24, y0 + (c.web ? 88 : 72), margin.contentWidth - 48, cardH - (c.web ? 100 : 88), copy.body || '通过线上招募与培训，活动参与人数显著提升，组织影响力持续扩大。', {
        fontSize: scale.body, color: colors.textMuted, fontFamily: fonts.body, lineHeight: 1.6,
      }),
    ]
  },

  'values-four': (c, copy = {}) => {
    const { scale, margin, colors, fonts, H } = c
    const values = copy.values || ['奉献', '友爱', '互助', '进步']
    const y0 = Math.round(H * 0.36)
    const cellW = Math.floor(margin.contentWidth / 4)
    const els = [
      text(uid('h'), margin.x, y0 - (c.web ? 72 : 60), margin.contentWidth, c.web ? 40 : 32, copy.title || '志愿精神', {
        fontSize: scale.h2, fontWeight: '600', color: colors.text, fontFamily: fonts.display, textAlign: 'center',
      }),
    ]
    values.forEach((v, i) => {
      const x = margin.x + i * cellW
      els.push(shape(uid('c'), x + cellW / 2 - (c.web ? 28 : 22), y0, c.web ? 56 : 44, c.web ? 56 : 44, { background: colors.accent, borderRadius: 12 }))
      els.push(text(uid('v'), x, y0 + (c.web ? 68 : 56), cellW, c.web ? 36 : 32, v, {
        fontSize: scale.body, fontWeight: '600', color: colors.text, fontFamily: fonts.body, textAlign: 'center',
      }))
    })
    return els
  },
}

export function buildBlock(blockId, viewportId = 'mobile-375', themeId = 'zjy-minimal', copy = {}) {
  const builder = BLOCK_BUILDERS[blockId]
  if (!builder) return []
  const c = ctx(themeId, viewportId)
  return builder(c, copy)
}

export function getDefaultBlockBackground(themeId) {
  return getTheme(themeId).colors.bg
}

export function listLayoutBlocks(group = 'all') {
  if (group === 'business') return BUSINESS_LAYOUT_BLOCKS
  if (group === 'story') return STORY_LAYOUT_BLOCKS
  return [...BUSINESS_LAYOUT_BLOCKS, ...STORY_LAYOUT_BLOCKS]
}
