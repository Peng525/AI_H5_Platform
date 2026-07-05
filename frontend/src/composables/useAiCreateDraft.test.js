import { afterEach, describe, expect, it } from 'vitest'
import { clearDraft, loadDraft, normalizeDeckReviewDraftState, saveDraft } from './useAiCreateDraft.js'

describe('useAiCreateDraft', () => {
  afterEach(() => {
    clearDraft()
  })

  it('loads the latest saved topic for the review page', () => {
    saveDraft({ type: 'deck', topic: '第一次提示词' })
    saveDraft({ type: 'deck', topic: '第二次提示词', extraContent: '第二次提示词' })

    expect(loadDraft().topic).toBe('第二次提示词')
  })

  it('uses topic as review content when no edited content exists', () => {
    const state = normalizeDeckReviewDraftState({
      type: 'deck',
      pageCount: 5,
      topic: '新的首页提示词',
      extraContent: '',
    })

    expect(state.extraContent).toBe('新的首页提示词')
    expect(state.pageContents).toHaveLength(5)
  })
})
