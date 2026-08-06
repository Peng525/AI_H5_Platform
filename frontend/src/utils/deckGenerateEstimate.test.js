import { describe, expect, it } from 'vitest'
import {
  computeDynamicRemainingSeconds,
  computeStageAwareRemainingSeconds,
  estimatePremiumDeckRange,
  estimatePremiumDeckSeconds,
  estimateQuickDeckSeconds,
  formatPremiumDeckRangeLabel,
  shouldShowPremiumRemaining,
  smoothEtaSeconds,
} from './deckGenerateEstimate.js'

describe('deckGenerateEstimate', () => {
  it('estimatePremiumDeckSeconds scales by page count', () => {
    expect(estimatePremiumDeckSeconds(5)).toBe(510)
    expect(estimatePremiumDeckSeconds(1)).toBe(180)
  })

  it('estimatePremiumDeckRange gives 5-page band 6–10 min', () => {
    const range = estimatePremiumDeckRange(5)
    expect(range.typicalSeconds).toBe(510)
    expect(range.minSeconds).toBe(360)
    expect(range.maxSeconds).toBe(600)
    expect(formatPremiumDeckRangeLabel(5)).toBe('6–10 分钟')
  })

  it('estimateQuickDeckSeconds stays fast-path formula', () => {
    expect(estimateQuickDeckSeconds(5)).toBe(28)
  })

  it('computeDynamicRemainingSeconds returns null before threshold', () => {
    expect(computeDynamicRemainingSeconds(10, 20)).toBeNull()
    expect(computeDynamicRemainingSeconds(20, 5)).toBeNull()
  })

  it('computeDynamicRemainingSeconds extrapolates remaining time', () => {
    expect(computeDynamicRemainingSeconds(100, 25)).toBe(300)
  })

  it('shouldShowPremiumRemaining only after generating starts', () => {
    expect(shouldShowPremiumRemaining('strategist', 0)).toBe(false)
    expect(shouldShowPremiumRemaining('generating', 1)).toBe(true)
    expect(shouldShowPremiumRemaining('importing', 5)).toBe(true)
  })

  it('computeStageAwareRemainingSeconds avoids early linear collapse', () => {
    const atStrategist = computeStageAwareRemainingSeconds({
      elapsedSeconds: 27,
      stage: 'strategist',
      currentPage: 0,
      totalPages: 5,
      typicalSeconds: 510,
    })
    const atPage1 = computeStageAwareRemainingSeconds({
      elapsedSeconds: 27,
      stage: 'generating',
      currentPage: 1,
      totalPages: 5,
      typicalSeconds: 510,
    })
    expect(atPage1).toBeGreaterThan(300)
    expect(atStrategist).toBeGreaterThan(atPage1)
  })

  it('smoothEtaSeconds limits per-tick change', () => {
    expect(smoothEtaSeconds(400, 300, 25)).toBe(375)
    expect(smoothEtaSeconds(null, 120)).toBe(120)
  })
})
