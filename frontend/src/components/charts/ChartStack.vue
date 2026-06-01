<template>
  <div
    class="chart-stack w-full h-full flex flex-col select-none"
    :class="interactive ? 'pointer-events-auto' : ''"
    @touchstart.passive="onTouchStart"
    @touchmove.passive="onTouchMove"
    @touchend="onTouchEnd"
  >
    <div class="chart-stack__viewport relative flex-1 min-h-0 mx-0 mb-0.5">
      <div
        v-for="item in renderItems"
        :key="item.card.id"
        class="chart-stack__card absolute bg-white rounded-lg overflow-hidden flex flex-col"
        :class="item.slot === 0 ? 'chart-stack__card--front' : 'chart-stack__card--back'"
        :style="item.style"
        @transitionend="(e) => onCardTransitionEnd(e, item.cardIndex)"
      >
        <p class="chart-stack__title shrink-0 text-[11px] font-semibold text-gray-800 px-3 py-2 leading-snug line-clamp-1 border-b border-gray-100">
          {{ item.card.title || '未命名图表' }}
        </p>
        <div class="flex-1 min-h-0 p-2">
          <SimpleChart
            :chart-type="item.card.chartType || 'bar'"
            :labels="item.card.labels || []"
            :values="item.card.values || []"
            :chart-color="chartColor"
          />
        </div>
      </div>
    </div>

    <div
      v-if="cards.length > 1"
      class="shrink-0 flex items-center justify-center gap-2 py-1"
      @pointerdown.stop
      @mousedown.stop
    >
      <button
        type="button"
        class="chart-stack__nav-btn"
        :disabled="activeIndex <= 0 || animating"
        aria-label="上一张"
        @click.stop="goPrev"
        @touchstart.stop
      >
        <span class="material-symbols-outlined text-[16px]">keyboard_arrow_up</span>
      </button>
      <span class="text-[10px] text-gray-500 tabular-nums min-w-[32px] text-center">
        {{ activeIndex + 1 }}/{{ cards.length }}
      </span>
      <button
        type="button"
        class="chart-stack__nav-btn"
        :disabled="activeIndex >= cards.length - 1 || animating"
        aria-label="下一张"
        @click.stop="goNext"
        @touchstart.stop
      >
        <span class="material-symbols-outlined text-[16px]">keyboard_arrow_down</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import SimpleChart from './SimpleChart.vue'

/** 槽位：0=前台(小) 1=后方1 2=后方2(大)，后大前小 */
const SLOTS = [
  { scale: 0.88, bottom: 0, insetX: 18, zIndex: 30, opacity: 1 },
  { scale: 0.96, bottom: 16, insetX: 10, zIndex: 20, opacity: 0.95 },
  { scale: 1.04, bottom: 32, insetX: 0, zIndex: 10, opacity: 0.9 },
]

const TRANSITION = 'transform 450ms cubic-bezier(0.4, 0, 0.2, 1), bottom 450ms cubic-bezier(0.4, 0, 0.2, 1), left 450ms cubic-bezier(0.4, 0, 0.2, 1), right 450ms cubic-bezier(0.4, 0, 0.2, 1), opacity 450ms cubic-bezier(0.4, 0, 0.2, 1)'

const props = defineProps({
  cards: { type: Array, default: () => [] },
  chartColor: { type: String, default: '#005daa' },
  interactive: { type: Boolean, default: true },
})

const activeIndex = ref(0)
const phase = ref('idle') // idle | toNext | toPrev
const slotOverrides = ref(null)
const animating = ref(false)

watch(
  () => props.cards.length,
  (len) => {
    if (activeIndex.value >= len) activeIndex.value = Math.max(0, len - 1)
  }
)

const cards = computed(() => (props.cards?.length ? props.cards : []))

function idleSlotForIndex(cardIndex) {
  const rel = cardIndex - activeIndex.value
  if (rel === 0) return 0
  if (rel === 1) return 1
  if (rel === 2) return 2
  // 刚离开顶层的卡片保留在后方；仅当仍有更后卡片时才用最远槽位，避免 2 张卡组 idle 时整体放大
  if (rel === -1) {
    const hasForwardBack = activeIndex.value + 1 < cards.value.length
    return hasForwardBack ? 2 : 1
  }
  if (rel === -2) return 1
  return null
}

function slotForCard(cardIndex) {
  if (slotOverrides.value && slotOverrides.value[cardIndex] !== undefined) {
    return slotOverrides.value[cardIndex]
  }
  if (phase.value === 'toPrev' && cardIndex === activeIndex.value - 1) {
    return 1
  }
  if (phase.value === 'toNext' && cardIndex === activeIndex.value + 3) {
    return 2
  }
  return idleSlotForIndex(cardIndex)
}

function visibleCardIndices() {
  const list = cards.value
  if (!list.length) return []

  if (phase.value === 'toPrev') {
    const start = Math.max(0, activeIndex.value - 1)
    const end = Math.min(list.length - 1, activeIndex.value + 2)
    const indices = []
    for (let i = start; i <= end; i += 1) indices.push(i)
    return indices
  }

  if (phase.value === 'toNext') {
    const start = activeIndex.value
    const end = Math.min(list.length - 1, activeIndex.value + 3)
    const indices = new Set()
    for (let i = start; i <= end; i += 1) indices.add(i)
    if (start > 0) indices.add(start - 1)
    return [...indices].sort((a, b) => a - b)
  }

  const end = Math.min(list.length - 1, activeIndex.value + 2)
  const indices = new Set()
  for (let i = activeIndex.value; i <= end; i += 1) indices.add(i)
  if (activeIndex.value > 0) indices.add(activeIndex.value - 1)
  if (activeIndex.value > 1) indices.add(activeIndex.value - 2)
  return [...indices].sort((a, b) => a - b)
}

function slotStyle(slot) {
  const s = SLOTS[slot]
  if (!s) return { display: 'none' }
  return {
    left: `${s.insetX}px`,
    right: `${s.insetX}px`,
    bottom: `${s.bottom}px`,
    transform: `scale(${s.scale})`,
    opacity: s.opacity,
    zIndex: s.zIndex,
    transition: phase.value !== 'idle' ? TRANSITION : 'none',
  }
}

const renderItems = computed(() => {
  const indices = visibleCardIndices()
  const items = indices.map((cardIndex) => {
    const slot = slotForCard(cardIndex)
    if (slot === null || slot === undefined) return null
    return {
      cardIndex,
      card: cards.value[cardIndex],
      slot,
      style: slotStyle(slot),
    }
  }).filter(Boolean)

  return items.sort((a, b) => b.slot - a.slot)
})

function buildNextOverrides() {
  const idx = activeIndex.value
  const n = cards.value.length
  const overrides = { [idx + 1]: 0 }

  if (idx + 2 < n) {
    overrides[idx] = 2
    overrides[idx + 2] = 1
    if (idx + 3 < n) {
      overrides[idx + 3] = 2
    }
  } else {
    overrides[idx] = 1
  }
  return overrides
}

function buildPrevOverrides() {
  const idx = activeIndex.value
  const overrides = {
    [idx - 1]: 0,
    [idx]: 1,
  }
  if (idx + 1 < cards.value.length) {
    overrides[idx + 1] = 2
  }
  return overrides
}

function goNext() {
  if (!props.interactive || animating.value || activeIndex.value >= cards.value.length - 1) return
  animating.value = true
  phase.value = 'toNext'
  slotOverrides.value = null
  nextTick(() => {
    requestAnimationFrame(() => {
      slotOverrides.value = buildNextOverrides()
    })
  })
}

function goPrev() {
  if (!props.interactive || animating.value || activeIndex.value <= 0) return
  animating.value = true
  phase.value = 'toPrev'
  slotOverrides.value = null
  nextTick(() => {
    requestAnimationFrame(() => {
      slotOverrides.value = buildPrevOverrides()
    })
  })
}

function finishTransition() {
  if (phase.value === 'toNext') {
    activeIndex.value += 1
  } else if (phase.value === 'toPrev') {
    activeIndex.value -= 1
  }
  phase.value = 'idle'
  slotOverrides.value = null
  animating.value = false
}

function onCardTransitionEnd(e, cardIndex) {
  if (phase.value === 'idle' || !animating.value) return
  if (e.propertyName !== 'transform') return
  const targetSlot = slotOverrides.value?.[cardIndex]
  if (targetSlot !== 0) return
  finishTransition()
}

function onTouchStart(e) {
  if (!props.interactive || animating.value) return
  touchStartY.value = e.touches[0]?.clientY ?? 0
  touchDeltaY.value = 0
}

function onTouchMove(e) {
  if (!props.interactive) return
  const y = e.touches[0]?.clientY ?? 0
  touchDeltaY.value = y - touchStartY.value
}

const touchStartY = ref(0)
const touchDeltaY = ref(0)

function onTouchEnd(e) {
  if (!props.interactive || animating.value) return
  e.stopPropagation()
  const threshold = 40
  if (touchDeltaY.value < -threshold) goNext()
  else if (touchDeltaY.value > threshold) goPrev()
  touchDeltaY.value = 0
}
</script>

<style scoped>
.chart-stack__viewport {
  overflow: visible;
  padding-top: 40px;
}

.chart-stack__card {
  top: 0;
  height: calc(100% - 4px);
  transform-origin: center bottom;
  pointer-events: none;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.chart-stack__card--front {
  pointer-events: auto;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.14);
}

.chart-stack__title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chart-stack__nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 9999px;
  border: 1px solid #c0c7d6;
  background: white;
  color: #005daa;
}

.chart-stack__nav-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
</style>
