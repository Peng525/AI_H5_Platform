<template>
  <AiCreateLayout show-back back-label="上一步" :quota-text="quotaText" @back="router.push('/create/generate')">
    <div class="mb-6 shrink-0">
      <h1 class="text-2xl sm:text-3xl font-bold">生成</h1>
      <p class="text-on-surface-variant text-sm mt-1">描述您想生成的内容</p>
      <p class="text-xs text-on-surface-variant mt-3 flex flex-wrap gap-2">
        <span class="bg-white/80 border border-outline-variant/50 rounded-full px-2.5 py-0.5">{{ draft.pageCount }} 页</span>
        <span class="bg-white/80 border border-outline-variant/50 rounded-full px-2.5 py-0.5">{{ backgroundLabel }}</span>
        <span class="bg-white/80 border border-outline-variant/50 rounded-full px-2.5 py-0.5">{{ viewportLabel }}</span>
        <span class="bg-white/80 border border-outline-variant/50 rounded-full px-2.5 py-0.5">{{ draft.language }}</span>
      </p>
    </div>

    <div class="relative bg-white rounded-2xl shadow-sm p-4 sm:p-5 mb-6">
      <textarea
        ref="topicEl"
        v-model="topic"
        rows="8"
        class="topic-input w-full bg-transparent text-[11px] leading-relaxed resize-none overflow-y-auto placeholder:text-on-surface-variant/60 min-h-[8rem] max-h-[min(22rem,calc(100vh-16rem))] pb-6 caret-primary"
        placeholder="描述您想生成的内容…"
        @paste="onPaste"
      />
      <span class="absolute bottom-4 right-5 text-[11px] text-on-surface-variant/60 pointer-events-none select-none">
        {{ charCount }}
      </span>
    </div>

    <div class="mb-4 flex items-center justify-between">
      <h2 class="text-sm font-semibold text-on-surface-variant">示例提示</h2>
      <button type="button" class="text-sm text-primary hover:underline inline-flex items-center gap-1" @click="rotateExamples">
        <span class="material-symbols-outlined text-[16px]">refresh</span>
        换一组
      </button>
    </div>
    <div class="grid sm:grid-cols-2 gap-3">
      <button
        v-for="(ex, i) in currentExamples"
        :key="i"
        type="button"
        class="text-left bg-white/90 border border-outline-variant/50 rounded-xl px-4 py-3 text-sm hover:border-primary/40 hover:bg-primary/5 transition"
        @click="applyExample(ex)"
      >
        {{ ex }}
      </button>
    </div>

    <template #footer>
      <div class="flex justify-end">
        <button
          type="button"
          class="px-8 py-2.5 rounded-xl bg-primary text-on-primary font-medium disabled:opacity-50"
          :disabled="!topic.trim()"
          @click="goNext"
        >
          继续
        </button>
      </div>
    </template>
  </AiCreateLayout>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../../api/client'
import AiCreateLayout from '../../components/create/AiCreateLayout.vue'
import { EXAMPLE_PROMPT_GROUPS, loadDraft, requireDeckDraft, saveDraft } from '../../composables/useAiCreateDraft.js'

const router = useRouter()
const draft = ref(loadDraft())
const topic = ref('')
const topicEl = ref(null)
const exampleGroup = ref(0)
const quotaText = ref('')

const charCount = computed(() => topic.value.length)

function scrollInputToTop() {
  const el = topicEl.value
  if (!el) return
  el.scrollTop = 0
  el.setSelectionRange(0, 0)
  const main = el.closest('main')
  if (main) main.scrollTop = 0
}

function onPaste() {
  nextTick(() => {
    requestAnimationFrame(scrollInputToTop)
  })
}

function applyExample(ex) {
  topic.value = ex
  nextTick(scrollInputToTop)
}

const backgroundLabel = computed(() => (draft.value.background === 'light_gray' ? '浅灰' : '经典白粉'))
const viewportLabel = computed(() => {
  const m = { auto: '默认动态', web: '传统网页', mobile: '移动端' }
  return m[draft.value.viewportMode] || '默认动态'
})
const currentExamples = computed(() => EXAMPLE_PROMPT_GROUPS[exampleGroup.value % EXAMPLE_PROMPT_GROUPS.length])

onMounted(async () => {
  const d = requireDeckDraft(router)
  if (!d) return
  draft.value = d
  topic.value = d.topic || ''
  await nextTick()
  topicEl.value?.focus({ preventScroll: true })
  scrollInputToTop()
  try {
    const q = await api.getQuota()
    quotaText.value = `${q.quota_remaining}/${q.quota_total}`
  } catch {
    quotaText.value = '—'
  }
})

function rotateExamples() {
  exampleGroup.value = (exampleGroup.value + 1) % EXAMPLE_PROMPT_GROUPS.length
}

function goNext() {
  if (!topic.value.trim()) return
  saveDraft({ topic: topic.value.trim() })
  router.push('/create/generate/review')
}
</script>

<style scoped>
.topic-input {
  border: none;
  outline: none;
  box-shadow: none;
  appearance: none;
  -webkit-appearance: none;
}

.topic-input:focus,
.topic-input:focus-visible {
  border: none;
  outline: none;
  box-shadow: none;
}
</style>
