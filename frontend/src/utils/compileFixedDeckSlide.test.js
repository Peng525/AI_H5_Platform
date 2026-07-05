import { describe, expect, it } from 'vitest'
import {
  FIXED_LAYOUT_IDS,
  compileFixedDeckSlide,
  resolveFixedSlide,
} from './compileFixedDeckSlide.js'
import { elementsOutOfBounds } from './compileStructuredSlide.js'

const VP_WIDE = 'web-wide-1024'
const VP_1280 = 'web-1280'
const THEME = 'zjy-minimal'

function sampleSlide(layoutId) {
  const base = { layout_id: layoutId, title: '示例标题', subtitle: '副标题与洞察说明' }
  switch (layoutId) {
    case FIXED_LAYOUT_IDS.TOC:
      return {
        ...base,
        title: '目录',
        points: [
          { title: '第一章 背景与目标' },
          { title: '第二章 市场洞察' },
          { title: '第三章 产品方案' },
          { title: '第四章 实施路径' },
          { title: '第五章 风险与对策' },
          { title: '第六章 总结展望' },
        ],
      }
    case FIXED_LAYOUT_IDS.KEY_POINTS:
      return {
        ...base,
        points: [
          { title: '论点一', body: '稳定生成与可编辑画布' },
          { title: '论点二', body: '自适应文本与动态行数' },
          { title: '论点三', body: '16:9 默认视口减少裁切' },
        ],
      }
    case FIXED_LAYOUT_IDS.ROADMAP_BOTTOM:
      return {
        ...base,
        insight: '核心价值循环',
        steps: ['准入', '沉淀', '续约'],
        image_url: 'https://example.com/roadmap.png',
      }
    case FIXED_LAYOUT_IDS.SCENE_LEFT:
      return { ...base, insight: '情景描述', image_url: 'https://example.com/scene.png' }
    case FIXED_LAYOUT_IDS.CHART_LEFT:
      return {
        ...base,
        insight: '数据洞察',
        chart: { type: 'bar', labels: ['A', 'B', 'C'], values: [30, 55, 82] },
      }
    case FIXED_LAYOUT_IDS.CHAPTER:
      return { ...base, kicker: 'PART 01' }
    case FIXED_LAYOUT_IDS.CLOSING:
      return { ...base, contact: 'contact@example.com' }
    default:
      return base
  }
}

function assertInBounds(elements, viewportId) {
  expect(elementsOutOfBounds(elements, viewportId)).toBe(false)
  expect(elements.length).toBeGreaterThan(0)
}

function byType(elements, type) {
  return elements.filter((el) => el.type === type)
}

describe('compileFixedDeckSlide', () => {
  it('renders the required title page as editable canvas text', () => {
    const elements = compileFixedDeckSlide({
      layout_id: FIXED_LAYOUT_IDS.COVER,
      title: 'Academic Curator 数字学习支持平台',
      subtitle: '将分散错误转化为结构化支持',
    }, VP_WIDE, THEME)

    expect(byType(elements, 'text').some((el) => el.content.includes('Academic Curator'))).toBe(true)
    expect(elementsOutOfBounds(elements, VP_WIDE)).toBe(false)
  })

  it('places roadmap visuals in the lower middle of the slide', () => {
    const elements = compileFixedDeckSlide({
      layout_id: FIXED_LAYOUT_IDS.ROADMAP_BOTTOM,
      title: '标准化流程驱动可持续商业生态',
      insight: '核心价值创造循环',
      steps: ['B 端准入', '数据沉淀', '续约回报'],
      image_url: 'https://example.com/roadmap.png',
    }, VP_WIDE, THEME)
    const image = byType(elements, 'image')[0]

    expect(image).toBeTruthy()
    expect(image.y).toBeGreaterThan(190)
    expect(image.x).toBeGreaterThan(180)
    expect(elementsOutOfBounds(elements, VP_WIDE)).toBe(false)
  })

  it('places scene images and charts on the left with narrative on the right', () => {
    const scene = compileFixedDeckSlide({
      layout_id: FIXED_LAYOUT_IDS.SCENE_LEFT,
      title: '情景页',
      insight: '管理者查看数据大屏',
      image_url: 'https://example.com/scene.png',
    }, VP_WIDE, THEME)
    const chart = compileFixedDeckSlide({
      layout_id: FIXED_LAYOUT_IDS.CHART_LEFT,
      title: '数字页',
      insight: '订阅转化提升',
      chart: { type: 'bar', labels: ['试用', '付费', '续约'], values: [30, 55, 82] },
    }, VP_WIDE, THEME)

    expect(byType(scene, 'image')[0].x).toBeLessThan(120)
    expect(byType(chart, 'chart')[0].x).toBeLessThan(120)
    expect(elementsOutOfBounds(scene, VP_WIDE)).toBe(false)
    expect(elementsOutOfBounds(chart, VP_WIDE)).toBe(false)
  })

  it('does not emit image elements for scene pages before an image url is available', () => {
    const scene = compileFixedDeckSlide({
      layout_id: FIXED_LAYOUT_IDS.SCENE_LEFT,
      title: '情景页',
      insight: '管理者查看数据大屏',
      image_prompt: '一位管理者在会议室查看教育数据大屏',
    }, VP_WIDE, THEME)

    expect(byType(scene, 'image')).toHaveLength(0)
    expect(byType(scene, 'shape').length).toBeGreaterThan(0)
    expect(elementsOutOfBounds(scene, VP_WIDE)).toBe(false)
  })

  it('resolves legacy slide objects that use layout_id instead of template', () => {
    const fixed = resolveFixedSlide({
      structured: {
        layout_id: 'key_points',
        title: '关键论点',
        points: ['稳定生成', '可编辑画布'],
      },
    })

    expect(fixed.layout_id).toBe(FIXED_LAYOUT_IDS.KEY_POINTS)
  })

  it('keeps toc with six items within web-wide-1024 bounds', () => {
    const elements = compileFixedDeckSlide(sampleSlide(FIXED_LAYOUT_IDS.TOC), VP_WIDE, THEME)
    assertInBounds(elements, VP_WIDE)
  })

  it('keeps toc with six items within web-1280 bounds', () => {
    const elements = compileFixedDeckSlide(sampleSlide(FIXED_LAYOUT_IDS.TOC), VP_1280, THEME)
    assertInBounds(elements, VP_1280)
  })

  it.each(Object.values(FIXED_LAYOUT_IDS))('layout %s stays in bounds on web-1280', (layoutId) => {
    const elements = compileFixedDeckSlide(sampleSlide(layoutId), VP_1280, THEME)
    assertInBounds(elements, VP_1280)
  })

  it.each(Object.values(FIXED_LAYOUT_IDS))('layout %s stays in bounds on web-wide-1024', (layoutId) => {
    const elements = compileFixedDeckSlide(sampleSlide(layoutId), VP_WIDE, THEME)
    assertInBounds(elements, VP_WIDE)
  })
})
