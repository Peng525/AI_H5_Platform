<template>
  <div class="h-dvh flex flex-col bg-surface-container-low overflow-hidden">
    <ResultPageHeader
      :title="projectTitle"
      :project-id="projectId"
      @update:title="projectTitle = $event"
      @save-title="saveProjectTitle"
      @present="goPreview"
    >
      <template v-if="generationMeta" #meta>
        <div class="hidden xl:flex items-center gap-3 text-[11px] text-on-surface-variant mr-1">
          <span v-if="generationMeta.model">模型 {{ generationMeta.model }}</span>
          <span v-if="generationMeta.duration_ms != null">{{ formatDuration(generationMeta.duration_ms) }}</span>
          <span>{{ slideCount }} 页</span>
        </div>
      </template>
    </ResultPageHeader>

    <div
      v-if="generationMeta"
      class="xl:hidden shrink-0 px-4 py-1.5 flex flex-wrap gap-x-3 gap-y-0.5 text-[11px] text-on-surface-variant border-b border-outline-variant/60 bg-white"
    >
      <span v-if="generationMeta.model">模型 {{ generationMeta.model }}</span>
      <span v-if="generationMeta.duration_ms != null">耗时 {{ formatDuration(generationMeta.duration_ms) }}</span>
      <span v-if="generationMeta.channel">通道 {{ generationMeta.channel }}</span>
      <span>{{ slideCount }} 页</span>
    </div>

    <div
      v-if="pageLoadError"
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
      <div
        v-if="pageLoading"
        class="absolute inset-0 z-20 flex items-center justify-center bg-surface-container-low/90"
      >
        <PageLoading message="加载项目中…" />
      </div>

      <DeckEditorWorkspace
        ref="workspaceRef"
        class="flex-1 min-h-0 flex flex-col"
        :project-id="projectId"
        layout-mode="result"
        @project-loaded="onProjectLoaded"
        @project-load-error="onProjectLoadError"
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
import { computed, onErrorCaptured, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../../api/client'
import DeckEditorWorkspace from '../../components/DeckEditorWorkspace.vue'
import ResultPageHeader from '../../components/create/ResultPageHeader.vue'
import ResultPageFooter from '../../components/create/ResultPageFooter.vue'
import PageLoading from '../../components/PageLoading.vue'
import { useToast } from '../../composables/useToast.js'
import { applyProjectSettingsLocal, loadDraft } from '../../composables/useAiCreateDraft.js'
import {
  copyEvaluationBundleMarkdown,
  downloadEvaluationBundle,
} from '../../composables/useEvaluationBundle.js'

const route = useRoute()
const router = useRouter()
const { success: toastSuccess } = useToast()

const workspaceRef = ref(null)
const loadedProject = ref(null)
const projectId = computed(() => String(route.params.publicId || ''))
const projectTitle = ref('')
const footerMessage = ref('')
const footerError = ref(false)
const loadFailed = ref(false)
const pageLoading = ref(true)
const pageLoadError = ref('')
const workspaceError = ref('')

let titleTimer = null

const project = computed(() => loadedProject.value)
const showFooter = computed(() => loadedProject.value && !loadFailed.value && !pageLoadError.value)
const showEmptySlidesBanner = computed(
  () => loadedProject.value && !pageLoading.value && !pageLoadError.value && slideCount.value === 0
)

const generationMeta = computed(() => project.value?.generation_meta || null)
const slideCount = computed(() => project.value?.slides?.length || 0)

function clearWorkspaceError() {
  workspaceError.value = ''
}

onErrorCaptured((err) => {
  workspaceError.value = err?.message || String(err)
  return false
})

function syncFromProject(p) {
  if (!p) return
  loadFailed.value = false
  loadedProject.value = p
  projectTitle.value = p.title?.trim() || ''
  applyProjectSettingsLocal(p.id, p.settings || {})
}

function onProjectLoaded(p) {
  pageLoadError.value = ''
  pageLoading.value = false
  syncFromProject(p)
}

function onProjectLoadError(err) {
  loadFailed.value = true
  pageLoading.value = false
  pageLoadError.value = err || '加载失败'
  footerError.value = true
  footerMessage.value = pageLoadError.value
}

async function fetchProjectForHeader() {
  const id = projectId.value
  if (!Number.isFinite(id)) {
    pageLoading.value = false
    pageLoadError.value = '无效的项目 ID'
    loadFailed.value = true
    return
  }
  pageLoading.value = true
  pageLoadError.value = ''
  try {
    const p = await api.getProject(id)
    syncFromProject(p)
  } catch (e) {
    loadFailed.value = true
    pageLoadError.value = e.message || '加载失败'
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

function formatDuration(ms) {
  if (ms < 1000) return `${ms} ms`
  return `${(ms / 1000).toFixed(1)} 秒`
}

function saveProjectTitle() {
  if (!project.value) return
  if (titleTimer) clearTimeout(titleTimer)
  titleTimer = setTimeout(async () => {
    const title = projectTitle.value.trim() || '无标题'
    try {
      const updated = await api.updateProject(projectId.value, { title })
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
      await api.updateProject(projectId.value, { title })
    }
    await workspaceRef.value?.flushCanvasSave?.()
    const refreshed = await api.getProject(projectId.value)
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
  if (project.value) router.push(`/preview/${projectId.value}`)
}

function regenerate() {
  router.push('/create/generate/review')
}

onMounted(() => {
  fetchProjectForHeader()
})

watch(projectId, () => {
  loadedProject.value = null
  projectTitle.value = ''
  fetchProjectForHeader()
})
</script>
