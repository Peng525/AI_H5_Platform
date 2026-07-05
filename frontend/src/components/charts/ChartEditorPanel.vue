<template>
  <div class="flex flex-col gap-4 p-3 min-h-0">
    <section v-if="isStackMode" class="space-y-2">
      <div class="flex items-center justify-between gap-2">
        <p class="text-[10px] font-semibold text-on-surface-variant">卡片</p>
        <button
          type="button"
          class="text-[10px] text-primary font-medium px-2 py-0.5 rounded hover:bg-primary/5"
          @click="addCard"
        >
          + 添加
        </button>
      </div>
      <div class="flex flex-wrap gap-1.5">
        <button
          v-for="(card, i) in draftCards"
          :key="card.id"
          type="button"
          class="px-2 py-1 text-[10px] rounded-lg border transition truncate max-w-[8rem]"
          :class="activeCardId === card.id ? 'border-primary ring-1 ring-primary bg-primary/5' : 'border-outline-variant hover:border-primary/40'"
          @click="activeCardId = card.id"
        >
          {{ card.title || `卡片 ${i + 1}` }}
        </button>
      </div>
    </section>

    <section class="space-y-2">
      <p class="text-[10px] font-semibold text-on-surface-variant">图表类型</p>
      <div class="grid grid-cols-2 gap-2">
        <button
          v-for="opt in chartTypeOptions"
          :key="opt.id"
          type="button"
          class="flex flex-col items-center gap-1 px-2 py-2.5 rounded-lg border text-[11px] font-medium transition"
          :class="activeCard?.chartType === opt.id ? 'border-primary bg-primary/5 text-primary' : 'border-outline-variant hover:bg-surface-container-low'"
          :disabled="!activeCard"
          @click="setChartType(opt.id)"
        >
          <span class="material-symbols-outlined text-[20px]">{{ opt.icon }}</span>
          {{ opt.label }}
        </button>
      </div>
    </section>

    <template v-if="activeCard">
      <section class="space-y-2">
        <label class="block">
          <span class="text-xs font-semibold text-on-surface">标题</span>
          <input
            v-model="activeCard.title"
            type="text"
            class="mt-1 w-full text-sm border border-outline-variant rounded-lg px-2 py-1.5"
            placeholder="图表标题"
          />
        </label>
      </section>

      <section class="space-y-2">
        <div class="flex items-center justify-between gap-2">
          <p class="text-xs font-semibold text-on-surface">数据</p>
          <button
            type="button"
            class="text-[10px] text-primary font-medium px-2 py-0.5 rounded hover:bg-primary/5"
            @click="addDataRow"
          >
            + 添加行
          </button>
        </div>
        <div class="space-y-1.5 max-h-[12rem] overflow-y-auto">
          <div
            v-for="(row, i) in dataRows"
            :key="i"
            class="flex items-center gap-1.5"
          >
            <input
              v-model="row.label"
              type="text"
              class="flex-1 min-w-0 text-xs border border-outline-variant rounded-lg px-2 py-1"
              placeholder="X 轴标签"
              @input="syncRowsToCard"
            />
            <input
              v-model.number="row.value"
              type="number"
              class="w-16 shrink-0 text-xs border border-outline-variant rounded-lg px-2 py-1"
              placeholder="Y"
              @input="syncRowsToCard"
            />
            <button
              type="button"
              class="p-1 rounded hover:bg-red-50 text-red-500 shrink-0"
              :disabled="dataRows.length <= 1"
              title="删除行"
              @click="removeDataRow(i)"
            >
              <span class="material-symbols-outlined text-[16px]">close</span>
            </button>
          </div>
        </div>
      </section>

      <section v-if="isStackMode" class="pt-1">
        <button
          type="button"
          class="w-full text-xs text-red-600 border border-red-200 rounded-lg py-1.5 hover:bg-red-50"
          :disabled="draftCards.length <= 1"
          @click="removeActiveCard"
        >
          删除当前卡片
        </button>
      </section>

      <section class="space-y-2 pt-1 border-t border-outline-variant/60">
        <p class="text-[10px] font-semibold text-on-surface-variant">预览</p>
        <div class="bg-white rounded-xl border border-outline-variant p-3 min-h-[140px] flex flex-col">
          <p class="text-xs font-semibold text-gray-800 mb-2 line-clamp-2">{{ activeCard.title || '未命名图表' }}</p>
          <div class="flex-1 min-h-[100px]">
            <SimpleChart
              :chart-type="activeCard.chartType"
              :labels="activeCard.labels"
              :values="activeCard.values"
              :chart-color="chartColor"
            />
          </div>
        </div>
      </section>
    </template>

    <p v-else class="text-xs text-on-surface-variant text-center py-4">请添加至少一张卡片</p>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import SimpleChart from './SimpleChart.vue'
import { defaultChartStackContent, normalizeChartContent } from '../../composables/useSlideCanvas.js'

const props = defineProps({
  mode: { type: String, default: 'chartStack' },
  initialContent: { type: Object, default: null },
  chartColor: { type: String, default: '#005daa' },
})

const emit = defineEmits(['save'])

const chartTypeOptions = [
  { id: 'bar', label: '柱状图', icon: 'bar_chart' },
  { id: 'pie', label: '饼图', icon: 'pie_chart' },
]

const draftCards = ref([])
const activeCardId = ref('')
const dataRows = ref([])

const isStackMode = computed(() => props.mode === 'chartStack')

const activeCard = computed(() => draftCards.value.find((c) => c.id === activeCardId.value) || null)

function cloneCards(cards) {
  return cards.map((c) => ({
    id: c.id || `c_${Math.random().toString(36).slice(2, 10)}`,
    title: c.title || '',
    chartType: c.chartType || 'bar',
    labels: [...(c.labels || [])],
    values: [...(c.values || [])],
  }))
}

function cardFromSingleContent(content) {
  const normalized = normalizeChartContent(content)
  return {
    id: 'single',
    title: normalized.title || '',
    chartType: normalized.chartType || 'bar',
    labels: [...normalized.labels],
    values: [...normalized.values],
  }
}

function initDraft() {
  if (props.mode === 'chartStack') {
    const source = props.initialContent?.cards?.length
      ? props.initialContent.cards
      : defaultChartStackContent().cards
    draftCards.value = cloneCards(source)
  } else {
    draftCards.value = [cardFromSingleContent(props.initialContent)]
  }
  activeCardId.value = draftCards.value[0]?.id || ''
  syncCardToRows()
}

watch(
  () => [props.mode, props.initialContent],
  () => initDraft(),
  { immediate: true, deep: true }
)

watch(activeCardId, () => syncCardToRows())

function syncCardToRows() {
  const card = activeCard.value
  if (!card) {
    dataRows.value = []
    return
  }
  const len = Math.max(card.labels?.length || 0, card.values?.length || 0, 1)
  dataRows.value = Array.from({ length: len }, (_, i) => ({
    label: card.labels?.[i] ?? '',
    value: card.values?.[i] ?? 0,
  }))
}

function syncRowsToCard() {
  const card = activeCard.value
  if (!card) return
  card.labels = dataRows.value.map((r) => r.label)
  card.values = dataRows.value.map((r) => Number(r.value) || 0)
}

function setChartType(type) {
  const card = activeCard.value
  if (!card) return
  card.chartType = type
}

function addDataRow() {
  dataRows.value.push({ label: '', value: 0 })
  syncRowsToCard()
}

function removeDataRow(index) {
  if (dataRows.value.length <= 1) return
  dataRows.value.splice(index, 1)
  syncRowsToCard()
}

function addCard() {
  const id = `c_${Math.random().toString(36).slice(2, 10)}`
  draftCards.value.push({
    id,
    title: `新图表 ${draftCards.value.length + 1}`,
    chartType: 'bar',
    labels: ['A', 'B', 'C'],
    values: [30, 50, 40],
  })
  activeCardId.value = id
}

function removeActiveCard() {
  if (draftCards.value.length <= 1) return
  const idx = draftCards.value.findIndex((c) => c.id === activeCardId.value)
  if (idx < 0) return
  draftCards.value.splice(idx, 1)
  activeCardId.value = draftCards.value[Math.min(idx, draftCards.value.length - 1)]?.id || ''
}

function buildSavePayload() {
  syncRowsToCard()
  if (props.mode === 'chartStack') {
    return { cards: cloneCards(draftCards.value) }
  }
  const card = draftCards.value[0]
  if (!card) return normalizeChartContent(null)
  return {
    chartType: card.chartType,
    title: card.title,
    labels: [...card.labels],
    values: [...card.values],
  }
}

function save() {
  emit('save', buildSavePayload())
}

defineExpose({ save, buildSavePayload })
</script>
