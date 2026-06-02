<template>
  <AiCreateLayout header-variant="entry">
    <div class="text-center mb-6 sm:mb-8">
      <h1 class="text-3xl sm:text-4xl font-bold text-on-surface">生成</h1>
      <p class="text-on-surface-variant mt-2 text-sm sm:text-base">您今天想创建什么？</p>
    </div>

    <div class="flex flex-wrap justify-center gap-2.5 sm:gap-3 mb-6 max-w-3xl mx-auto w-full">
      <button
        v-for="tab in typeTabs"
        :key="tab.id"
        type="button"
        class="flex flex-col items-center gap-1.5 px-5 py-3 sm:px-6 sm:py-3.5 rounded-xl border min-w-[7rem] sm:min-w-[8.5rem] transition shadow-sm"
        :class="type === tab.id ? 'border-primary bg-primary/5 text-primary' : 'border-outline-variant/60 bg-white text-on-surface hover:border-outline-variant'"
        @click="type = tab.id"
      >
        <span class="material-symbols-outlined text-[24px] sm:text-[26px]">{{ tab.icon }}</span>
        <span class="text-sm font-medium">{{ tab.label }}</span>
      </button>
    </div>

    <div class="max-w-3xl mx-auto space-y-6">
      <div v-if="type === 'deck'" class="flex flex-wrap justify-start gap-2">
        <label class="relative inline-flex items-center">
          <select
            v-model.number="pageCount"
            class="appearance-none rounded-full border border-outline-variant bg-white pl-4 pr-9 py-2 text-sm text-on-surface cursor-pointer hover:bg-surface-container-low/50 transition"
          >
            <option v-for="n in 10" :key="n" :value="n">{{ n }} 张卡片</option>
          </select>
          <span class="material-symbols-outlined absolute right-2.5 text-[18px] text-on-surface-variant pointer-events-none">expand_more</span>
        </label>
        <label class="relative inline-flex items-center">
          <select
            v-model="background"
            class="appearance-none rounded-full border border-outline-variant bg-white pl-4 pr-9 py-2 text-sm text-on-surface cursor-pointer hover:bg-surface-container-low/50 transition"
          >
            <option value="classic_white">经典白粉</option>
            <option value="light_gray">浅灰</option>
          </select>
          <span class="material-symbols-outlined absolute right-2.5 text-[18px] text-on-surface-variant pointer-events-none">expand_more</span>
        </label>
        <label class="relative inline-flex items-center">
          <select
            v-model="viewportMode"
            class="appearance-none rounded-full border border-outline-variant bg-white pl-4 pr-9 py-2 text-sm text-on-surface cursor-pointer hover:bg-surface-container-low/50 transition"
          >
            <option value="auto">默认动态</option>
            <option value="web">传统网页</option>
            <option value="mobile">移动端</option>
          </select>
          <span class="material-symbols-outlined absolute right-2.5 text-[18px] text-on-surface-variant pointer-events-none">expand_more</span>
        </label>
        <label class="relative inline-flex items-center">
          <select
            v-model="language"
            class="appearance-none rounded-full border border-outline-variant bg-white pl-4 pr-9 py-2 text-sm text-on-surface cursor-pointer hover:bg-surface-container-low/50 transition"
          >
            <option value="简体中文">简体中文</option>
            <option value="English">English</option>
          </select>
          <span class="material-symbols-outlined absolute right-2.5 text-[18px] text-on-surface-variant pointer-events-none">expand_more</span>
        </label>
      </div>

      <div>
        <div class="relative bg-white rounded-2xl border border-outline-variant shadow-card min-h-[10rem] sm:min-h-[12rem]">
          <textarea
            ref="topicEl"
            v-model="topic"
            class="topic-input absolute inset-0 w-full h-full p-4 sm:p-5 bg-transparent text-sm leading-relaxed resize-none overflow-y-auto placeholder:text-on-surface-variant/60 caret-primary box-border rounded-2xl"
            placeholder="描述您想生成的…"
            @paste="onPaste"
          />
        </div>
        <p class="text-right text-xs text-on-surface-variant/60 mt-1.5 tabular-nums">{{ charCount }}</p>
      </div>

      <section v-if="type === 'deck'">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-semibold text-on-surface-variant">尝试这些示例提示</h2>
          <button
            type="button"
            class="text-primary hover:underline inline-flex items-center gap-1 text-sm"
            @click="rotateExamples"
          >
            <span class="material-symbols-outlined text-[16px]">refresh</span>
            换一组
          </button>
        </div>
        <div class="grid sm:grid-cols-2 gap-2">
          <button
            v-for="(ex, i) in currentExamples"
            :key="i"
            type="button"
            class="flex items-center gap-3 w-full text-left bg-white rounded-xl border border-outline-variant/50 px-3 py-3 shadow-sm hover:border-primary/30 hover:bg-primary/5 transition"
            @click="applyExample(ex)"
          >
            <span class="material-symbols-outlined text-[20px] text-primary shrink-0">{{ exampleIcons[i % exampleIcons.length] }}</span>
            <span class="flex-1 text-sm text-on-surface line-clamp-2 min-w-0">{{ ex }}</span>
            <span class="material-symbols-outlined text-[20px] text-primary shrink-0">add</span>
          </button>
        </div>
      </section>
    </div>

    <template #footer>
      <div class="flex justify-end">
        <button
          type="button"
          class="w-full sm:w-auto px-8 py-2.5 rounded-full bg-primary text-on-primary font-medium shadow-card hover:bg-primary/90 transition disabled:opacity-50"
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
import { EXAMPLE_PROMPT_GROUPS, loadDraft, saveDraft } from '../../composables/useAiCreateDraft.js'

const router = useRouter()
const type = ref('deck')
const pageCount = ref(10)
const background = ref('classic_white')
const viewportMode = ref('auto')
const language = ref('简体中文')
const topic = ref('')
const topicEl = ref(null)
const exampleGroup = ref(0)

const exampleIcons = ['eco', 'coffee', 'payments', 'analytics', 'psychology', 'monitoring']

const typeTabs = [
  { id: 'deck', label: '演示文稿', icon: 'stacked_bar_chart' },
  { id: 'image', label: '生成图片', icon: 'image' },
]

const charCount = computed(() => topic.value.length)
const currentExamples = computed(() => EXAMPLE_PROMPT_GROUPS[exampleGroup.value % EXAMPLE_PROMPT_GROUPS.length])

onMounted(() => {
  const draft = loadDraft()
  type.value = 'deck'
  pageCount.value = draft.pageCount || 10
  background.value = draft.background || 'classic_white'
  viewportMode.value = draft.viewportMode || 'auto'
  language.value = draft.language || '简体中文'
  topic.value = draft.topic || ''
})

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

function rotateExamples() {
  exampleGroup.value = (exampleGroup.value + 1) % EXAMPLE_PROMPT_GROUPS.length
}

function goNext() {
  if (!topic.value.trim()) return
  saveDraft({
    type: type.value,
    pageCount: pageCount.value,
    background: background.value,
    viewportMode: viewportMode.value,
    language: language.value,
    topic: topic.value.trim(),
  })
  if (type.value === 'image') {
    router.push('/create/generate/image')
    return
  }
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
