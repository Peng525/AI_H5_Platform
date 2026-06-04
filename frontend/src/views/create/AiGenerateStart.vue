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

    <div class="mx-auto w-full px-0 max-w-3xl space-y-6">
      <div v-if="type === 'deck'" class="generate-pills-bar flex flex-wrap justify-start gap-1.5 items-center">
        <AspectRatioSelect v-model="imageAspectRatio" @update:model-value="onAspectRatioChange" />
        <label class="relative inline-flex items-center">
          <select v-model="background" class="pill-select">
            <option v-for="opt in deckBackgroundOptions" :key="opt.value || 'none'" :value="opt.value">{{ opt.label }}</option>
          </select>
          <span class="material-symbols-outlined pill-chevron">expand_more</span>
        </label>
        <label class="relative inline-flex items-center">
          <select v-model.number="pageCount" class="pill-select">
            <option v-for="n in 10" :key="n" :value="n">{{ n }} 张卡片</option>
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

      <div v-if="type === 'image'" class="generate-pills-bar flex flex-wrap justify-start gap-1.5 items-center">
        <AspectRatioSelect v-model="imageAspectRatio" @update:model-value="onAspectRatioChange" />
        <label class="relative inline-flex items-center">
          <select v-model="imageColor" class="pill-select">
            <option v-for="opt in colorOptions" :key="opt.value || 'none'" :value="opt.value">{{ opt.label }}</option>
          </select>
          <span class="material-symbols-outlined pill-chevron">expand_more</span>
        </label>
        <label class="relative inline-flex items-center">
          <select v-model="imageStyle" class="pill-select">
            <option v-for="opt in imageStyleOptions" :key="opt.value || 'none'" :value="opt.value">{{ opt.label }}</option>
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
          <h2 class="text-sm font-semibold text-on-surface-variant mb-3">选择提示词模板</h2>
          <PageLoading v-if="deckPromptsLoading" message="加载模板…" />
          <p v-else-if="deckPromptsLoadError && !deckTemplates.length" class="text-sm text-red-600">
            {{ deckPromptsLoadError }}
            <button type="button" class="text-primary ml-2 hover:underline" @click="reloadDeckPromptTemplates">重试</button>
          </p>
          <p v-else-if="!deckTemplates.length" class="text-sm text-on-surface-variant">暂无提示词模板</p>
          <ul v-else class="flex md:grid md:grid-cols-3 gap-2 overflow-x-auto pb-1 md:overflow-visible snap-x snap-mandatory md:snap-none">
            <li
              v-for="tpl in deckTemplates"
              :key="tpl.id"
              class="snap-start shrink-0 w-[min(78vw,14rem)] md:w-auto md:shrink flex"
            >
              <PromptTemplateCard
                :title="tpl.title"
                :description="tpl.description"
                :fields="tpl.fields"
                :preview-url="tpl.preview_url || ''"
                :selected="selectedDeckTemplateId === tpl.id"
                @select="applyDeckTemplate(tpl)"
              />
            </li>
          </ul>
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
          <ul v-else class="flex md:grid md:grid-cols-3 gap-2 overflow-x-auto pb-1 md:overflow-visible snap-x snap-mandatory md:snap-none">
            <li
              v-for="tpl in imageTemplates"
              :key="tpl.id"
              class="snap-start shrink-0 w-[min(78vw,14rem)] md:w-auto md:shrink flex"
            >
              <PromptTemplateCard
                :title="tpl.title"
                :description="tpl.description"
                :fields="tpl.fields"
                :preview-url="tpl.preview_url || ''"
                :selected="selectedImageTemplateId === tpl.id"
                @select="applyImageTemplate(tpl)"
              />
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
import AspectRatioSelect from '../../components/create/AspectRatioSelect.vue'
import PromptTemplateCard from '../../components/create/PromptTemplateCard.vue'
import PageLoading from '../../components/PageLoading.vue'
import { loadDraft, saveDraft } from '../../composables/useAiCreateDraft.js'
import { useDeckPromptTemplates } from '../../composables/useDeckPromptTemplates.js'
import { useImagePromptTemplates } from '../../composables/useImagePromptTemplates.js'
import { formatDeckPromptTemplate } from '../../constants/deckPromptTemplates.js'
import { formatImagePromptTemplate } from '../../constants/imagePromptTemplates.js'
import {
  DECK_BACKGROUND_OPTIONS,
  IMAGE_COLOR_OPTIONS,
  IMAGE_STYLE_OPTIONS,
  aspectRatioToViewportMode,
  isValidImageStyle,
  viewportModeToAspectRatio,
} from '../../constants/imageGenerateOptions.js'

const TOPIC_MIN_PX = 44
const TOPIC_MAX_EMPTY_PX = 192
const TOPIC_MAX_FILLED_PX = 320

const router = useRouter()
const type = ref('deck')
const pageCount = ref(10)
const background = ref('')
const viewportMode = ref('auto')
const imageAspectRatio = ref('9:16')
const imageColor = ref('')
const imageStyle = ref('')
const language = ref('简体中文')
const topic = ref('')
const topicEl = ref(null)
const selectedImageTemplateId = ref('')
const selectedDeckTemplateId = ref('')

const {
  templates: imageTemplates,
  loading: promptsLoading,
  loadError: promptsLoadError,
  load: loadPromptTemplates,
  reload: reloadPromptTemplates,
} = useImagePromptTemplates()

const {
  templates: deckTemplates,
  loading: deckPromptsLoading,
  loadError: deckPromptsLoadError,
  load: loadDeckPromptTemplates,
  reload: reloadDeckPromptTemplates,
} = useDeckPromptTemplates()

const typeTabs = [
  { id: 'deck', label: '演示文稿', icon: 'stacked_bar_chart' },
  { id: 'image', label: '生成图片', icon: 'image' },
]

const colorOptions = IMAGE_COLOR_OPTIONS
const deckBackgroundOptions = DECK_BACKGROUND_OPTIONS
const imageStyleOptions = IMAGE_STYLE_OPTIONS

const charCount = computed(() => topic.value.length)
const hasTopic = computed(() => topic.value.trim().length > 0)

function topicMaxPx() {
  if (hasTopic.value && typeof window !== 'undefined') {
    return Math.min(TOPIC_MAX_FILLED_PX, Math.round(window.innerHeight * 0.35))
  }
  return TOPIC_MAX_EMPTY_PX
}

function onAspectRatioChange(ratio) {
  viewportMode.value = aspectRatioToViewportMode(ratio)
}

onMounted(() => {
  const draft = loadDraft()
  type.value = 'deck'
  pageCount.value = draft.pageCount || 10
  background.value = draft.background ?? ''
  viewportMode.value = draft.viewportMode || 'auto'
  imageColor.value = draft.imageColor ?? ''
  imageStyle.value = draft.imageStyle ?? ''
  imageAspectRatio.value = draft.imageAspectRatio
    || viewportModeToAspectRatio(draft.viewportMode)
  viewportMode.value = aspectRatioToViewportMode(imageAspectRatio.value)
  language.value = draft.language || '简体中文'
  topic.value = draft.topic || ''
  loadPromptTemplates()
  loadDeckPromptTemplates()
  nextTick(resizeTopicInput)
})

watch(hasTopic, () => {
  nextTick(resizeTopicInput)
})

watch(topic, (val) => {
  if (!val.trim()) {
    selectedImageTemplateId.value = ''
    selectedDeckTemplateId.value = ''
  }
  nextTick(resizeTopicInput)
})

function resizeTopicInput() {
  const el = topicEl.value
  if (!el) return
  el.style.height = 'auto'
  const maxPx = topicMaxPx()
  const next = Math.min(Math.max(el.scrollHeight, TOPIC_MIN_PX), maxPx)
  el.style.height = `${next}px`
  el.style.overflowY = el.scrollHeight > maxPx ? 'auto' : 'hidden'
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

function applyDeckTemplate(tpl) {
  selectedDeckTemplateId.value = tpl.id
  selectedImageTemplateId.value = ''
  topic.value = formatDeckPromptTemplate(tpl)
  nextTick(() => {
    scrollInputToTop()
    resizeTopicInput()
  })
}

function applyImageTemplate(tpl) {
  selectedImageTemplateId.value = tpl.id
  selectedDeckTemplateId.value = ''
  if (tpl.suggestedStyle && isValidImageStyle(tpl.suggestedStyle)) {
    imageStyle.value = tpl.suggestedStyle
  }
  topic.value = formatImagePromptTemplate(tpl)
  nextTick(() => {
    scrollInputToTop()
    resizeTopicInput()
  })
}

function goNext() {
  if (!topic.value.trim()) return
  const ratio = imageAspectRatio.value
  const vp = aspectRatioToViewportMode(ratio)
  if (type.value === 'image') {
    saveDraft({
      type: 'image',
      imageAspectRatio: ratio,
      viewportMode: vp,
      imageColor: imageColor.value,
      imageStyle: imageStyle.value,
      topic: topic.value.trim(),
    })
    router.push('/create/generate/image')
    return
  }
  saveDraft({
    type: type.value,
    pageCount: pageCount.value,
    background: background.value,
    imageAspectRatio: ratio,
    viewportMode: vp,
    language: language.value,
    topic: topic.value.trim(),
  })
  router.push('/create/generate/review')
}
</script>

<style scoped>
.generate-pills-bar {
  position: sticky;
  top: 0;
  z-index: 10;
  margin-bottom: 0.25rem;
  padding-top: 0.25rem;
  padding-bottom: 0.5rem;
  background: linear-gradient(to bottom, rgb(248 250 252 / 0.97) 75%, rgb(248 250 252 / 0));
}

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
