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
      @save-pdf="onSavePdf"
      @save-pptx="onSavePptx"
    />

    <Teleport to="body">
      <Transition name="fade">
        <div
          v-if="generateError"
          class="fixed inset-0 z-[110] flex items-center justify-center bg-black/35 px-4 py-6"
          role="presentation"
        >
          <div
            class="w-full max-w-[28rem] overflow-hidden rounded-xl border border-red-100 bg-white shadow-elevated"
            role="dialog"
            aria-modal="true"
            aria-labelledby="generate-error-title"
            aria-describedby="generate-error-message"
          >
            <div class="p-6">
              <div class="flex items-start gap-3">
                <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-red-50 text-red-600">
                  <span class="material-symbols-outlined text-[24px]">error</span>
                </div>
                <div class="min-w-0">
                  <h2 id="generate-error-title" class="text-base font-semibold text-on-surface">
                    生成失败
                  </h2>
                  <p
                    id="generate-error-message"
                    class="mt-2 max-h-40 overflow-y-auto break-words text-sm leading-6 text-on-surface-variant"
                  >
                    {{ displayGenerateError }}
                  </p>
                </div>
              </div>
            </div>
            <div class="flex flex-col-reverse gap-2 border-t border-outline-variant bg-surface-container-low px-6 py-4 sm:flex-row sm:justify-end">
              <button
                type="button"
                class="rounded-lg border border-outline-variant bg-white px-4 py-2 text-sm font-medium text-on-surface hover:bg-surface-container-high"
                @click="goReview"
              >
                返回编辑
              </button>
              <button
                v-if="isPendingRoute && canRetryGenerate"
                type="button"
                class="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary/90"
                @click="retryPendingGeneration"
              >
                重试
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

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
      <!-- _pending 阶段：纯转圈等待 API 返回 -->
      <div
        v-if="isPendingRoute"
        class="flex-1 flex flex-col items-center justify-center gap-4 bg-surface-container-low"
      >
        <div class="w-14 h-14 border-4 border-primary/20 border-t-primary rounded-full animate-spin" />
        <p class="text-base text-on-surface-variant font-medium">AI 正在生成演示内容…</p>
        <p class="text-xs text-on-surface-variant/50">预计 {{ generateEstimatedSeconds }} 秒</p>
      </div>

      <!-- 工作区 -->
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
        @reveal-complete="onRevealComplete"
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
import { computed, onActivated, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../../api/client'
import DeckEditorWorkspace from '../../components/DeckEditorWorkspace.vue'
import ResultPageHeader from '../../components/create/ResultPageHeader.vue'
import ResultPageFooter from '../../components/create/ResultPageFooter.vue'
import { useToast } from '../../composables/useToast.js'
import { useQuota } from '../../composables/useQuota.js'
import {
  applyProjectSettingsLocal,
  clearGenerateJob,
  clearPendingReveal,
  consumeShouldRevealDeck,
  grantGenerateResultAccess,
  isDeckRevealed,
  loadDraft,
  loadGenerateJob,
  markDeckRevealed,
  markReturnToResult,
  markShouldRevealDeck,
  PENDING_RESULT_PUBLIC_ID,
  shouldAutoRevealDeck,
} from '../../composables/useAiCreateDraft.js'
import {
  copyEvaluationBundleMarkdown,
  downloadEvaluationBundle,
} from '../../composables/useEvaluationBundle.js'
import {
  estimatePremiumDeckRange,
  estimatePremiumDeckSeconds,
} from '../../utils/deckGenerateEstimate.js'
import { exportPdf, exportPptx } from '../../utils/exportDeck.js'

defineOptions({ name: 'AiGenerateResult' })

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
const premiumJob = ref(null)
const premiumPolling = ref(false)

let titleTimer = null
let premiumPollTimer = null
let generationStarted = false

const PREMIUM_POLL_MS = 3000

function normalizeGenerateError(message) {
  const raw = String(message || '未知错误').trim()
  return raw.replace(/^生成失败[：:]\s*/u, '') || '未知错误'
}

const displayGenerateError = computed(() => normalizeGenerateError(generateError.value))

const canRetryGenerate = computed(() => !!loadGenerateJob()?.body)

const showGenerateOverlay = computed(() => premiumPolling.value)

const overlayTitle = computed(() =>
  premiumPolling.value ? '正在生成高质量演示' : '加载中…',
)

const overlayStageLabel = computed(() => {
  if (!premiumPolling.value) return ''
  return premiumJob.value?.stage_label
    || premiumJob.value?.hint
    || 'AI 正在根据您的提示词创建演示，请稍候…'
})

const overlayProgress = computed(() => {
  if (!premiumPolling.value) return null
  const p = premiumJob.value?.progress
  return typeof p === 'number' ? p : 0
})

const overlayFooterHint = computed(() => {
  if (premiumPolling.value && premiumJob.value?.total_pages) {
    return `共 ${premiumJob.value.total_pages} 页 · 完成后将自动进入编辑器`
  }
  return '生成完成后将开始绘制页面'
})

function isPremiumJob(job) {
  return job?.generationMode === 'premium' || !!job?.body?.ppt_template_id
}

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
const showWorkspace = computed(() =>
  !isPendingRoute.value && !pageLoading.value && !loadFailed.value && !generateError.value
)
const showFooter = computed(
  () => loadedProject.value && !loadFailed.value && !pageLoadError.value && !generatingDeck.value
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

function stopPremiumPolling() {
  if (premiumPollTimer) {
    clearInterval(premiumPollTimer)
    premiumPollTimer = null
  }
  premiumPolling.value = false
}

async function handlePremiumCompleted(job) {
  const publicId = job?.project_public_id
  if (!publicId) {
    throw new Error('任务已完成但未返回项目 ID')
  }
  stopPremiumPolling()
  premiumJob.value = null
  generatingDeck.value = false
  grantGenerateResultAccess(publicId)
  projectTitle.value = String(job.topic || '').trim().slice(0, 80) || '高质量演示'
  markShouldRevealDeck(publicId)
  autoRevealOnLoad.value = true
  isRevealing.value = true
  pageLoading.value = true
  await router.replace(`/create/generate/result/${publicId}`)
  refreshQuota().catch(() => {})
}

async function pollPremiumJobOnce(jobId) {
  const job = await api.getPremiumDeckJob(jobId)
  premiumJob.value = job
  if (job.status === 'completed' && job.project_public_id) {
    await handlePremiumCompleted(job)
    return
  }
  if (job.status === 'failed') {
    stopPremiumPolling()
    generatingDeck.value = false
    generationStarted = false
    generateError.value = job.error || '高质量演示生成失败'
    premiumJob.value = null
  }
}

function startPremiumPolling(jobId) {
  stopPremiumPolling()
  premiumPolling.value = true
  pollPremiumJobOnce(jobId).catch((e) => {
    console.error('[AiGenerateResult] premium poll failed', e)
    stopPremiumPolling()
    generatingDeck.value = false
    generationStarted = false
    generateError.value = formatCaughtError(e)
    premiumJob.value = null
  })
  premiumPollTimer = setInterval(() => {
    pollPremiumJobOnce(jobId).catch((e) => {
      console.error('[AiGenerateResult] premium poll failed', e)
    })
  }, PREMIUM_POLL_MS)
}

function clearResultTransientState() {
  generateError.value = ''
  pageLoadError.value = ''
  footerError.value = false
  footerMessage.value = ''
  workspaceError.value = ''
}

function goReview() {
  clearResultTransientState()
  stopPremiumPolling()
  premiumJob.value = null
  clearGenerateJob()
  router.replace('/create/generate/review')
}

function goReviewFromHeader() {
  clearResultTransientState()
  if (!isPendingRoute.value) {
    markReturnToResult(routePublicId.value)
  }
  router.replace('/create/generate/review')
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
    if (isPremiumJob(job) && !job.body.strict_template_mode) {
      const result = await api.submitPremiumDeckJob(job.body)
      clearGenerateJob()
      premiumJob.value = result
      projectTitle.value = String(job.body.topic || '').trim().slice(0, 80) || '高质量演示'
      generateEstimatedSeconds.value = estimatePremiumDeckRange(job.body.page_count).typicalSeconds
      startPremiumPolling(result.job_id)
      refreshQuota().catch(() => {})
      return
    }
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
    loadFailed.value = false
    workspaceError.value = ''
    projectTitle.value = created.title?.trim() || ''
    markShouldRevealDeck(created.public_id)
    autoRevealOnLoad.value = true
    isRevealing.value = true
    await router.replace(`/create/generate/result/${created.public_id}`)
    refreshQuota().catch(() => {})
  } catch (e) {
    console.error('[AiGenerateResult] generateAiDeck failed', e)
    generateError.value = formatCaughtError(e)
    generationStarted = false
  } finally {
    if (!premiumPolling.value) {
      generatingDeck.value = false
    }
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
  footerError.value = false
  footerMessage.value = ''
  syncFromProject(p)
  if (autoRevealOnLoad.value) {
    isRevealing.value = true
  }
}

function onProjectLoadError(err) {
  // _pending 占位ID 的加载失败是预期的，不显示错误
  if (isPendingRoute.value) return
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
    footerError.value = false
    footerMessage.value = ''
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
  if (project.value) {
    router.push({
      path: `/preview/${routePublicId.value}`,
      query: { returnTo: `/create/generate/result/${routePublicId.value}` },
    })
  }
}

async function onSavePdf() {
  if (!loadedProject.value || isPendingRoute.value) return
  toastSuccess('正在导出 PDF…')
  try {
    await exportPdf(loadedProject.value)
    toastSuccess('PDF 已导出')
  } catch (e) {
    toastSuccess('PDF 导出失败：' + (e.message || '未知错误'))
  }
}

async function onSavePptx() {
  if (!loadedProject.value || isPendingRoute.value) return
  toastSuccess('正在导出 PPTX…')
  try {
    await exportPptx(loadedProject.value)
    toastSuccess('PPTX 已导出')
  } catch (e) {
    toastSuccess('PPTX 导出失败：' + (e.message || '未知错误'))
  }
}

function regenerate() {
  if (!isPendingRoute.value) {
    markReturnToResult(routePublicId.value)
  }
  router.push('/create/generate/review')
}

function onRevealComplete() {
  if (!isPendingRoute.value) {
    markDeckRevealed(routePublicId.value)
  }
  requestAnimationFrame(() => {
    isRevealing.value = false
  })
}

function applyAutoRevealForProject(pid) {
  if (isDeckRevealed(pid)) {
    autoRevealOnLoad.value = false
    isRevealing.value = false
    return
  }
  if (!autoRevealOnLoad.value) {
    autoRevealOnLoad.value = shouldAutoRevealDeck(pid)
  } else {
    clearPendingReveal(pid)
  }
  if (autoRevealOnLoad.value) isRevealing.value = true
}

function bootstrap() {
  workspaceError.value = ''

  if (isPendingRoute.value) {
    // 结果页刚进入，API 还未调用 → 发起生成
    pageLoading.value = false
    runPendingGeneration()
    return
  }

  // 已有真实 projectId → 常规加载
  const pid = routePublicId.value
  if (!pid) return
  applyAutoRevealForProject(pid)
  pageLoading.value = true
  pageLoadError.value = ''
}

onActivated(() => {
  if (isPendingRoute.value) return
  const pid = routePublicId.value
  if (loadedProject.value?.public_id === pid) {
    pageLoading.value = false
    autoRevealOnLoad.value = false
    isRevealing.value = false
    if (!pageLoadError.value) {
      footerError.value = false
      footerMessage.value = ''
    }
    if (isDeckRevealed(pid) && workspaceRef.value?.reveal?.isRevealing?.value) {
      workspaceRef.value.reveal.skipReveal()
    }
  }
})

onUnmounted(() => {
  stopPremiumPolling()
  if (titleTimer) clearTimeout(titleTimer)
})

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

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.18s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
