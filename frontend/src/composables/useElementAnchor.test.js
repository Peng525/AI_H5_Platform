import { describe, expect, it, beforeEach, afterEach } from 'vitest'
import { floatingBarStyle } from './useElementAnchor.js'

describe('floatingBarStyle', () => {
  const anchor = { left: 100, top: 200, width: 80, height: 60, bottom: 260, right: 180 }

  beforeEach(() => {
    Object.defineProperty(window, 'innerWidth', { value: 1024, configurable: true })
    Object.defineProperty(window, 'innerHeight', { value: 768, configurable: true })
  })

  afterEach(() => {
    delete window.innerWidth
    delete window.innerHeight
  })

  it('places compact toolbar above anchor top edge', () => {
    const style = floatingBarStyle(anchor, 'above', 6, { compact: true, barHeight: 36 })
    expect(style.top).toBe('194px')
    expect(style.transform).toBe('translateX(-50%) translateY(-100%)')
    expect(style.left).toBe('140px')
    expect(style.width).toBe('max-content')
    expect(style.maxWidth).toBe('1008px')
  })

  it('places wide toolbar above with translateY only', () => {
    const style = floatingBarStyle(anchor, 'above', 10, { barHeight: 40 })
    expect(style.top).toBe('190px')
    expect(style.transform).toBe('translateY(-100%)')
    expect(style.width).toBe('560px')
  })

  it('flips to below when anchor is near viewport top', () => {
    const nearTop = { left: 50, top: 20, width: 100, height: 40, bottom: 60, right: 150 }
    const style = floatingBarStyle(nearTop, 'above', 6, { compact: true, barHeight: 36 })
    expect(style.top).toBe('66px')
    expect(style.transform).toBe('translateX(-50%)')
  })

  it('returns display none when anchorRect is missing', () => {
    expect(floatingBarStyle(null)).toEqual({ display: 'none' })
  })

  it('places below when placement is below', () => {
    const style = floatingBarStyle(anchor, 'below', 8, { compact: true, barHeight: 36 })
    expect(style.top).toBe('268px')
    expect(style.transform).toBe('translateX(-50%)')
  })
})
