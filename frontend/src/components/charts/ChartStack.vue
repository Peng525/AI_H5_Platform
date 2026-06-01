<template>
  <div
    class="chart-stack w-full h-full flex flex-col select-none"
    :class="interactive ? 'pointer-events-auto' : ''"
    @touchstart.passive="onTouchStart"
    @touchmove.passive="onTouchMove"
    @touchend="onTouchEnd"
  >
    <div class="relative flex-1 min-h-0 pt-2 px-1">
      <div
        v-for="item in visibleLayers"
        :key="item.card.id + '-' + item.layerIndex"
        class="chart-stack__card absolute left-2 right-2 bg-white rounded-lg shadow-md overflow-hidden flex flex-col"
        :class="item.animClass"
        :style="item.style"
      >
        <p class="shrink-0 text-[11px] font-semibold text-gray-800 px-3 py-2 leading-snug line-clamp-2 border-b border-gray-100">
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
      class="shrink-0 flex items-center justify-center gap-2 py-1.5"
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
import { computed, ref, watch } from 'vue'
import SimpleChart from './SimpleChart.vue'

const props = defineProps({
  cards: { type: Array, default: () => [] },
  chartColor: { type: String, default: '#005daa' },
  interactive: { type: Boolean, default: true },
})

const activeIndex = ref(0)
const animating = ref(false)
const animDirection = ref('')
const touchStartY = ref(0)
const touchDeltaY = ref(0)

watch(
  () => props.cards.length,
  (len) => {
    if (activeIndex.value >= len) activeIndex.value = Math.max(0, len - 1)
  }
)

const cards = computed(() => (props.cards?.length ? props.cards : []))

const visibleLayers = computed(() => {
  const list = cards.value
  if (!list.length) return []
  const layers = []
  for (let offset = 0; offset < Math.min(3, list.length - activeIndex.value); offset += 1) {
    const idx = activeIndex.value + offset
    if (idx >= list.length) break
    const card = list[idx]
    const isFront = offset === 0
    const scale = isFront ? 1 : offset === 1 ? 0.94 : 0.88
    const translateY = isFront ? 0 : offset === 1 ? -14 : -26
    const opacity = isFront ? 1 : offset === 1 ? 0.88 : 0.72
    const zIndex = 10 - offset
    let animClass = ''
    if (isFront && animating.value) {
      animClass = animDirection.value === 'next' ? 'chart-stack__card--exit-up' : 'chart-stack__card--exit-down'
    } else if (offset === 1 && animating.value && animDirection.value === 'next') {
      animClass = 'chart-stack__card--enter-front'
    } else if (isFront && animating.value && animDirection.value === 'prev') {
      animClass = 'chart-stack__card--enter-from-top'
    }
    layers.push({
      card,
      layerIndex: offset,
      animClass,
      style: {
        top: `${8 + translateY}px`,
        transform: `scale(${scale})`,
        opacity,
        zIndex,
        transition: animating.value ? 'transform 0.3s ease, opacity 0.3s ease, top 0.3s ease' : 'none',
      },
    })
  }
  return layers
})

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

function onTouchEnd(e) {
  if (!props.interactive || animating.value) return
  e.stopPropagation()
  const threshold = 40
  if (touchDeltaY.value < -threshold) goNext()
  else if (touchDeltaY.value > threshold) goPrev()
  touchDeltaY.value = 0
}

function goNext() {
  if (!props.interactive || animating.value || activeIndex.value >= cards.value.length - 1) return
  animDirection.value = 'next'
  animating.value = true
  setTimeout(() => {
    activeIndex.value += 1
    animating.value = false
    animDirection.value = ''
  }, 300)
}

function goPrev() {
  if (!props.interactive || animating.value || activeIndex.value <= 0) return
  animDirection.value = 'prev'
  animating.value = true
  setTimeout(() => {
    activeIndex.value -= 1
    animating.value = false
    animDirection.value = ''
  }, 300)
}
</script>

<style scoped>
.chart-stack__card {
  height: calc(100% - 12px);
  transform-origin: center top;
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

.chart-stack__card--exit-up {
  transform: scale(1) translateY(-120%) !important;
  opacity: 0 !important;
}

.chart-stack__card--exit-down {
  transform: scale(0.92) translateY(80%) !important;
  opacity: 0 !important;
}

.chart-stack__card--enter-front {
  animation: chartEnterFront 0.3s ease forwards;
}

.chart-stack__card--enter-from-top {
  animation: chartEnterFromTop 0.3s ease forwards;
}

@keyframes chartEnterFront {
  from {
    transform: scale(0.94) translateY(20px);
    opacity: 0.6;
  }
  to {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
}

@keyframes chartEnterFromTop {
  from {
    transform: scale(0.94) translateY(-40px);
    opacity: 0.5;
  }
  to {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
}
</style>
