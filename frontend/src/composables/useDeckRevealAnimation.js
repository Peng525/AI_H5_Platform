import { computed, ref } from 'vue'

/** 每个组件 reveal 间隔（毫秒）— 控制绘制速度 */
const ELEMENT_REVEAL_MS = 800
/** 进入新页面前的暂停（给用户感知"开始绘制新页"） */
const SLIDE_INTRO_MS = 1000
/** 切到下一页前的短过渡 */
const SLIDE_TRANSITION_MS = 120

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
    // 新页面进入前暂停，让用户感知"开始绘制新页"
    schedule(SLIDE_INTRO_MS, () => {
      void revealElementBatch(slideIndex + 1)
    })
  }

  function preloadImageUrl(url) {
    const src = String(url || '').trim()
    if (!src || src.startsWith('data:')) return Promise.resolve()
    return new Promise((resolve) => {
      const img = new Image()
      img.onload = () => resolve()
      img.onerror = () => resolve()
      img.src = src
    })
  }

  async function revealElementBatch(slideIndex) {
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
    if (el?.type === 'image' && el.content) {
      await preloadImageUrl(el.content)
    }
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

    schedule(pageElementStepMs(els.length), () => {
      void revealElementBatch(slideIndex)
    })
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

  function startReveal({ slides, getElements, onComplete }) {
    slidesRef = slides || []
    getElementsForSlide = getElements || (() => [])
    onCompleteCb = onComplete
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
    schedule(SLIDE_TRANSITION_MS, () => {
      void revealElementBatch(0)
    })
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
