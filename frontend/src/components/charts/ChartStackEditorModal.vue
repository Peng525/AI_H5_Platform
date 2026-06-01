<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="open" class="fixed inset-0 z-[200] bg-surface-container-low flex flex-col">
        <header class="shrink-0 flex items-center justify-between px-4 py-3 border-b border-outline-variant bg-white">
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">stacked_bar_chart</span>
            <h1 class="text-lg font-bold">图表卡组</h1>
          </div>
          <div class="flex items-center gap-2">
            <button
              type="button"
              class="px-3 py-1.5 text-sm bg-primary text-on-primary rounded-lg font-medium"
              :disabled="!draftCards.length"
              @click="save"
            >
              保存
            </button>
            <button type="button" class="p-2 rounded-lg hover:bg-surface-container" @click="$emit('close')">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
        </header>

        <div class="flex-1 flex min-h-0">
          <aside class="w-48 shrink-0 border-r border-outline-variant bg-white overflow-y-auto p-2 space-y-1">
            <div class="flex items-center justify-between px-1 mb-2">
              <p class="text-[10px] font-semibold text-on-surface-variant">卡片列表</p>
              <button
                type="button"
                class="text-[10px] text-primary font-medium px-2 py-0.5 rounded hover:bg-primary/5"
                @click="addCard"
              >
                + 添加
              </button>
            </div>
            <button
              v-for="(card, i) in draftCards"
              :key="card.id"
              type="button"
              class="w-full text-left rounded-lg border px-2 py-2 text-xs transition"
              :class="activeCardId === card.id ? 'border-primary ring-1 ring-primary bg-primary/5' : 'border-outline-variant hover:border-primary/40'"
              @click="activeCardId = card.id"
            >
              <span class="block font-medium truncate">{{ card.title || `卡片 ${i + 1}` }}</span>
              <span class="block text-[10px] text-on-surface-variant mt-0.5">{{ card.chartType === 'pie' ? '饼图' : '柱状图' }}</span>
            </button>
          </aside>

          <main class="flex-1 flex flex-col min-w-0 bg-surface-container-low">
            <div v-if="activeCard" class="flex-1 flex flex-col lg:flex-row min-h-0">
              <section class="flex-1 p-4 flex flex-col min-h-0">
                <p class="text-xs font-semibold text-on-surface-variant mb-2">预览</p>
                <div class="flex-1 bg-white rounded-xl shadow border border-outline-variant p-3 min-h-[200px] max-w-md mx-auto w-full flex flex-col">
                  <p class="text-sm font-semibold text-gray-800 mb-2 line-clamp-2">{{ activeCard.title || '未命名图表' }}</p>
                  <div class="flex-1 min-h-0">
                    <SimpleChart
                      :chart-type="activeCard.chartType"
                      :labels="activeCard.labels"
                      :values="activeCard.values"
                      chart-color="#005daa"
                    />
                  </div>
                </div>
              </section>

              <section class="w-full lg:w-80 shrink-0 border-t lg:border-t-0 lg:border-l border-outline-variant bg-white p-4 overflow-y-auto space-y-3">
                <label class="block">
                  <span class="text-xs font-semibold text-on-surface">标题</span>
                  <input
                    v-model="activeCard.title"
                    type="text"
                    class="mt-1 w-full text-sm border border-outline-variant rounded-lg px-2 py-1.5"
                    placeholder="图表标题"
                  />
                </label>

                <label class="block">
                  <span class="text-xs font-semibold text-on-surface">图表类型</span>
                  <select
                    v-model="activeCard.chartType"
                    class="mt-1 w-full text-sm border border-outline-variant rounded-lg px-2 py-1.5"
                  >
                    <option value="bar">柱状图</option>
                    <option value="pie">饼图</option>
                  </select>
                </label>

                <label class="block">
                  <span class="text-xs font-semibold text-on-surface">数据（每行：标签,数值）</span>
                  <textarea
                    v-model="dataText"
                    rows="6"
                    class="mt-1 w-full text-sm border border-outline-variant rounded-lg px-2 py-1.5 font-mono"
                    placeholder="增加,45&#10;维持,35&#10;减少,20"
                    @blur="parseDataText"
                  />
                </label>

                <button
                  type="button"
                  class="w-full text-sm text-red-600 border border-red-200 rounded-lg py-1.5 hover:bg-red-50"
                  :disabled="draftCards.length <= 1"
                  @click="removeActiveCard"
                >
                  删除当前卡片
                </button>
              </section>
            </div>
            <div v-else class="flex-1 flex items-center justify-center text-sm text-on-surface-variant">
              请添加至少一张卡片
            </div>
          </main>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import SimpleChart from './SimpleChart.vue'
import { defaultChartStackContent } from '../../composables/useSlideCanvas.js'

const props = defineProps({
  open: { type: Boolean, default: false },
  initialContent: { type: Object, default: null },
})

const emit = defineEmits(['close', 'save'])

const draftCards = ref([])
const activeCardId = ref('')

function cloneCards(cards) {
  return cards.map((c) => ({
    id: c.id || `c_${Math.random().toString(36).slice(2, 10)}`,
    title: c.title || '',
    chartType: c.chartType || 'bar',
    labels: [...(c.labels || [])],
    values: [...(c.values || [])],
  }))
}

watch(
  () => props.open,
  (v) => {
    if (!v) return
    const source = props.initialContent?.cards?.length
      ? props.initialContent.cards
      : defaultChartStackContent().cards
    draftCards.value = cloneCards(source)
    activeCardId.value = draftCards.value[0]?.id || ''
  }
)

const activeCard = computed(() => draftCards.value.find((c) => c.id === activeCardId.value) || null)

const dataText = computed({
  get() {
    const card = activeCard.value
    if (!card) return ''
    const labels = card.labels || []
    const values = card.values || []
    const len = Math.max(labels.length, values.length)
    const lines = []
    for (let i = 0; i < len; i += 1) {
      lines.push(`${labels[i] ?? ''},${values[i] ?? 0}`)
    }
    return lines.join('\n')
  },
  set(v) {
    parseDataTextFrom(v)
  },
})

function parseDataTextFrom(text) {
  const card = activeCard.value
  if (!card) return
  const labels = []
  const values = []
  text.split('\n').forEach((line) => {
    const trimmed = line.trim()
    if (!trimmed) return
    const comma = trimmed.indexOf(',')
    if (comma >= 0) {
      labels.push(trimmed.slice(0, comma).trim())
      values.push(Number(trimmed.slice(comma + 1).trim()) || 0)
    } else {
      labels.push(trimmed)
      values.push(0)
    }
  })
  card.labels = labels
  card.values = values
}

function parseDataText() {
  parseDataTextFrom(dataText.value)
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

function save() {
  parseDataText()
  emit('save', { cards: cloneCards(draftCards.value) })
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
