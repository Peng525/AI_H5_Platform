import { describe, expect, it } from 'vitest'
import { blankPage, duplicatePage, normalizePages } from './resumePages.js'
import { defaultStructured } from './resumeBind.js'

describe('resumePages', () => {
  it('normalizePages falls back to single page from structured', () => {
    const structured = { ...defaultStructured(), basics: { ...defaultStructured().basics, name: '张三' } }
    const pages = normalizePages({ template_id: 'classic-blue', styles: {} }, structured)
    expect(pages).toHaveLength(1)
    expect(pages[0].structured.basics.name).toBe('张三')
  })

  it('normalizePages reads visual_document.pages', () => {
    const pages = normalizePages(
      {
        pages: [
          { id: 'p1', structured: { basics: { name: 'A' } } },
          { id: 'p2', structured: { basics: { name: 'B' } } },
        ],
      },
      {},
    )
    expect(pages).toHaveLength(2)
    expect(pages[1].structured.basics.name).toBe('B')
  })

  it('duplicatePage deep clones structured', () => {
    const source = blankPage()
    source.structured.basics.name = '原页'
    const copy = duplicatePage(source)
    copy.structured.basics.name = '副本'
    expect(source.structured.basics.name).toBe('原页')
    expect(copy.id).not.toBe(source.id)
  })
})
