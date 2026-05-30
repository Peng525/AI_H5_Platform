<template>
  <div>
    <div v-if="!hasData" class="py-8">
      <EmptyState icon="visibility_off" title="暂无访问记录" description="近 14 日无访问数据" />
    </div>
    <div v-else class="overflow-x-auto -mx-1 px-1">
      <div class="flex items-end gap-2 min-w-max h-40 pb-1">
        <div
          v-for="(d, i) in chart"
          :key="d.date || i"
          class="flex flex-col items-center gap-1.5 shrink-0"
          style="width: 2.25rem"
        >
          <span class="text-[10px] text-on-surface-variant tabular-nums leading-none min-h-[14px]">
            {{ d.count > 0 ? d.count : '' }}
          </span>
          <div class="w-full h-24 flex items-end justify-center">
            <div
              class="w-4 rounded-t bg-primary/85 hover:bg-primary transition-colors cursor-default"
              :style="{ height: barHeight(d.count) + '%', minHeight: d.count > 0 ? '4px' : '2px' }"
              :title="`${formatDate(d.date)} · ${d.count} 次`"
            />
          </div>
          <span
            v-if="showLabel(i)"
            class="text-[10px] text-on-surface-variant whitespace-nowrap leading-none"
          >
            {{ formatDate(d.date) }}
          </span>
          <span v-else class="text-[10px] leading-none invisible">·</span>
        </div>
      </div>
    </div>
    <p v-if="summary" class="text-xs text-on-surface-variant mt-4">{{ summary }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import EmptyState from '../EmptyState.vue'

const props = defineProps({
  chart: { type: Array, default: () => [] },
  summary: { type: String, default: '' },
})

const maxCount = computed(() => Math.max(1, ...props.chart.map((d) => d.count || 0)))

const hasData = computed(() => props.chart.some((d) => (d.count || 0) > 0))

function barHeight(count) {
  return Math.max(count > 0 ? 6 : 2, ((count || 0) / maxCount.value) * 100)
}

function formatDate(iso) {
  if (!iso) return ''
  const parts = iso.split('-')
  if (parts.length >= 3) return `${parts[1]}/${parts[2]}`
  return iso.slice(5)
}

function showLabel(index) {
  const len = props.chart.length
  if (len <= 7) return true
  return index % 2 === 0
}
</script>
