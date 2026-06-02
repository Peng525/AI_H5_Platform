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

      <section class="shrink-0 pt-1">
        <div class="flex items-center justify-between mb-2" :class="!hasTopic && 'mb-3'">
          <h2 class="font-semibold text-on-surface-variant" :class="hasTopic ? 'text-xs' : 'text-sm'">示例提示</h2>
          <button
            type="button"
            class="text-primary hover:underline inline-flex items-center gap-1"
            :class="hasTopic ? 'text-xs' : 'text-sm'"
            @click="rotateExamples"
          >
            <span class="material-symbols-outlined" :class="hasTopic ? 'text-[14px]' : 'text-[16px]'">refresh</span>
            换一组
          </button>
        </div>
        <div class="grid sm:grid-cols-2" :class="hasTopic ? 'gap-2' : 'gap-3'">
          <button
            v-for="(ex, i) in currentExamples"
            :key="i"
            type="button"
            class="text-left bg-white/90 border border-outline-variant/50 hover:border-primary/40 hover:bg-primary/5 transition line-clamp-2"
            :class="hasTopic
              ? 'rounded-lg px-3 py-2 text-xs'
              : 'rounded-xl px-4 py-3 text-sm'"
            @click="applyExample(ex)"
          >
            {{ ex }}
          </button>
        </div>
      </section>
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
import { EXAMPLE_PROMPT_GROUPS, loadDraft, requireDeckDraft, saveDraft } from '../../composables/useAiCreateDraft.js'

const router = useRouter()
const draft = ref(loadDraft())
const topic = ref('')
const topicEl = ref(null)
const exampleGroup = ref(0)

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
