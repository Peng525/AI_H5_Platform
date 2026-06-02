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
      <div v-if="type === 'deck'" class="flex flex-wrap justify-start gap-1.5">
        <label class="relative inline-flex items-center">
          <select v-model.number="pageCount" class="pill-select">
            <option v-for="n in 10" :key="n" :value="n">{{ n }} 张卡片</option>
          </select>
          <span class="material-symbols-outlined pill-chevron">expand_more</span>
        </label>
        <label class="relative inline-flex items-center">
          <select v-model="background" class="pill-select">
            <option value="classic_white">经典白粉</option>
            <option value="light_gray">浅灰</option>
          </select>
          <span class="material-symbols-outlined pill-chevron">expand_more</span>
        </label>
        <label class="relative inline-flex items-center">
          <select v-model="viewportMode" class="pill-select">
            <option value="auto">默认动态</option>
            <option value="web">传统网页</option>
            <option value="mobile">移动端</option>
          </select>
          <span class="material-symbols-outlined pill-chevron">expand_more</span>
        </label>
        <label class="relative inline-flex items-center">
          <select v-model="language" class="pill-select">
            <option value="简体中文">简体中文</option>
            <option value="English">English</option>
          </select>
          <span class="material-symbols-outlined pill-chevron">expand_more</span>
        </label>
      </div>

      <div>
        <div class="rounded-2xl border border-outline-variant shadow-card overflow-hidden bg-white">
          <textarea
            ref="topicEl"
            v-model="topic"
            rows="1"
            class="topic-input w-full px-4 sm:px-5 py-3 sm:py-3.5 bg-transparent text-sm leading-relaxed resize-none overflow-y-hidden placeholder:text-on-surface-variant/60 caret-primary box-border"
            placeholder="描述您想生成的…"
            @input="resizeTopicInput"
            @paste="onPaste"
          />
        </div>
        <p class="text-right text-xs text-on-surface-variant/60 mt-1.5 tabular-nums">{{ charCount }}</p>
      </div>

      <div v-if="hasTopic" class="flex justify-center pt-2">
        <button
          type="button"
          class="inline-flex items-center gap-2 px-8 py-2.5 rounded-full bg-primary text-on-primary font-medium shadow-card hover:bg-primary/90 transition"
          @click="goNext"
        >
          <span class="material-symbols-outlined text-[18px]">auto_awesome</span>
          编辑提示词
        </button>
      </div>

      <template v-if="type === 'deck' && !hasTopic">
        <hr class="border-0 border-t border-outline-variant/50" />
        <section>
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
      </template>

      <template v-if="type === 'image' && !hasTopic">
        <hr class="border-0 border-t border-outline-variant/50" />
        <section>
          <h2 class="text-sm font-semibold text-on-surface-variant mb-3">选择提示词模板</h2>
          <PageLoading v-if="promptsLoading" message="加载模板…" />
          <p v-else-if="promptsLoadError && !imageTemplates.length" class="text-sm text-red-600">
            {{ promptsLoadError }}
            <button type="button" class="text-primary ml-2 hover:underline" @click="reloadPromptTemplates">重试</button>
          </p>
          <p v-else-if="!imageTemplates.length" class="text-sm text-on-surface-variant">暂无提示词模板</p>
          <ul v-else class="space-y-2">
            <li
              v-for="tpl in imageTemplates"
              :key="tpl.id"
              class="rounded-xl border bg-white shadow-sm overflow-hidden transition-colors"
              :class="selectedImageTemplateId === tpl.id ? 'border-primary ring-1 ring-primary/20' : 'border-outline-variant/50 hover:border-primary/30'"
            >
              <button type="button" class="w-full text-left p-3 sm:p-4" @click="applyImageTemplate(tpl)">
                <div class="flex items-start justify-between gap-2">
                  <div class="min-w-0">
                    <p class="text-sm font-medium text-on-surface">{{ tpl.title }}</p>
                    <p v-if="tpl.description" class="text-xs text-on-surface-variant mt-0.5">{{ tpl.description }}</p>
                  </div>
                  <span
                    v-if="selectedImageTemplateId === tpl.id"
                    class="material-symbols-outlined text-primary text-lg shrink-0"
                  >check_circle</span>
                </div>
                <table class="mt-2 w-full text-xs text-on-surface-variant border-collapse">
                  <tbody>
                    <tr v-for="field in tpl.fields" :key="field.label" class="align-top">
                      <td class="pr-2 py-0.5 whitespace-nowrap text-on-surface/70 w-10">{{ field.label }}</td>
                      <td class="py-0.5 leading-snug">{{ field.value }}</td>
                    </tr>
                  </tbody>
                </table>
              </button>
            </li>
          </ul>
        </section>
      </template>
    </div>
  </AiCreateLayout>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import AiCreateLayout from '../../components/create/AiCreateLayout.vue'
import PageLoading from '../../components/PageLoading.vue'
import { EXAMPLE_PROMPT_GROUPS, loadDraft, saveDraft } from '../../composables/useAiCreateDraft.js'
import { useImagePromptTemplates } from '../../composables/useImagePromptTemplates.js'
import { formatImagePromptTemplate } from '../../constants/imagePromptTemplates.js'

const TOPIC_MIN_PX = 44
const TOPIC_MAX_PX = 192

const router = useRouter()
const type = ref('deck')
const pageCount = ref(10)
const background = ref('classic_white')
const viewportMode = ref('auto')
const language = ref('简体中文')
const topic = ref('')
const topicEl = ref(null)
const exampleGroup = ref(0)
const selectedImageTemplateId = ref('')

const {
  templates: imageTemplates,
  loading: promptsLoading,
  loadError: promptsLoadError,
  load: loadPromptTemplates,
  reload: reloadPromptTemplates,
} = useImagePromptTemplates()

const exampleIcons = ['eco', 'coffee', 'payments', 'analytics', 'psychology', 'monitoring']

const typeTabs = [
  { id: 'deck', label: '演示文稿', icon: 'stacked_bar_chart' },
  { id: 'image', label: '生成图片', icon: 'image' },
]

const charCount = computed(() => topic.value.length)
const hasTopic = computed(() => topic.value.trim().length > 0)
const currentExamples = computed(() => EXAMPLE_PROMPT_GROUPS[exampleGroup.value % EXAMPLE_PROMPT_GROUPS.length])

onMounted(() => {
  const draft = loadDraft()
  type.value = 'deck'
  pageCount.value = draft.pageCount || 10
  background.value = draft.background || 'classic_white'
  viewportMode.value = draft.viewportMode || 'auto'
  language.value = draft.language || '简体中文'
  topic.value = draft.topic || ''
  loadPromptTemplates()
  nextTick(resizeTopicInput)
})

watch(topic, (val) => {
  if (!val.trim()) selectedImageTemplateId.value = ''
  nextTick(resizeTopicInput)
})

function resizeTopicInput() {
  const el = topicEl.value
  if (!el) return
  el.style.height = 'auto'
  const next = Math.min(Math.max(el.scrollHeight, TOPIC_MIN_PX), TOPIC_MAX_PX)
  el.style.height = `${next}px`
  el.style.overflowY = el.scrollHeight > TOPIC_MAX_PX ? 'auto' : 'hidden'
}

function scrollInputToTop() {
  const el = topicEl.value
  if (!el) return
  el.scrollTop = 0
  el.setSelectionRange(0, 0)
}

function onPaste() {
  nextTick(() => {
    requestAnimationFrame(() => {
      scrollInputToTop()
      resizeTopicInput()
    })
  })
}

function applyExample(ex) {
  selectedImageTemplateId.value = ''
  topic.value = ex
  nextTick(() => {
    scrollInputToTop()
    resizeTopicInput()
  })
}

function applyImageTemplate(tpl) {
  selectedImageTemplateId.value = tpl.id
  topic.value = formatImagePromptTemplate(tpl)
  nextTick(() => {
    scrollInputToTop()
    resizeTopicInput()
  })
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
.pill-select {
  @apply appearance-none rounded-full border border-outline-variant bg-white pl-2.5 pr-7 py-0.5 text-xs leading-5 text-on-surface cursor-pointer hover:bg-surface-container-low/50 transition max-w-full;
}

.pill-chevron {
  @apply absolute right-1.5 text-[15px] text-on-surface-variant pointer-events-none;
}

.topic-input {
  border: none;
  outline: none;
  box-shadow: none;
  appearance: none;
  -webkit-appearance: none;
  min-height: 2.75rem;
}

.topic-input:focus,
.topic-input:focus-visible {
  border: none;
  outline: none;
  box-shadow: none;
}
</style>
