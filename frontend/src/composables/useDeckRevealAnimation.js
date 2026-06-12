import { computed, ref } from 'vue'

/** 每个组件 reveal 间隔（毫秒） */
const ELEMENT_REVEAL_MS = 500
/** 切到下一页前的短过渡 */
const SLIDE_TRANSITION_MS = 80

function pageElementStepMs(_elementCount) {
  return ELEMENT_REVEAL_MS
}

/**
 * 全量生成完成后的 staged reveal：逐页 → 逐组件
 * 每个组件间隔约 ELEMENT_REVEAL_MS
 * phase: idle | revealing | done
 */
export function useDeckRevealAnimation() {
  const phase = ref('idle')
  const visibleSlideCount = ref(-1)
  const visibleElementIdsBySlide = ref({})
  const currentSlideIndex = ref(-1)
  const currentElementIndex = ref(-1)
  const brushTarget = ref(null)

  let timer = null
  let slidesRef = []
  let getElementsForSlide = () => []
  let onCompleteCb = null
  let overviewScrollFn = null

  const isRevealing = computed(() => phase.value === 'revealing')
  const isDone = computed(() => phase.value === 'done')

  function clearTimer() {
    if (timer) {
      clearTimeout(timer)
      timer = null
    }
  }

  function sortedElements(slide) {
    const els = getElementsForSlide(slide) || []
    return [...els].sort((a, b) => (a.zIndex || 0) - (b.zIndex || 0))
  }

  function schedule(ms, fn) {
    clearTimer()
    timer = setTimeout(fn, ms)
  }

  function goToNextSlide(slideIndex) {
    if (slideIndex + 1 >= slidesRef.length) {
      finishReveal()
      return
    }
    visibleSlideCount.value = slideIndex + 2
    currentSlideIndex.value = slideIndex + 1
    currentElementIndex.value = 0
    overviewScrollFn?.(slidesRef[slideIndex + 1]?.id)
    schedule(SLIDE_TRANSITION_MS, () => revealElementBatch(slideIndex + 1))
  }

  function revealElementBatch(slideIndex) {
    const slide = slidesRef[slideIndex]
    if (!slide) {
      finishReveal()
      return
    }
    const els = sortedElements(slide)
    const slideId = slide.id
    const map = { ...visibleElementIdsBySlide.value }
    const revealed = [...(map[slideId] || [])]

    if (!els.length) {
      goToNextSlide(slideIndex)
      return
    }

    if (currentElementIndex.value >= els.length) {
      goToNextSlide(slideIndex)
      return
    }

    const el = els[currentElementIndex.value]
    if (el?.id) {
      revealed.push(el.id)
      map[slideId] = revealed
      visibleElementIdsBySlide.value = map
      brushTarget.value = { slideId, elementId: el.id, at: Date.now() }
    }
    currentElementIndex.value += 1

    if (currentElementIndex.value >= els.length) {
      goToNextSlide(slideIndex)
      return
    }

    schedule(pageElementStepMs(els.length), () => revealElementBatch(slideIndex))
  }

  function finishReveal() {
    clearTimer()
    visibleSlideCount.value = slidesRef.length
    const map = {}
    for (const slide of slidesRef) {
      map[slide.id] = sortedElements(slide).map((e) => e.id).filter(Boolean)
    }
    visibleElementIdsBySlide.value = map
    phase.value = 'done'
    brushTarget.value = null
    onCompleteCb?.()
  }

  function startReveal({ slides, getElements, onComplete, scrollToSlide }) {
    slidesRef = slides || []
    getElementsForSlide = getElements || (() => [])
    onCompleteCb = onComplete
    overviewScrollFn = scrollToSlide
    if (!slidesRef.length) {
      phase.value = 'done'
      onComplete?.()
      return
    }
    phase.value = 'revealing'
    visibleSlideCount.value = 1
    visibleElementIdsBySlide.value = {}
    currentSlideIndex.value = 0
    currentElementIndex.value = 0
    brushTarget.value = null
    overviewScrollFn?.(slidesRef[0]?.id)
    schedule(SLIDE_TRANSITION_MS, () => revealElementBatch(0))
  }

  function skipReveal() {
    if (phase.value !== 'revealing') return
    finishReveal()
  }

  function resetReveal() {
    clearTimer()
    phase.value = 'idle'
    visibleSlideCount.value = -1
    visibleElementIdsBySlide.value = {}
    currentSlideIndex.value = -1
    currentElementIndex.value = -1
    brushTarget.value = null
    slidesRef = []
    getElementsForSlide = () => []
    onCompleteCb = null
    overviewScrollFn = null
  }

  function isSlideVisible(index) {
    if (phase.value === 'done') return true
    if (phase.value !== 'revealing') return false
    return index < visibleSlideCount.value
  }

  function visibleElementsForSlide(slide, allElements) {
    if (phase.value === 'done') return allElements
    if (phase.value !== 'revealing') return []
    const ids = new Set(visibleElementIdsBySlide.value[slide.id] || [])
    return allElements.filter((el) => ids.has(el.id))
  }

  return {
    phase,
    isRevealing,
    isDone,
    visibleSlideCount,
    visibleElementIdsBySlide,
    currentSlideIndex,
    brushTarget,
    startReveal,
    skipReveal,
    resetReveal,
    isSlideVisible,
    visibleElementsForSlide,
  }
}
