<template>
  <AiCreateLayout
    fill-height
    show-back
    back-label="上一步"
    @back="router.push('/create/generate')"
  >
    <div class="flex flex-col flex-1 min-h-0 gap-3 sm:gap-4">
      <div class="shrink-0">
        <h1 class="text-2xl sm:text-3xl font-bold">生成</h1>
        <p class="text-on-surface-variant text-sm mt-1">描述您想生成的内容</p>
        <p class="text-xs text-on-surface-variant mt-3 flex flex-wrap gap-2">
          <span class="bg-white/80 border border-outline-variant/50 rounded-full px-2.5 py-0.5">{{ draft.pageCount }} 页</span>
          <span class="bg-white/80 border border-outline-variant/50 rounded-full px-2.5 py-0.5">{{ backgroundLabel }}</span>
          <span class="bg-white/80 border border-outline-variant/50 rounded-full px-2.5 py-0.5">{{ viewportLabel }}</span>
          <span class="bg-white/80 border border-outline-variant/50 rounded-full px-2.5 py-0.5">{{ draft.language }}</span>
        </p>
      </div>

      <div class="flex flex-col flex-1 min-h-0">
        <div class="relative flex-1 min-h-[12rem] bg-white rounded-2xl shadow-sm">
          <textarea
            ref="topicEl"
            v-model="topic"
            class="topic-input absolute inset-0 w-full h-full p-4 sm:p-5 bg-transparent text-xs leading-relaxed resize-none overflow-y-auto placeholder:text-on-surface-variant/60 caret-primary box-border"
            placeholder="描述您想生成的内容…"
            @paste="onPaste"
          />
        </div>
        <p class="text-right text-xs text-on-surface-variant/60 mt-1.5 pr-0.5 shrink-0 tabular-nums">
          {{ charCount }}
        </p>
      </div>

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
import AiCreateLayout from '../../components/create/AiCreateLayout.vue'
import { loadDraft, requireDeckDraft, saveDraft } from '../../composables/useAiCreateDraft.js'
import { getImageColorLabel, getImageRatioOption } from '../../constants/imageGenerateOptions.js'

const router = useRouter()
const draft = ref(loadDraft())
const topic = ref('')
const topicEl = ref(null)

const charCount = computed(() => topic.value.length)
const hasTopic = computed(() => !!topic.value.trim())

function scrollInputToTop() {
  const el = topicEl.value
  if (!el) return
  el.scrollTop = 0
  el.setSelectionRange(0, 0)
}

function onPaste() {
  nextTick(() => {
    requestAnimationFrame(scrollInputToTop)
  })
}

const backgroundLabel = computed(() => {
  const bg = draft.value.background
  if (!bg) return '无'
  return getImageColorLabel(bg)
})
const viewportLabel = computed(() => {
  const ratio = draft.value.imageAspectRatio
  if (ratio) return getImageRatioOption(ratio).label
  const m = { auto: '默认动态', web: '传统网页', mobile: '移动端' }
  return m[draft.value.viewportMode] || '9:16'
})

onMounted(async () => {
  const d = requireDeckDraft(router)
  if (!d) return
  draft.value = d
  topic.value = d.topic || ''
  await nextTick()
  topicEl.value?.focus({ preventScroll: true })
  scrollInputToTop()
})

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
