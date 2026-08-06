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

      <div v-if="type !== 'resume-edit' && type !== 'resume-optimize'">
        <div v-if="type === 'deck'" class="flex items-center justify-start mb-2">
          <button
            type="button"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-outline-variant/80 bg-white text-xs font-medium text-on-surface hover:bg-surface-container-low transition disabled:opacity-50"
            :disabled="pptTemplateImporting"
            @click="triggerPptTemplateImport"
          >
            <span class="material-symbols-outlined text-[16px]">upload</span>
            {{ pptTemplateImporting ? '导入中…' : '导入 PPT 模板' }}
          </button>
          <input
            ref="pptTemplateFileRef"
            type="file"
            accept=".pptx,application/vnd.openxmlformats-officedocument.presentationml.presentation"
            class="hidden"
            @change="onPptTemplateFileSelected"
          />
        </div>
        <p v-if="pptTemplateImportError" class="text-xs text-red-600 mb-2">{{ pptTemplateImportError }}</p>
        <GenerateTopicInput
          ref="topicInputRef"
          v-model="topic"
          placeholder="描述您想生成的…"
          @paste="onPaste"
        />
        <p class="text-right text-xs text-on-surface-variant/60 mt-1.5 tabular-nums">{{ charCount }}</p>
      </div>

      <template v-if="type === 'resume-edit'">
        <PageLoading v-if="visualTemplatesLoading" message="加载模板…" />
        <p v-else-if="visualTemplatesError" class="text-sm text-red-600">{{ visualTemplatesError }}</p>
        <ResumeTemplatePicker
          v-else
          heading="选择简历模板"
          :templates="visualTemplates"
          :selected-id="selectedVisualTemplateId"
          @select="onSelectVisualTemplate"
        />
        <p v-if="editCreating" class="text-center text-sm text-on-surface-variant pt-2">正在创建…</p>
        <p v-if="editError" class="text-sm text-red-600">{{ editError }}</p>
      </template>

      <template v-else-if="type === 'resume-optimize'">
        <ResumeOptimizeForm
          ref="resumeOptimizeRef"
          v-model:prompt="resumePrompt"
          :resume-file-name="resumeFileName"
          :jd-file-name="jdFileName"
          :resume-file="pendingResumeFile"
          :jd-file="pendingJdFile"
          :resume-uploading="resumeUploading"
          :jd-uploading="jdUploading"
          :generating="resumeGenerating"
          :can-generate="canResumeGenerate"
          :error="resumeUploadError"
          :resume-error="resumeFieldError"
          :jd-error="jdFieldError"
          @select-resume="onResumeFileSelect"
          @remove-resume="onResumeFileRemove"
          @select-jd="onJdFileSelect"
          @remove-jd="onJdFileRemove"
          @generate="goResumeGenerate"
          @paste="onResumePaste"
        >
          <template #after-prompt>
            <PageLoading v-if="visualTemplatesLoading && !visualTemplates.length" message="加载模板…" />
            <p v-else-if="visualTemplatesError" class="text-sm text-red-600">{{ visualTemplatesError }}</p>
            <ResumeOptimizeSteps
              v-else
              :step="resumeOptimizeStep"
              :visual-templates="filteredVisualTemplates"
              :prompt-templates="filteredPromptTemplates"
              :industries="industries"
              :selected-visual-id="selectedVisualTemplateId"
              :selected-visual-title="selectedVisualTitle"
              :selected-prompt-id="selectedResumeTemplateId"
              :selected-industry-id="selectedIndustryId"
              :template-error="templateSelectError"
              :prompt-loading="promptTemplatesLoading"
              :prompt-error="promptTemplatesError"
              @select-visual="onSelectVisualForOptimize"
              @select-prompt="applyResumeTemplate"
              @back-visual="onBackToVisualStep"
              @update:industry="onIndustryChange"
            />
          </template>
          <template #generate-hint>
            <ResumeGenerateHintBubble ref="hintBubbleRef" />
          </template>
        </ResumeOptimizeForm>
      </template>

      <div v-if="type !== 'resume-edit' && type !== 'resume-optimize' && hasTopic" class="flex flex-col items-center pt-2 gap-2">
        <div
          v-if="type === 'deck' && selectedPptTemplate"
          class="flex flex-wrap items-center justify-center gap-2 text-sm"
        >
          <span class="text-on-surface-variant">已选：</span>
          <span class="inline-flex items-center rounded-full bg-primary/10 text-primary px-3 py-1 text-xs font-medium">
            {{ selectedPptTemplate.title }}
          </span>
          <button
            type="button"
            class="text-xs text-primary hover:underline"
            @click="showTemplatePicker = true"
          >
            更换模板
          </button>
        </div>
        <button
          type="button"
          class="inline-flex items-center gap-2 px-8 py-2.5 rounded-full bg-primary text-on-primary font-medium shadow-card hover:bg-primary/90 transition"
          @click="goNext"
        >
          <span class="material-symbols-outlined text-[18px]">auto_awesome</span>
          继续生成
        </button>
        <p v-if="type === 'deck'" class="text-xs text-on-surface-variant">
          下一步可调整页数、语气与内容
        </p>
      </div>

      <template v-if="type === 'deck' && (!hasTopic || showTemplatePicker)">
        <hr class="border-0 border-t border-outline-variant/50" />
        <DeckPptTemplatePicker
          heading="选择 PPT 模板"
          :templates="deckPptTemplates"
          :selected-id="selectedPptTemplateId"
          :loading="deckPptTemplatesLoading"
          :load-error="deckPptTemplatesError"
          @select="onSelectPptTemplate"
          @retry="loadDeckPptTemplates"
        />
        <p v-if="pptTemplateError" class="text-sm text-red-600 mt-2">{{ pptTemplateError }}</p>
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
import { useRoute, useRouter } from 'vue-router'
import AiCreateLayout from '../../components/create/AiCreateLayout.vue'
import AspectRatioSelect from '../../components/create/AspectRatioSelect.vue'
import DeckPptTemplatePicker from '../../components/create/DeckPptTemplatePicker.vue'
import GenerateTopicInput from '../../components/create/GenerateTopicInput.vue'
import PromptTemplateCard from '../../components/create/PromptTemplateCard.vue'
import PageLoading from '../../components/PageLoading.vue'
import ResumeOptimizeForm from '../../components/resume/ResumeOptimizeForm.vue'
import ResumeOptimizeSteps from '../../components/resume/ResumeOptimizeSteps.vue'
import ResumeGenerateHintBubble from '../../components/resume/ResumeGenerateHintBubble.vue'
import ResumeTemplatePicker from '../../components/resume/ResumeTemplatePicker.vue'
import { api } from '../../api/client.js'
import { useToast } from '../../composables/useToast.js'
import { loadDraft, saveDraft } from '../../composables/useAiCreateDraft.js'
import { loadResumeDraft, saveResumeDraft, clearResumeDraft, resolveResumeTab } from '../../composables/useResumeDraft.js'
import { savePendingGenerate } from '../../composables/useResumePendingGenerate.js'
import { isQuotaExceeded, isResumeLimit, isContentPolicy } from '../../composables/useResumeErrors.js'
import { useImagePromptTemplates } from '../../composables/useImagePromptTemplates.js'
import { formatImagePromptTemplate } from '../../constants/imagePromptTemplates.js'
import {
  DECK_BACKGROUND_OPTIONS,
  IMAGE_COLOR_OPTIONS,
  IMAGE_STYLE_OPTIONS,
  aspectRatioToViewportMode,
  isValidImageStyle,
  viewportModeToAspectRatio,
} from '../../constants/imageGenerateOptions.js'

const router = useRouter()
const route = useRoute()
const { success: toastSuccess } = useToast()
const type = ref('deck')
const pageCount = ref(10)
const background = ref('')
const viewportMode = ref('auto')
const imageAspectRatio = ref('9:16')
const imageColor = ref('')
const imageStyle = ref('')
const language = ref('简体中文')
const topic = ref('')
const topicInputRef = ref(null)
const selectedImageTemplateId = ref('')
const selectedPptTemplateId = ref('')
const pptTemplateError = ref('')
const showTemplatePicker = ref(false)
const pptTemplateFileRef = ref(null)
const pptTemplateImporting = ref(false)
const pptTemplateImportError = ref('')
const deckPptTemplates = ref([])
const deckPptTemplatesLoading = ref(false)
const deckPptTemplatesError = ref('')
const resumePrompt = ref('')
const resumeFileId = ref(null)
const resumeFileName = ref('')
const jdFileId = ref(null)
const jdFileName = ref('')
const resumeUploading = ref(false)
const jdUploading = ref(false)
const resumeUploadError = ref('')
const resumeFieldError = ref('')
const jdFieldError = ref('')
const resumeGenerating = ref(false)
const resumePromptTemplates = ref([])
const promptTemplatesLoading = ref(false)
const promptTemplatesError = ref('')
const industries = ref([])
const selectedIndustryId = ref('all')
const resumeOptimizeStep = ref('visual')
const visualTemplates = ref([])
const visualTemplatesLoading = ref(false)
const visualTemplatesError = ref('')
const selectedResumeTemplateId = ref('')
const selectedVisualTemplateId = ref('')
const templateSelectError = ref('')
const resumeOptimizeRef = ref(null)
const hintBubbleRef = ref(null)
const editCreating = ref(false)
const editError = ref('')
const pendingResumeFile = ref(null)
const pendingJdFile = ref(null)

const {
  templates: imageTemplates,
  loading: promptsLoading,
  loadError: promptsLoadError,
  load: loadPromptTemplates,
  reload: reloadPromptTemplates,
} = useImagePromptTemplates()

const typeTabs = [
  { id: 'deck', label: '演示文稿', icon: 'stacked_bar_chart' },
  { id: 'image', label: '生成图片', icon: 'image' },
  { id: 'resume-edit', label: '简历编辑', icon: 'edit_document' },
  { id: 'resume-optimize', label: '简历优化', icon: 'auto_awesome' },
]

const colorOptions = IMAGE_COLOR_OPTIONS
const deckBackgroundOptions = DECK_BACKGROUND_OPTIONS
const imageStyleOptions = IMAGE_STYLE_OPTIONS

const charCount = computed(() => topic.value.length)
const hasTopic = computed(() => topic.value.trim().length > 0)
const selectedPptTemplate = computed(() =>
  deckPptTemplates.value.find((t) => t.id === selectedPptTemplateId.value) || null,
)
const hasResumeInput = computed(() =>
  resumePrompt.value.trim().length > 0
  || !!resumeFileId.value
  || !!pendingResumeFile.value
  || !!jdFileId.value
  || !!pendingJdFile.value,
)
const showResumePromptTemplates = computed(() => resumeOptimizeStep.value === 'prompt')
const selectedVisualTitle = computed(() => {
  const tpl = visualTemplates.value.find((t) => t.id === selectedVisualTemplateId.value)
  return tpl?.title || ''
})
const canResumeGenerate = computed(() =>
  resumePrompt.value.trim()
  || resumeFileId.value
  || pendingResumeFile.value
  || jdFileId.value
  || pendingJdFile.value,
)

const filteredPromptTemplates = computed(() => {
  if (selectedIndustryId.value === 'all') return resumePromptTemplates.value
  return resumePromptTemplates.value.filter((t) => t.industry_id === selectedIndustryId.value)
})

const filteredVisualTemplates = computed(() => {
  if (selectedIndustryId.value === 'all') return visualTemplates.value
  return visualTemplates.value.filter((t) =>
    (t.industry_tags || []).includes(selectedIndustryId.value),
  )
})
const isResumeTab = computed(() => type.value === 'resume-edit' || type.value === 'resume-optimize')

function resizeTopicInput() {
  topicInputRef.value?.resize()
}

function scrollInputToTop() {
  topicInputRef.value?.scrollToTop()
}

function onAspectRatioChange(ratio) {
  viewportMode.value = aspectRatioToViewportMode(ratio)
}

onMounted(() => {
  const draft = loadDraft()
  const rd = loadResumeDraft()
  type.value = resolveResumeTab(route.query.tab) || 'deck'
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
  selectedPptTemplateId.value = draft.pptTemplateId || ''
  resumePrompt.value = rd.prompt || ''
  resumeFileId.value = rd.fileId
  resumeFileName.value = rd.fileName || ''
  jdFileId.value = rd.jdFileId ?? null
  jdFileName.value = rd.jdFileName || ''
  selectedResumeTemplateId.value = rd.selectedPromptTemplateId || rd.selectedTemplateId || ''
  selectedVisualTemplateId.value = rd.selectedVisualTemplateId || ''
  selectedIndustryId.value = rd.selectedIndustryId || 'all'
  resumeOptimizeStep.value = rd.selectedVisualTemplateId ? 'prompt' : 'visual'
  loadPromptTemplates()
  loadDeckPptTemplates()
  loadIndustries()
  loadResumePromptTemplates()
  if (isResumeTab.value) loadVisualTemplates()
  nextTick(resizeTopicInput)
})

watch(() => route.query.tab, (tab) => {
  const resumeTab = resolveResumeTab(tab)
  if (resumeTab) type.value = resumeTab
})

watch(type, (val) => {
  if ((val === 'resume-edit' || val === 'resume-optimize') && !visualTemplates.value.length) {
    loadVisualTemplates()
  }
  if (val === 'deck' && !deckPptTemplates.value.length) {
    loadDeckPptTemplates()
  }
  if (val === 'resume-optimize') resumeOptimizeStep.value = selectedVisualTemplateId.value ? 'prompt' : 'visual'
  if (isResumeTab.value) {
    saveResumeDraft({
      tab: val,
      prompt: resumePrompt.value,
      fileId: resumeFileId.value,
      fileName: resumeFileName.value,
      jdFileId: jdFileId.value,
      jdFileName: jdFileName.value,
      selectedPromptTemplateId: selectedResumeTemplateId.value,
      selectedVisualTemplateId: selectedVisualTemplateId.value,
      selectedIndustryId: selectedIndustryId.value,
    })
  }
})

async function loadIndustries() {
  try {
    const data = await api.listResumeIndustries()
    industries.value = data.items || []
  } catch {
    industries.value = [{ id: 'all', label: '全部' }]
  }
}

function onIndustryChange(id) {
  selectedIndustryId.value = id
  if (selectedResumeTemplateId.value) {
    const still = filteredPromptTemplates.value.some((t) => t.id === selectedResumeTemplateId.value)
    if (!still) selectedResumeTemplateId.value = ''
  }
  saveResumeDraft({
    tab: type.value,
    selectedIndustryId: id,
    selectedVisualTemplateId: selectedVisualTemplateId.value,
    selectedPromptTemplateId: selectedResumeTemplateId.value,
  })
}

function onSelectVisualForOptimize(tpl) {
  selectedVisualTemplateId.value = tpl.id
  templateSelectError.value = ''
  resumeOptimizeStep.value = 'prompt'
  saveResumeDraft({
    tab: type.value,
    selectedVisualTemplateId: tpl.id,
    selectedIndustryId: selectedIndustryId.value,
  })
}

function onBackToVisualStep() {
  resumeOptimizeStep.value = 'visual'
  templateSelectError.value = ''
}

async function loadResumePromptTemplates() {
  promptTemplatesLoading.value = true
  promptTemplatesError.value = ''
  try {
    const data = await api.listResumeTemplates()
    resumePromptTemplates.value = (data.items || []).map((t) => ({
      id: t.id,
      title: t.title,
      description: t.description,
      prompt_hint: t.prompt_hint,
      prompt_full: t.prompt_full || t.prompt_hint,
      fields: t.fields || [],
      industry_id: t.industry_id,
    }))
  } catch (e) {
    promptTemplatesError.value = e.message || '加载提示词失败'
    resumePromptTemplates.value = []
  } finally {
    promptTemplatesLoading.value = false
  }
}

async function loadVisualTemplates() {
  visualTemplatesLoading.value = true
  visualTemplatesError.value = ''
  try {
    const data = await api.listResumeVisualTemplates()
    visualTemplates.value = (data.items || []).map((t) => ({
      id: t.id,
      title: t.title,
      description: t.description,
      preview_url: t.preview_url || '',
      industry_tags: t.industry_tags || [],
    }))
  } catch (e) {
    visualTemplatesError.value = e.message || '加载模板失败'
    visualTemplates.value = []
  } finally {
    visualTemplatesLoading.value = false
  }
}

watch([resumePrompt, resumeFileId, resumeFileName, jdFileId, jdFileName], () => {
  if (!isResumeTab.value) return
  saveResumeDraft({
    tab: type.value,
    prompt: resumePrompt.value,
    fileId: resumeFileId.value,
    fileName: resumeFileName.value,
    jdFileId: jdFileId.value,
    jdFileName: jdFileName.value,
    selectedPromptTemplateId: selectedResumeTemplateId.value,
    selectedVisualTemplateId: selectedVisualTemplateId.value,
    selectedIndustryId: selectedIndustryId.value,
  })
  nextTick(() => resumeOptimizeRef.value?.resize())
})

watch(hasTopic, () => {
  nextTick(resizeTopicInput)
})

watch(topic, (val) => {
  if (!val.trim()) {
    selectedImageTemplateId.value = ''
  }
  nextTick(resizeTopicInput)
})

function onPaste() {
  /* resize handled inside GenerateTopicInput */
}

function onResumePaste() {
  nextTick(() => resumeOptimizeRef.value?.resize())
}

function applyResumeTemplate(tpl) {
  selectedResumeTemplateId.value = tpl.id
  resumePrompt.value = tpl.prompt_full || tpl.prompt_hint || tpl.description || ''
  nextTick(() => resumeOptimizeRef.value?.resize())
}

async function onSelectVisualTemplate(tpl) {
  if (editCreating.value) return
  selectedVisualTemplateId.value = tpl.id
  editCreating.value = true
  editError.value = ''
  try {
    const created = await api.createResume({ template_id: tpl.id })
    router.push(`/create/generate/resume/${created.public_id}?mode=edit`)
  } catch (e) {
    if (isResumeLimit(e)) {
      editError.value = e.message || '最多保存 5 份简历，请先在「个人简历」中删除旧简历'
      return
    }
    editError.value = e.message || '创建失败'
  } finally {
    editCreating.value = false
  }
}

async function onResumeFileSelect(payload) {
  if (payload.error) {
    resumeFieldError.value = payload.error
    return
  }
  resumeFieldError.value = ''
  pendingResumeFile.value = payload.file
  resumeFileName.value = payload.file.name
  resumeFileId.value = null
}

function onResumeFileRemove() {
  pendingResumeFile.value = null
  resumeFileName.value = ''
  resumeFileId.value = null
  resumeFieldError.value = ''
}

async function onJdFileSelect(payload) {
  if (payload.error) {
    jdFieldError.value = payload.error
    return
  }
  jdFieldError.value = ''
  pendingJdFile.value = payload.file
  jdFileName.value = payload.file.name
  jdFileId.value = null
}

function onJdFileRemove() {
  pendingJdFile.value = null
  jdFileName.value = ''
  jdFileId.value = null
  jdFieldError.value = ''
}

async function goResumeGenerate() {
  if (resumeGenerating.value) return
  if (!selectedVisualTemplateId.value) {
    templateSelectError.value = '请选择简历模板'
    return
  }
  if (!canResumeGenerate.value) return
  templateSelectError.value = ''
  resumeGenerating.value = true
  resumeUploadError.value = ''
  let createdPublicId = null
  try {
    let fileId = resumeFileId.value
    let jdId = jdFileId.value
    if (pendingResumeFile.value) {
      resumeUploading.value = true
      const fd = new FormData()
      fd.append('file', pendingResumeFile.value)
      const up = await api.uploadResumeFile(fd)
      fileId = up.file_id
      resumeFileId.value = fileId
      pendingResumeFile.value = null
      resumeUploading.value = false
    }
    if (pendingJdFile.value) {
      jdUploading.value = true
      const fd = new FormData()
      fd.append('file', pendingJdFile.value)
      const up = await api.uploadResumeFile(fd)
      jdId = up.file_id
      jdFileId.value = jdId
      pendingJdFile.value = null
      jdUploading.value = false
    }
    const created = await api.createResume({
      prompt: resumePrompt.value.trim() || undefined,
      file_id: fileId || undefined,
      jd_file_id: jdId || undefined,
      template_id: selectedVisualTemplateId.value,
      prompt_template_id: selectedResumeTemplateId.value || undefined,
      industry_id: selectedIndustryId.value !== 'all' ? selectedIndustryId.value : undefined,
    })
    createdPublicId = created.public_id
    savePendingGenerate(created.public_id, {
      prompt: resumePrompt.value.trim() || undefined,
      file_id: fileId || undefined,
      jd_file_id: jdId || undefined,
      template_id: selectedVisualTemplateId.value,
      prompt_template_id: selectedResumeTemplateId.value || undefined,
      industry_id: selectedIndustryId.value !== 'all' ? selectedIndustryId.value : undefined,
    })
    hintBubbleRef.value?.dismissAfterGenerate?.()
    clearResumeDraft()
    router.push(`/create/generate/resume/${created.public_id}?mode=optimize&generating=1`)
  } catch (e) {
    if (createdPublicId) {
      try {
        await api.deleteResume(createdPublicId)
      } catch {
        /* ignore cleanup failure */
      }
    }
    if (isQuotaExceeded(e)) {
      resumeUploadError.value = e.message || '配额已用完'
      router.push('/upgrade')
      return
    }
    if (isResumeLimit(e)) {
      resumeUploadError.value = e.message || '最多保存 5 份简历，请先在「个人简历」中删除旧简历'
      return
    }
    if (isContentPolicy(e)) {
      resumeUploadError.value = e.message || '内容不符合规范'
      return
    }
    resumeUploadError.value = e.message || '创建失败'
  } finally {
    resumeGenerating.value = false
    resumeUploading.value = false
    jdUploading.value = false
  }
}

function onSelectPptTemplate(tpl) {
  selectedPptTemplateId.value = tpl.id
  pptTemplateError.value = ''
  showTemplatePicker.value = false
  saveDraft({
    pptTemplateId: tpl.id,
    pptTemplateKind: tpl.kind || '',
  })
}

async function loadDeckPptTemplates() {
  deckPptTemplatesLoading.value = true
  deckPptTemplatesError.value = ''
  try {
    const data = await api.listDeckPptTemplates()
    deckPptTemplates.value = data.items || []
  } catch (e) {
    deckPptTemplatesError.value = e.message || '加载 PPT 模板失败'
    deckPptTemplates.value = []
  } finally {
    deckPptTemplatesLoading.value = false
  }
}

function triggerPptTemplateImport() {
  pptTemplateImportError.value = ''
  pptTemplateFileRef.value?.click()
}

async function onPptTemplateFileSelected(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  if (!file.name.toLowerCase().endsWith('.pptx')) {
    pptTemplateImportError.value = '请选择 .pptx 文件'
    return
  }
  pptTemplateImporting.value = true
  pptTemplateImportError.value = ''
  try {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('title', file.name.replace(/\.pptx$/i, ''))
    const imported = await api.importDeckPptTemplate(fd)
    await loadDeckPptTemplates()
    const tpl = deckPptTemplates.value.find((t) => t.id === imported.id)
      || {
        id: imported.id,
        kind: imported.kind || 'deck',
        title: imported.title,
        description: '',
        preview_url: imported.preview_url,
      }
    onSelectPptTemplate(tpl)
    showTemplatePicker.value = false
    toastSuccess(`已导入模板「${imported.title || tpl.title}」`)
  } catch (err) {
    pptTemplateImportError.value = err.message || '导入失败'
  } finally {
    pptTemplateImporting.value = false
  }
}

function applyImageTemplate(tpl) {
  selectedImageTemplateId.value = tpl.id
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
  if (type.value === 'deck' && !selectedPptTemplateId.value) {
    pptTemplateError.value = '请选择 PPT 模板'
    return
  }
  pptTemplateError.value = ''
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
    extraContent: topic.value.trim(),
    contentMode: 'free',
    cardSplitMode: null,
    pageContents: [],
    pptTemplateId: selectedPptTemplateId.value,
    pptTemplateKind: deckPptTemplates.value.find((t) => t.id === selectedPptTemplateId.value)?.kind || '',
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
</style>
