import { describe, expect, it } from 'vitest'
import {
  STRUCTURED_COMPILE_VERSION,
  compileStructuredSlide,
  elementsLookMobileOnWideCanvas,
  ensureSlideCompiled,
  shouldCompileSlide,
} from './compileStructuredSlide.js'
import { getLayoutCanvasSize } from '../constants/editorPresets.js'

const VP_WIDE = 'web-wide-1024'
const THEME = 'zjy-minimal'
const THEME_DARK = 'tech-blue'

function maxRight(elements) {
  if (!elements?.length) return 0
  return Math.max(...elements.map((el) => (el.x ?? 0) + (el.width ?? 0)))
}

function cardShapes(elements) {
  return (elements || []).filter((el) => el.type === 'shape' && el.style?.borderRadius != null)
}

function textElementsOverlap(elements) {
  const texts = (elements || []).filter((el) => el.type === 'text')
  for (let i = 0; i < texts.length; i++) {
    for (let j = i + 1; j < texts.length; j++) {
      const a = texts[i]
      const b = texts[j]
      const overlapY = a.y + a.height > b.y + 2 && b.y + b.height > a.y + 2
      const overlapX = a.x + a.width > b.x + 2 && b.x + b.width > a.x + 2
      if (overlapY && overlapX) return true
    }
  }
  return false
}

function bodyInsideCard(elements) {
  const cards = cardShapes(elements)
  const bodies = (elements || []).filter(
    (el) => el.type === 'text' && String(el.content || '').length > 20
  )
  return bodies.every((body) =>
    cards.some(
      (card) =>
        body.x >= card.x &&
        body.y >= card.y &&
        body.x + body.width <= card.x + card.width + 2 &&
        body.y + body.height <= card.y + card.height + 2
    )
  )
}

function cardBackgrounds(elements) {
  return cardShapes(elements).map((el) => el.style?.background).filter(Boolean)
}

const fourModules = [
  { icon: 'target', title: '核心痛点', body: '将错误数据转化为可行洞察。' },
  { icon: 'groups', title: '用户群体', body: '学生、教师与管理者三重受益。' },
  { icon: 'lightbulb', title: '战略前提', body: '数据驱动教学改进。' },
  { icon: 'analytics', title: '关键功能', body: '集成分析与反馈回路。' },
]

describe('compileStructuredSlide layout', () => {
  it('grid_2x2 wide uses true 2x2 grid spanning canvas width', () => {
    const elements = compileStructuredSlide(
      { template: 'grid_2x2', title: '平台定位', headline: 'Academic Curator', modules: fourModules },
      VP_WIDE,
      THEME
    )
    const { width: W } = getLayoutCanvasSize(VP_WIDE)
    expect(cardShapes(elements).length).toBe(4)
    expect(maxRight(elements)).toBeGreaterThan(W * 0.7)
    const xs = cardShapes(elements).map((c) => c.x)
    expect(new Set(xs).size).toBeGreaterThanOrEqual(2)
  })

  it('normalizes generated lucide-style icon names to Material Symbols', () => {
    const elements = compileStructuredSlide(
      {
        template: 'grid_2x2',
        title: '图标归一化',
        modules: [
          { icon: 'zap', title: '平台定位', body: '说明' },
          { icon: 'users', title: '利益相关方', body: '说明' },
          { icon: 'trending-up', title: '战略前提', body: '说明' },
          { icon: 'bar-chart-2', title: '价值回报', body: '说明' },
        ],
      },
      VP_WIDE,
      THEME
    )
    const iconNames = elements.filter((el) => el.type === 'icon').map((el) => el.content)
    expect(iconNames).toEqual(['bolt', 'groups', 'trending_up', 'bar_chart'])
    expect(iconNames).not.toContain('zap')
    expect(iconNames).not.toContain('bar-chart-2')
  })

  it('grid_2x2 with padded modules fills width', () => {
    const elements = compileStructuredSlide(
      {
        template: 'grid_2x2',
        title: '双模块页',
        modules: fourModules.slice(0, 2),
      },
      VP_WIDE,
      THEME
    )
    const { width: W } = getLayoutCanvasSize(VP_WIDE)
    expect(cardShapes(elements).length).toBe(4)
    expect(maxRight(elements)).toBeGreaterThan(W * 0.7)
  })

  it('headline and long title do not overlap', () => {
    const elements = compileStructuredSlide(
      {
        template: 'grid_2x2',
        headline: '将错误数据转化为可行行动的结构化学术支持',
        title: 'Academic Curator Platform',
        modules: fourModules,
      },
      VP_WIDE,
      THEME
    )
    expect(textElementsOverlap(elements)).toBe(false)
  })

  it('cards_row long body stays inside card bounds', () => {
    const longBody =
      '集中式机构采购由B端决策者与现金流驱动，学生高频扫码刷题提升参与度，沉淀高保真交互数据并赋能AI分析，最终形成效能提升与价值回报闭环。'
    const elements = compileStructuredSlide(
      {
        template: 'cards_row',
        title: '从采购到续约的增强回路',
        modules: [
          { icon: 'shopping_cart', title: '集中式机构采购', body: longBody },
          { icon: 'bolt', title: '高频终端驱动', body: longBody },
          { icon: 'database', title: '数据沉淀与AI赋能', body: longBody },
          { icon: 'trending_up', title: '效能提升与价值回报', body: longBody },
        ],
      },
      VP_WIDE,
      THEME
    )
    expect(bodyInsideCard(elements)).toBe(true)
  })

  it('grid and cards_row use consistent card surface on dark theme', () => {
    const grid = compileStructuredSlide(
      { template: 'grid_2x2', title: '四宫格', modules: fourModules },
      VP_WIDE,
      THEME_DARK
    )
    const row = compileStructuredSlide(
      {
        template: 'cards_row',
        title: '横排',
        modules: fourModules.slice(0, 3),
      },
      VP_WIDE,
      THEME_DARK
    )
    const gridBg = cardBackgrounds(grid)[0]
    const rowBg = cardBackgrounds(row)[0]
    expect(gridBg).toBe(rowBg)
    expect(gridBg).toBe('#152238')
  })

  it('recompiles when viewport switches from mobile to wide', () => {
    const structured = { template: 'grid_2x2', title: '测试', modules: fourModules }
    const slide = {
      structured,
      canvas_elements: compileStructuredSlide(structured, 'mobile-375', THEME),
      _compiledViewportId: 'mobile-375',
      _compileVersion: STRUCTURED_COMPILE_VERSION,
    }
    expect(elementsLookMobileOnWideCanvas(slide.canvas_elements, VP_WIDE)).toBe(true)
    expect(shouldCompileSlide(slide, VP_WIDE)).toBe(true)
    ensureSlideCompiled(slide, VP_WIDE, THEME)
    expect(elementsLookMobileOnWideCanvas(slide.canvas_elements, VP_WIDE)).toBe(false)
    expect(slide._compileVersion).toBe(STRUCTURED_COMPILE_VERSION)
  })

  it('forces recompile when compile version is stale', () => {
    const structured = { template: 'section', title: '章节', subtitle: '说明' }
    const slide = {
      structured,
      canvas_elements: [{ id: 'old', type: 'text', x: 0, y: 0, width: 10, height: 10, content: 'x' }],
      _compiledViewportId: VP_WIDE,
      _compileVersion: STRUCTURED_COMPILE_VERSION - 1,
    }
    expect(shouldCompileSlide(slide, VP_WIDE)).toBe(true)
  })

  it('section long body fits within viewport height', () => {
    const longBody =
      '平台采用 B2B2C 数据飞轮模型，以优化教学效能与提升学术竞争力为中心，通过订阅制创造经常性收入，实现长期战略价值与可持续增长。'
    const elements = compileStructuredSlide(
      {
        template: 'section',
        headline: '超越 SaaS，构建教育机构解决方案',
        title: '商业模式与生态循环',
        subtitle: longBody,
      },
      VP_WIDE,
      THEME
    )
    const { height: H } = getLayoutCanvasSize(VP_WIDE)
    const maxBottom = Math.max(...elements.map((el) => (el.y ?? 0) + (el.height ?? 0)))
    expect(maxBottom).toBeLessThanOrEqual(H + 2)
  })

  it('cover uses theme-first layout without side panel by default', () => {
    const elements = compileStructuredSlide(
      {
        template: 'cover',
        title: 'Academic Curator 数字学习支持平台',
        subtitle: '为香港中学构建的 B2B2C 智能错题管理系统',
        image_intent: 'none',
      },
      VP_WIDE,
      THEME
    )
    expect(elements.some((el) => el.type === 'image')).toBe(false)
    expect(elements.some((el) => el.type === 'shape' && (el.width ?? 0) > 400)).toBe(false)
    const { width: W, height: H } = getLayoutCanvasSize(VP_WIDE)
    expect(elements.every((el) => (el.x ?? 0) + (el.width ?? 0) <= W + 2)).toBe(true)
    expect(elements.every((el) => (el.y ?? 0) + (el.height ?? 0) <= H + 2)).toBe(true)
  })

  it('cover renders full-bleed image only with cover_bg intent and url', () => {
    const elements = compileStructuredSlide(
      {
        template: 'cover',
        title: 'Academic Curator',
        subtitle: '平台介绍',
        image_intent: 'cover_bg',
        image_url: 'https://example.com/cover.jpg',
      },
      VP_WIDE,
      THEME
    )
    const imgs = elements.filter((el) => el.type === 'image')
    expect(imgs.length).toBe(1)
    expect(imgs[0].width).toBeGreaterThan(900)
    expect(imgs[0].content).toContain('example.com')
  })

  it('split_lr without scene url uses full-width text without placeholder image', () => {
    const elements = compileStructuredSlide(
      {
        template: 'split_lr',
        headline: '摒弃功能分级',
        title: '盈利策略',
        modules: [
          { role: 'text', title: '双轨定价策略', body: '基于资源用量的定价模型。' },
          { role: 'text', title: '补充说明', body: '右侧纯文字。' },
        ],
      },
      VP_WIDE,
      THEME
    )
    expect(elements.some((el) => el.type === 'image')).toBe(false)
    expect(elements.some((el) => el.type === 'chartPlaceholder')).toBe(false)
  })

  it('split_lr renders image when scene intent and image_url are set', () => {
    const elements = compileStructuredSlide(
      {
        template: 'split_lr',
        title: '盈利策略',
        modules: [
          { role: 'text', title: '左栏', body: '说明' },
          { role: 'scene_image', image_intent: 'scene', image_url: 'https://example.com/scene.jpg' },
        ],
      },
      VP_WIDE,
      THEME
    )
    expect(elements.some((el) => el.type === 'image' && el.content?.includes('example.com'))).toBe(true)
  })

  it('steps renders roadmap image at bottom when image_intent is roadmap', () => {
    const elements = compileStructuredSlide(
      {
        template: 'steps',
        title: '实施路径',
        image_intent: 'roadmap',
        image_url: 'https://example.com/roadmap.jpg',
        modules: [
          { title: '步骤一' },
          { title: '步骤二' },
          { title: '步骤三' },
        ],
      },
      VP_WIDE,
      THEME
    )
    const img = elements.find((el) => el.type === 'image')
    expect(img?.content).toContain('example.com')
    const { height: H } = getLayoutCanvasSize(VP_WIDE)
    expect((img?.y ?? 0) + (img?.height ?? 0)).toBeLessThanOrEqual(H + 2)
  })
})
