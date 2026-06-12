<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[1300] flex items-center justify-center p-4 bg-black/45"
      @mousedown.self="$emit('close')"
    >
      <div
        class="w-full max-w-lg rounded-2xl overflow-hidden shadow-2xl border border-outline-variant/40"
        role="dialog"
        aria-modal="true"
        aria-labelledby="generate-card-title"
        @mousedown.stop
      >
        <div class="bg-gradient-to-br from-[#1a2744] via-[#243b6a] to-[#1e3a5f] px-5 py-4 text-white">
          <div class="flex items-start justify-between gap-3 mb-4">
            <h2 id="generate-card-title" class="text-base font-semibold">Generate card</h2>
            <button type="button" class="p-1 rounded hover:bg-white/10" aria-label="关闭" @click="$emit('close')">
              <span class="material-symbols-outlined text-[20px]">close</span>
            </button>
          </div>
          <textarea
            v-model="prompt"
            rows="3"
            class="w-full rounded-xl bg-black/25 border border-white/15 px-3 py-2.5 text-sm text-white placeholder:text-white/50 resize-none focus:outline-none focus:ring-2 focus:ring-primary/60"
            placeholder="描述你想制作的内容…"
            :disabled="loading"
          />
          <div class="flex flex-wrap gap-2 mt-3">
            <button
              v-for="tag in suggestedTags"
              :key="tag"
              type="button"
              class="text-xs px-2.5 py-1 rounded-full bg-white/10 hover:bg-white/20 border border-white/15 inline-flex items-center gap-1"
              :disabled="loading"
              @click="prompt = tag"
            >
              <span class="material-symbols-outlined text-[14px]">auto_awesome</span>
              {{ tag }}
            </button>
          </div>
        </div>

        <div class="bg-white px-5 py-4">
          <p class="text-xs font-medium text-on-surface-variant mb-2">Choose a template</p>
          <div class="flex flex-wrap gap-2 mb-4">
            <button
              v-for="t in templates"
              :key="t.id"
              type="button"
              class="px-3 py-2 rounded-lg border text-xs font-medium transition-colors"
              :class="templateHint === t.id ? 'border-primary bg-primary/8 text-primary' : 'border-outline-variant hover:bg-surface-container-low'"
              :disabled="loading"
              @click="templateHint = t.id"
            >
              {{ t.label }}
            </button>
          </div>

          <div class="flex items-center justify-between gap-3">
            <p v-if="quotaRemaining != null" class="text-xs text-on-surface-variant">
              剩余配额 {{ quotaRemaining }} / {{ quotaTotal }}
            </p>
            <div class="flex-1" />
            <button
              type="button"
              class="px-4 py-2 rounded-lg text-sm font-medium border border-outline-variant hover:bg-surface-container-low disabled:opacity-50"
              :disabled="loading"
              @click="$emit('close')"
            >
              取消
            </button>
            <button
              type="button"
              class="px-4 py-2 rounded-lg text-sm font-medium bg-primary text-on-primary inline-flex items-center gap-1.5 disabled:opacity-50"
              :disabled="loading || !prompt.trim()"
              @click="submit"
            >
              <span v-if="loading" class="material-symbols-outlined text-[18px] animate-spin">progress_activity</span>
              <span v-else class="material-symbols-outlined text-[18px]">send</span>
              {{ loading ? '生成中…' : '生成' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  quotaRemaining: { type: Number, default: null },
  quotaTotal: { type: Number, default: null },
})

const emit = defineEmits(['close', 'generate'])

const prompt = ref('')
const templateHint = ref('magic')

const suggestedTags = [
  '产品功能亮点',
  '学习数据分析',
  '家长协同管理',
  '师生互动体验',
]

const templates = [
  { id: 'magic', label: 'Magic' },
  { id: 'text', label: '文本' },
  { id: 'split', label: '分栏' },
  { id: 'image', label: '大图' },
  { id: 'grid', label: '网格' },
]

watch(
  () => props.open,
  (v) => {
    if (v) {
      prompt.value = ''
      templateHint.value = 'magic'
    }
  },
)

function submit() {
  const text = prompt.value.trim()
  if (!text || props.loading) return
  emit('generate', { prompt: text, templateHint: templateHint.value })
}
</script>
