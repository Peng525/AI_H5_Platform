<template>
  <div class="h-dvh flex flex-col bg-surface-container-low overflow-hidden">
    <ResultPageHeader
      :title="projectTitle"
      :project-id="effectiveProjectId"
      :theme-drawer-open="themeDrawerOpen"
      @update:title="projectTitle = $event"
      @save-title="saveProjectTitle"
      @present="goPreview"
      @open-theme="themeDrawerOpen = !themeDrawerOpen"
      @back-to-review="goReviewFromHeader"
    />

    <div
      v-if="generateError"
      class="shrink-0 px-4 py-3 bg-red-50 border-b border-red-200 text-sm text-red-800 flex items-center justify-between gap-3 flex-wrap"
    >
      <span class="min-w-0">生成失败：{{ displayGenerateError }}</span>
      <div class="flex items-center gap-3 shrink-0">
        <button
          v-if="isPendingRoute && canRetryGenerate"
          type="button"
          class="text-xs font-medium underline"
          @click="retryPendingGeneration"
        >
          重试
        </button>
        <button type="button" class="text-xs font-medium underline" @click="goReview">返回编辑</button>
      </div>
    </div>

    <div
      v-if="pageLoadError && !isPendingRoute"
      class="shrink-0 px-4 py-2 bg-red-50 border-b border-red-200 text-sm text-red-800 flex items-center justify-between gap-3"
    >
      <span>{{ pageLoadError }}</span>
      <button type="button" class="text-xs font-medium underline shrink-0" @click="retryLoad">重试</button>
    </div>

    <div
      v-else-if="showEmptySlidesBanner"
      class="shrink-0 px-4 py-2 bg-amber-50 border-b border-amber-200 text-sm text-amber-900"
    >
      项目已加载，但未包含任何幻灯片页面。请尝试「再生成一次」或返回检查生成是否完整成功。
    </div>

    <div
      v-if="workspaceError"
      class="shrink-0 px-4 py-2 bg-red-50 border-b border-red-200 text-sm text-red-800 flex items-center justify-between gap-3"
    >
      <span>编辑器加载失败：{{ workspaceError }}</span>
      <button type="button" class="text-xs font-medium underline shrink-0" @click="clearWorkspaceError">关闭</button>
    </div>

    <div class="flex-1 min-h-0 flex flex-col relative">
      <DeckGenerateOverlay
        :open="generatingDeck"
        :estimated-seconds="generateEstimatedSeconds"
      />

      <div
        v-if="showProjectLoading"
        class="absolute inset-0 z-20 flex items-center justify-center bg-surface-container-low/90"
      >
        <PageLoading message="加载项目中…" />
      </div>

      <DeckEditorWorkspace
        v-if="showWorkspace"
        ref="workspaceRef"
        class="flex-1 min-h-0 flex flex-col"
        :project-id="effectiveProjectId"
        :initial-project="initialProject"
        :theme-drawer-open="themeDrawerOpen"
        layout-mode="result"
        :auto-reveal-on-load="autoRevealOnLoad"
        @project-loaded="onProjectLoaded"
        @project-load-error="onProjectLoadError"
        @reveal-complete="isRevealing = false"
        @close-theme-drawer="themeDrawerOpen = false"
      />
    </div>

    <ResultPageFooter
      v-if="showFooter"
      :message="footerMessage"
      :error="footerError"
      @save="onSave"
      @regenerate="regenerate"
    />
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../../api/client'
import DeckEditorWorkspace from '../../components/DeckEditorWorkspace.vue'
import ResultPageHeader from '../../components/create/ResultPageHeader.vue'
import ResultPageFooter from '../../components/create/ResultPageFooter.vue'
import DeckGenerateOverlay from '../../components/create/DeckGenerateOverlay.vue'
import PageLoading from '../../components/PageLoading.vue'
import { useToast } from '../../composables/useToast.js'
import { useQuota } from '../../composables/useQuota.js'
import {
  applyProjectSettingsLocal,
  clearGenerateJob,
  consumeShouldRevealDeck,
  grantGenerateResultAccess,
  loadDraft,
  loadGenerateJob,
  markReturnToResult,
  markShouldRevealDeck,
  PENDING_RESULT_PUBLIC_ID,
} from '../../composables/useAiCreateDraft.js'
import {
  copyEvaluationBundleMarkdown,
  downloadEvaluationBundle,
} from '../../composables/useEvaluationBundle.js'

const route = useRoute()
const router = useRouter()
const { success: toastSuccess } = useToast()
const { refreshQuota } = useQuota()

const workspaceRef = ref(null)
const loadedProject = ref(null)
const routePublicId = computed(() => String(route.params.publicId || ''))
const isPendingRoute = computed(() => routePublicId.value === PENDING_RESULT_PUBLIC_ID)
const effectiveProjectId = computed(() =>
  isPendingRoute.value ? PENDING_RESULT_PUBLIC_ID : routePublicId.value
)

const projectTitle = ref('')
const footerMessage = ref('')
const footerError = ref(false)
const loadFailed = ref(false)
const pageLoading = ref(true)
const pageLoadError = ref('')
const workspaceError = ref('')
const generatingDeck = ref(false)
const generateError = ref('')
const generateEstimatedSeconds = ref(48)
const autoRevealOnLoad = ref(false)
const isRevealing = ref(false)
const initialProject = ref(null)
const themeDrawerOpen = ref(false)

let titleTimer = null
let generationStarted = false

function normalizeGenerateError(message) {
  const raw = String(message || '未知错误').trim()
  return raw.replace(/^生成失败[：:]\s*/u, '') || '未知错误'
}

const displayGenerateError = computed(() => normalizeGenerateError(generateError.value))

const canRetryGenerate = computed(() => !!loadGenerateJob()?.body)

function formatCaughtError(err) {
  if (err == null) return '未知错误（请打开浏览器控制台查看详情）'
  if (typeof err === 'string') return err.trim() || '未知错误（请打开浏览器控制台查看详情）'
  const msg = err.message ?? err.detail ?? err.statusText
  if (msg && String(msg).trim()) return String(msg).trim()
  if (err.name && err.name !== 'Error') return `${err.name}：请求异常，请稍后重试`
  try {
    const serialized = JSON.stringify(err)
    if (serialized && serialized !== '{}') return serialized.slice(0, 300)
  } catch {
    /* ignore */
  }
  return '未知错误（请打开浏览器控制台查看详情）'
}

const project = computed(() => loadedProject.value)
const showWorkspace = computed(() => !isPendingRoute.value && !generatingDeck.value && !generateError.value)
const showProjectLoading = computed(
  () => showWorkspace.value && pageLoading.value && !generatingDeck.value && !loadedProject.value
)
const showFooter = computed(
  () => loadedProject.value && !loadFailed.value && !pageLoadError.value && !generatingDeck.value && !isRevealing.value
)
const showEmptySlidesBanner = computed(
  () =>
    loadedProject.value &&
    !pageLoading.value &&
    !pageLoadError.value &&
    !generatingDeck.value &&
    slideCount.value === 0
)

const slideCount = computed(() => project.value?.slides?.length || 0)

function clearWorkspaceError() {
  workspaceError.value = ''
}

function goReview() {
  clearGenerateJob()
  router.push('/create/generate/review')
}

function goReviewFromHeader() {
  if (!isPendingRoute.value) {
    markReturnToResult(routePublicId.value)
  }
  router.push('/create/generate/review')
}

async function runPendingGeneration() {
  if (generationStarted) return
  const job = loadGenerateJob()
  if (!job?.body) {
    generateError.value = '未找到生成任务，请返回编辑页重试'
    return
  }
  const topic = String(job.body.topic || '').trim()
  if (topic.length < 2) {
    generateError.value = '主题过短或为空，请返回编辑页填写主题（逐页模式可用第一页内容作为主题）'
    return
  }
  generationStarted = true
  generatingDeck.value = true
  generateError.value = ''
  generateEstimatedSeconds.value = job.estimatedSeconds || 48
  pageLoading.value = false
  try {
    const created = await api.generateAiDeck(job.body)
    if (!created?.public_id) {
      throw new Error('服务器未返回项目 ID，请稍后重试')
    }
    clearGenerateJob()
    grantGenerateResultAccess(created.public_id)
    applyProjectSettingsLocal(created.public_id, created.settings || {})
    initialProject.value = created
    syncFromProject(created)
    pageLoading.value = false
    pageLoadError.value = ''
    projectTitle.value = created.title?.trim() || ''
    markShouldRevealDeck()
    autoRevealOnLoad.value = true
    isRevealing.value = true
    await router.replace(`/create/generate/result/${created.public_id}`)
    refreshQuota().catch(() => {})
  } catch (e) {
    console.error('[AiGenerateResult] generateAiDeck failed', e)
    generateError.value = formatCaughtError(e)
    generationStarted = false
  } finally {
    generatingDeck.value = false
  }
}

function retryPendingGeneration() {
  generationStarted = false
  runPendingGeneration()
}

function syncFromProject(p) {
  if (!p) return
  loadFailed.value = false
  loadedProject.value = p
  projectTitle.value = p.title?.trim() || ''
  applyProjectSettingsLocal(p.public_id || routePublicId.value, p.settings || {})
}

function onProjectLoaded(p) {
  pageLoadError.value = ''
  pageLoading.value = false
  initialProject.value = null
  syncFromProject(p)
  if (autoRevealOnLoad.value) {
    isRevealing.value = true
  }
}

function onProjectLoadError(err) {
  loadFailed.value = true
  pageLoading.value = false
  initialProject.value = null
  pageLoadError.value = err || '加载失败'
  console.error('[AiGenerateResult] project load failed', routePublicId.value, err)
  footerError.value = true
  footerMessage.value = pageLoadError.value
}

async function fetchProjectForHeader() {
  const id = routePublicId.value
  if (isPendingRoute.value) return
  pageLoading.value = true
  pageLoadError.value = ''
  try {
    const p = await api.getProject(id)
    syncFromProject(p)
  } catch (e) {
    loadFailed.value = true
    pageLoadError.value = e.message || '加载失败'
    console.error('[AiGenerateResult] fetchProjectForHeader failed', id, e)
    footerError.value = true
    footerMessage.value = pageLoadError.value
  } finally {
    pageLoading.value = false
  }
}

function retryLoad() {
  footerError.value = false
  footerMessage.value = ''
  fetchProjectForHeader()
  workspaceRef.value?.load?.()
}

function saveProjectTitle() {
  if (!project.value && !routePublicId.value) return
  if (titleTimer) clearTimeout(titleTimer)
  titleTimer = setTimeout(async () => {
    const title = projectTitle.value.trim() || '无标题'
    try {
      const updated = await api.updateProject(routePublicId.value, { title })
      if (loadedProject.value) loadedProject.value.title = updated.title
    } catch (e) {
      footerError.value = true
      footerMessage.value = e.message || '标题保存失败'
    }
  }, 400)
}

async function onSave() {
  footerError.value = false
  footerMessage.value = ''
  try {
    if (titleTimer) {
      clearTimeout(titleTimer)
      titleTimer = null
      const title = projectTitle.value.trim() || '无标题'
      await api.updateProject(routePublicId.value, { title })
    }
    await workspaceRef.value?.flushCanvasSave?.()
    const refreshed = await api.getProject(routePublicId.value)
    loadedProject.value = refreshed
    if (workspaceRef.value?.project) {
      Object.assign(workspaceRef.value.project, refreshed)
    }
    downloadEvaluationBundle(refreshed, loadDraft())
    try {
      await copyEvaluationBundleMarkdown(refreshed, loadDraft())
      toastSuccess('已保存并下载评估包，Markdown 已复制到剪贴板')
    } catch {
      toastSuccess('已保存并下载评估包')
    }
  } catch (e) {
    footerError.value = true
    footerMessage.value = e.message || '保存失败'
  }
}

function goPreview() {
  if (project.value) router.push(`/preview/${routePublicId.value}`)
}

function regenerate() {
  router.push('/create/generate/review')
}

function bootstrap() {
  workspaceError.value = ''
  if (isPendingRoute.value) {
    pageLoading.value = false
    runPendingGeneration()
    return
  }
  const pid = routePublicId.value
  const hasLocal =
    (loadedProject.value?.public_id === pid) ||
    (initialProject.value?.public_id === pid)
  if (hasLocal) {
    if (initialProject.value && loadedProject.value?.public_id !== pid) {
      syncFromProject(initialProject.value)
    }
    pageLoading.value = false
    pageLoadError.value = ''
    if (!autoRevealOnLoad.value) {
      autoRevealOnLoad.value = consumeShouldRevealDeck()
    }
    if (autoRevealOnLoad.value) isRevealing.value = true
    return
  }
  autoRevealOnLoad.value = consumeShouldRevealDeck()
  if (autoRevealOnLoad.value) isRevealing.value = true
  fetchProjectForHeader()
}

watch(
  routePublicId,
  (newId, oldId) => {
    if (oldId != null && newId === oldId) return
    const fromPending = oldId === PENDING_RESULT_PUBLIC_ID && newId !== PENDING_RESULT_PUBLIC_ID
    if (!fromPending) {
      loadedProject.value = null
      initialProject.value = null
      projectTitle.value = ''
    }
    if (oldId !== PENDING_RESULT_PUBLIC_ID || newId === PENDING_RESULT_PUBLIC_ID) {
      generationStarted = false
      if (newId === PENDING_RESULT_PUBLIC_ID || oldId == null) {
        generateError.value = ''
      }
    }
    bootstrap()
  },
  { immediate: true }
)
</script>
