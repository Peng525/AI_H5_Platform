<template>
  <div class="simple-chart w-full h-full flex flex-col min-h-0">
    <div v-if="chartType === 'bar'" class="flex-1 flex items-end justify-around gap-1 min-h-0 px-2 pb-1">
      <div
        v-for="(v, i) in normalizedValues"
        :key="i"
        class="flex flex-col items-center gap-0.5 flex-1 max-w-[22%] min-w-0"
      >
        <div
          class="w-full rounded-t-sm transition-all"
          :style="{
            height: barHeight(v) + '%',
            background: segmentColor(i),
            minHeight: '4px',
          }"
        />
        <span v-if="showLabels && normalizedLabels[i]" class="text-[9px] text-gray-500 truncate w-full text-center leading-tight">
          {{ normalizedLabels[i] }}
        </span>
      </div>
    </div>
    <div v-else class="flex-1 flex items-center justify-center min-h-0 p-2">
      <svg viewBox="0 0 100 100" class="w-full h-full max-h-full" preserveAspectRatio="xMidYMid meet">
        <g transform="translate(50,50)">
          <path
            v-for="(seg, i) in pieSegments"
            :key="i"
            :d="seg.path"
            :fill="segmentColor(i)"
            stroke="#fff"
            stroke-width="0.5"
          />
        </g>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const PIE_COLORS = ['#005daa', '#3d8fd1', '#7eb8e8', '#f4a261', '#e76f51', '#2a9d8f']

const props = defineProps({
  chartType: { type: String, default: 'bar' },
  labels: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
  chartColor: { type: String, default: '#005daa' },
  showLabels: { type: Boolean, default: true },
})

const normalizedValues = computed(() => {
  const vals = props.values?.length ? props.values.map(Number) : [35, 65, 45, 80, 55]
  return vals.map((v) => (Number.isFinite(v) ? v : 0))
})

const normalizedLabels = computed(() => {
  if (props.labels?.length) return props.labels
  return normalizedValues.value.map((_, i) => String.fromCharCode(65 + i))
})

function segmentColor(i) {
  if (props.chartType === 'bar') return props.chartColor
  return PIE_COLORS[i % PIE_COLORS.length]
}

function barHeight(v) {
  const max = Math.max(...normalizedValues.value, 1)
  return Math.max(8, (v / max) * 100)
}

const pieSegments = computed(() => {
  const total = normalizedValues.value.reduce((s, v) => s + v, 0) || 1
  let angle = -Math.PI / 2
  const r = 42
  return normalizedValues.value.map((v) => {
    const slice = (v / total) * Math.PI * 2
    const x1 = r * Math.cos(angle)
    const y1 = r * Math.sin(angle)
    angle += slice
    const x2 = r * Math.cos(angle)
    const y2 = r * Math.sin(angle)
    const large = slice > Math.PI ? 1 : 0
    const path = `M 0 0 L ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2} Z`
    return { path }
  })
})
</script>
