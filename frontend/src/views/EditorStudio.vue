<template>
  <div class="h-screen flex flex-col bg-background overflow-hidden">
    <EditorTopBar
      :project-id="projectId"
      :hide-publish="!!isAdminEditorMode"
      :nav-mode="isAdminEditorMode ? 'admin' : 'user'"
    >
      <template v-if="adminLayoutId" #actions>
        <router-link
          to="/admin/layouts"
          class="hidden lg:inline-flex items-center px-3 py-1.5 rounded-lg border border-outline-variant text-xs sm:text-sm hover:bg-surface-container-high whitespace-nowrap"
        >
          返回版式管理
        </router-link>
        <button
          type="button"
          class="hidden lg:inline-flex px-3 py-1.5 rounded-lg bg-secondary text-on-secondary text-xs sm:text-sm font-medium whitespace-nowrap"
          @click="openLayoutSave"
        >
          保存版式
        </button>
        <div ref="adminLayoutActionsRef" class="relative lg:hidden">
          <button
            type="button"
            class="px-2.5 py-1.5 rounded-lg border border-outline-variant text-xs hover:bg-surface-container-high"
            aria-label="更多操作"
            @click="adminLayoutActionsOpen = !adminLayoutActionsOpen"
          >
            <span class="material-symbols-outlined text-[20px] leading-none">more_vert</span>
          </button>
          <div
            v-if="adminLayoutActionsOpen"
            class="absolute right-0 top-full mt-1 w-44 bg-white border border-outline-variant rounded-lg shadow-lg py-1 z-50 text-sm"
          >
            <router-link
              to="/admin/layouts"
              class="block px-3 py-2 hover:bg-surface-container-low"
              @click="adminLayoutActionsOpen = false"
            >
              返回版式管理
            </router-link>
            <button
              type="button"
              class="w-full text-left px-3 py-2 hover:bg-surface-container-low"
              @click="adminLayoutActionsOpen = false; openLayoutSave()"
            >
              保存版式
            </button>
          </div>
        </div>
      </template>
      <template v-else-if="adminPresetId" #actions>
        <!-- 大屏：完整按钮 -->
        <router-link
          to="/admin/templates"
          class="hidden lg:inline-flex items-center px-3 py-1.5 rounded-lg border border-outline-variant text-xs sm:text-sm hover:bg-surface-container-high whitespace-nowrap"
        >
          返回模板管理
        </router-link>
        <label class="hidden lg:inline-flex items-center px-3 py-1.5 rounded-lg border border-outline-variant text-xs sm:text-sm hover:bg-surface-container-high cursor-pointer whitespace-nowrap">
          从 PPT 导入
          <input type="file" accept=".pptx" class="hidden" :disabled="pptImporting" @change="onAdminPptxImport" />
        </label>
        <button
          type="button"
          class="hidden lg:inline-flex px-3 py-1.5 rounded-lg bg-primary text-on-primary text-xs sm:text-sm font-medium whitespace-nowrap disabled:opacity-50"
          :disabled="pptImporting"
          @click="openPresetSave"
        >
          保存为预设
        </button>
        <!-- 小屏：更多菜单 -->
        <div ref="adminActionsRef" class="relative lg:hidden">
          <button
            type="button"
            class="px-2.5 py-1.5 rounded-lg border border-outline-variant text-xs hover:bg-surface-container-high"
            aria-label="更多操作"
            @click="adminActionsOpen = !adminActionsOpen"
          >
            <span class="material-symbols-outlined text-[20px] leading-none">more_vert</span>
          </button>
          <div
            v-if="adminActionsOpen"
            class="absolute right-0 top-full mt-1 w-44 bg-white border border-outline-variant rounded-lg shadow-lg py-1 z-50 text-sm"
          >
            <router-link
              to="/admin/templates"
              class="block px-3 py-2 hover:bg-surface-container-low"
              @click="adminActionsOpen = false"
            >
              返回模板管理
            </router-link>
            <label class="block px-3 py-2 hover:bg-surface-container-low cursor-pointer">
              从 PPT 导入
              <input type="file" accept=".pptx" class="hidden" :disabled="pptImporting" @change="onAdminPptxMenuImport" />
            </label>
            <button
              type="button"
              class="w-full text-left px-3 py-2 hover:bg-surface-container-low disabled:opacity-50"
              :disabled="pptImporting"
              @click="adminActionsOpen = false; openPresetSave()"
            >
              保存为预设
            </button>
          </div>
        </div>
      </template>
    </EditorTopBar>
    <div v-if="projectLoading" class="flex-1 flex items-center justify-center min-h-0">
      <PageLoading message="加载项目中…" />
    </div>
    <div v-else-if="loadError" class="flex-1 flex items-center justify-center p-6">
      <EmptyState
        icon="error"
        title="无法加载项目"
        :description="loadError"
        action-label="重试"
        @action="load"
      />
    </div>
    <div
      v-else
      class="editor-workspace flex flex-1 min-h-0 min-w-0 relative"
      :class="isAdminEditorMode ? 'editor-workspace--admin-responsive overflow-hidden' : 'overflow-x-auto overflow-y-hidden'"
    >
      <template v-if="isAdminEditorMode && !isWideLayout">
        <button
          type="button"
          class="admin-drawer-fab admin-drawer-fab--left"
          @click="aiDrawerOpen = false; toolboxDrawerOpen = true"
        >
          <span class="material-symbols-outlined text-[18px]">widgets</span>
          工具箱
        </button>
        <button
          type="button"
          class="admin-drawer-fab admin-drawer-fab--right"
          @click="toolboxDrawerOpen = false; aiDrawerOpen = true"
        >
          <span class="material-symbols-outlined text-[18px]">auto_awesome</span>
          AI
        </button>
        <div
          v-if="toolboxDrawerOpen || aiDrawerOpen"
          class="fixed inset-0 top-14 bg-black/30 z-[55]"
          @click="closeAdminDrawers"
        />
      </template>
      <div
        v-if="showEditorCoach"
        class="absolute top-3 left-1/2 -translate-x-1/2 z-[70] max-w-sm w-[calc(100%-2rem)] bg-white border border-outline-variant/60 rounded-xl px-4 py-3.5 shadow-md"
      >
        <div class="flex items-start justify-between gap-3 mb-3">
          <p class="text-sm font-medium text-on-surface">首次使用 AI 配图</p>
          <button
            type="button"
            class="shrink-0 text-on-surface-variant hover:text-on-surface material-symbols-outlined text-lg leading-none"
            aria-label="关闭"
            @click="dismissEditorCoach"
          >
            close
          </button>
        </div>
        <ol class="space-y-2 text-xs text-on-surface-variant">
          <li class="flex items-center gap-2.5">
            <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary text-[11px] font-medium">1</span>
            <span>选择生图分辨率</span>
          </li>
          <li class="flex items-center gap-2.5">
            <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary text-[11px] font-medium">2</span>
            <span>填写画面描述并生图</span>
          </li>
          <li class="flex items-center gap-2.5">
            <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary text-[11px] font-medium">3</span>
            <span>预览后选择添加方式</span>
          </li>
        </ol>
        <button
          type="button"
          class="mt-3 w-full py-1.5 text-xs font-medium text-primary hover:bg-primary/5 rounded-lg transition-colors"
          @click="dismissEditorCoach"
        >
          知道了
        </button>
      </div>
      <div :class="toolboxPanelClass">
      <EditorToolbox
        :slides="project?.slides || []"
        :current-id="current?.id"
        :current-slide="current"
        :scroll-effect="settings.scrollEffect"
        :canvas-background="canvasBackground"
        :project-settings="settings"
        :project-id="projectId"
        :viewport="viewport"
        :live-slide-id="current?.id ?? null"
        :live-elements="elements"
        :primary-layouts="primaryLayoutItems"
        :more-layouts="moreLayoutItems"
        @select-slide="selectSlide"
        @add-slide="addSlide"
        @remove-slide="removeSlide"
        @save-slide="saveSlideFields"
        @sync-canvas="syncCanvasFromSlide"
        @add-material="addMaterial"
        @apply-layout="applyLayoutBlock"
        @canvas-bg-change="onCanvasBgChange"
        @scroll-change="setScrollEffect"
        @preview-animation="onPreviewAnimation"
        @open-help="shortcutsHelpOpen = true"
        @bgm-change="onBgmChange"
        @open-dialogue-generator="openDialogueGenerator"
        @open-wordcloud-editor="wordCloudOpen = true"
      />
      </div>

      <EditorPhoneCanvas
        class="editor-canvas-panel"
        :elements="elements"
        :selected-ids="selectedIds"
        :slide="current"
        :slide-index="slideIndex"
        :viewport="viewport"
        :viewport-id="settings.viewportId"
        :preview-animation="previewAnimation"
        :preview-animation-tick="previewAnimationTick"
        :canvas-background="canvasBackground"
        :theme-id="settings.themeId || 'zjy-minimal'"
        :show-dialogue-preview="showDialoguePreview"
        :show-bgm-player="bgmActive"
        :bgm-muted="bgmMuted"
        :bgm-spinning="bgmSpinning"
        @toggle-bgm-mute="toggleBgmMute"
        @select="onSelectElement"
        @deselect="clearSelection"
        @marquee-select="onMarqueeSelect"
        @update-element="updateElement"
        @add-text="addElement('text')"
        @add-shape="addElement('shape')"
        @add-image="addImagePlaceholder"
        @style-change="onStyleChange"
        @duplicate="onDuplicate"
        @delete-selected="onDeleteSelected"
        @bring-front="onBringFront"
        @send-back="onSendBack"
        @bring-forward="onBringForward"
        @send-backward="onSendBackward"
        @center-element="onCenterElement"
        @image-fit="onImageFit"
        @image-crop="onImageCrop"
        @viewport-change="setViewport"
        @undo="undo"
        @redo="redo"
        :can-undo="canUndo()"
        :can-redo="canRedo()"
        @batch-start="onBatchStart"
        @batch-end="onBatchEnd"
        @move-delta="onMoveDelta"
        @edit-wordcloud="onEditWordCloud"
        @edit-chart-stack="onEditChartStack"
        @update:show-dialogue-preview="showDialoguePreview = $event"
      />

      <div :class="aiPanelClass">
      <AiPanel
        ref="aiPanelRef"
        :image-loading="imageLoading"
        :quota-remaining="quota.remaining"
        :quota-total="quota.total"
        :canvas-viewport-id="settings.viewportId"
        @generate-image="onGenerateImage"
        @add-image-to-page="onAddImageToPage"
      />
      </div>
    </div>

    <EditorShortcutsHelp v-model:open="shortcutsHelpOpen" />
    <DialogueGeneratorModal
      :open="dialogueGeneratorOpen"
      :initial-script="current?.chat_script"
      @close="dialogueGeneratorOpen = false"
      @insert="onInsertDialogue"
    />
    <WordCloudEditorModal
      :open="wordCloudOpen"
      :theme-id="settings.themeId || 'zjy-minimal'"
      :initial-content="wordCloudEditContent"
      @close="wordCloudOpen = false; wordCloudEditContent = null"
      @insert-vector="onInsertWordCloud"
      @insert-image="onInsertWordCloudImage"
    />
    <ChartStackEditorModal
      :open="chartStackOpen"
      :initial-content="chartStackEditContent"
      @close="chartStackOpen = false; chartStackEditContent = null"
      @save="onSaveChartStack"
    />
    <ImageCropModal
      :open="cropModalOpen"
      :image-url="cropImageUrl"
      :initial-crop="cropInitial"
      @close="cropModalOpen = false"
      @confirm="onCropConfirm"
      @reset="onCropReset"
    />
    <ConfirmDialog
      :open="!!deleteSlideConfirm"
      title="删除页面"
      message="确定删除该页面？此操作不可撤销。"
      confirm-text="删除"
      cancel-text="取消"
      danger
      @confirm="onDeleteSlideConfirm"
      @cancel="deleteSlideConfirm = null"
    />
    <AdminPresetSaveDialog
      :open="presetSaveOpen"
      :template-id="adminPresetId"
      :project-id="projectId"
      :initial="templateMeta"
      @close="presetSaveOpen = false"
      @saved="onPresetSaved"
    />
    <AdminLayoutSaveDialog
      :open="layoutSaveOpen"
      :layout-id="adminLayoutId"
      :project-id="projectId"
      :initial="layoutMeta"
      @close="layoutSaveOpen = false"
      @saved="onLayoutSaved"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { onBeforeRouteLeave, useRoute } from 'vue-router'
import { api } from '../api/client'
import { useAuth } from '../composables/useAuth'
import { registerCanvasFlush, unregisterCanvasFlush } from '../composables/useEditorCanvasSave'
import { useSlideCanvas } from '../composables/useSlideCanvas'
import { useProjectEditorSettings } from '../composables/useProjectEditorSettings'
import { useBgmPlayer } from '../composables/useBgmPlayer'
import AiPanel from '../components/AiPanel.vue'
import EditorPhoneCanvas from '../components/EditorPhoneCanvas.vue'
import EditorToolbox from '../components/EditorToolbox.vue'
import EditorTopBar from '../components/EditorTopBar.vue'
import EditorShortcutsHelp from '../components/EditorShortcutsHelp.vue'
import DialogueGeneratorModal from '../components/dialogue/DialogueGeneratorModal.vue'
import WordCloudEditorModal from '../components/wordcloud/WordCloudEditorModal.vue'
import ChartStackEditorModal from '../components/charts/ChartStackEditorModal.vue'
import ImageCropModal from '../components/ImageCropModal.vue'
import PageLoading from '../components/PageLoading.vue'
import EmptyState from '../components/EmptyState.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import AdminPresetSaveDialog from '../components/admin/AdminPresetSaveDialog.vue'
import AdminLayoutSaveDialog from '../components/admin/AdminLayoutSaveDialog.vue'
import { useToast } from '../composables/useToast.js'

const COACH_KEY = 'ai_h5_editor_coach_seen'
const { error: toastError, success: toastSuccess } = useToast()
import { buildBlock, getDefaultBlockBackground, resetLayoutBlockIds, resolveStoredLayoutElements } from '../constants/layoutBlocks.js'
import { useLayoutCatalog } from '../composables/useLayoutCatalog.js'
import { normalizeChatScript, serializeChatScript } from '../utils/chatScript.js'

const route = useRoute()
const { user } = useAuth()
const projectId = computed(() => route.params.id)
const adminPresetId = computed(() => (typeof route.query.adminPreset === 'string' ? route.query.adminPreset : ''))
const adminLayoutId = computed(() => (typeof route.query.adminLayout === 'string' ? route.query.adminLayout : ''))
const isAdminEditorMode = computed(() => !!(adminPresetId.value || adminLayoutId.value))
const isWideLayout = ref(true)
const toolboxDrawerOpen = ref(false)
const aiDrawerOpen = ref(false)
const adminActionsOpen = ref(false)
const adminLayoutActionsOpen = ref(false)
const adminActionsRef = ref(null)
const adminLayoutActionsRef = ref(null)

const toolboxPanelClass = computed(() => {
  if (!isAdminEditorMode.value || isWideLayout.value) return 'shrink-0 flex min-h-0'
  return toolboxDrawerOpen.value
    ? 'fixed left-0 top-14 bottom-0 z-[56] flex min-h-0 shadow-xl'
    : 'hidden shrink-0'
})

const aiPanelClass = computed(() => {
  if (!isAdminEditorMode.value || isWideLayout.value) return 'shrink-0 flex min-h-0'
  return aiDrawerOpen.value
    ? 'fixed right-0 top-14 bottom-0 z-[56] flex min-h-0 shadow-xl'
    : 'hidden shrink-0'
})

function closeAdminDrawers() {
  toolboxDrawerOpen.value = false
  aiDrawerOpen.value = false
}

function onAdminPptxMenuImport(e) {
  adminActionsOpen.value = false
  onAdminPptxImport(e)
}

function onAdminActionsClickOutside(e) {
  if (adminActionsRef.value && !adminActionsRef.value.contains(e.target)) {
    adminActionsOpen.value = false
  }
  if (adminLayoutActionsRef.value && !adminLayoutActionsRef.value.contains(e.target)) {
    adminLayoutActionsOpen.value = false
  }
}

let layoutMq = null
function onLayoutMqChange(e) {
  isWideLayout.value = e.matches
  if (e.matches) closeAdminDrawers()
}
const project = ref(null)
const current = ref(null)
const imageLoading = ref(false)
const aiPanelRef = ref(null)
const quota = ref({ remaining: 5, total: 5 })
const previewAnimation = ref('')
const previewAnimationTick = ref(0)
const shortcutsHelpOpen = ref(false)
const dialogueGeneratorOpen = ref(false)
const wordCloudOpen = ref(false)
const wordCloudEditContent = ref(null)
const chartStackOpen = ref(false)
const chartStackEditContent = ref(null)
const showDialoguePreview = ref(false)
const cropModalOpen = ref(false)
const cropTargetId = ref(null)
const cropImageUrl = ref('')
const cropInitial = ref(null)
const projectLoading = ref(true)
const loadError = ref('')
const deleteSlideConfirm = ref(null)
const presetSaveOpen = ref(false)
const layoutSaveOpen = ref(false)
const pptImporting = ref(false)
const templateMeta = ref(null)
const layoutMeta = ref(null)
const showEditorCoach = ref(false)

const { settings, viewport, setViewport, setScrollEffect, getSlideBackground, setSlideBackground, applyFromServer, setBgm } = useProjectEditorSettings(projectId)

const layoutCatalog = useLayoutCatalog()
const primaryLayoutItems = computed(() => layoutCatalog.getPrimaryLayoutItems())
const moreLayoutItems = computed(() => layoutCatalog.getMoreLayoutItems())

const {
  active: bgmActive,
  muted: bgmMuted,
  playing: bgmPlaying,
  toggleMute: toggleBgmMute,
} = useBgmPlayer(settings)

const bgmSpinning = computed(() => bgmPlaying.value && !bgmMuted.value)

const canvasBackground = computed(() => getSlideBackground(current.value?.id))

const slideIdRef = computed(() => current.value?.id ?? null)
const {
  elements,
  selectedIds,
  selectedId,
  saveElements,
  loadElements,
  addElement,
  updateElement,
  removeElement,
  removeSelected,
  duplicateElement,
  duplicateSelected,
  copySelected,
  pasteClipboard,
  selectElement,
  selectElements,
  clearSelection,
  bringToFront,
  bringSelectedToFront,
  sendSelectedToBack,
  bringSelectedForward,
  sendSelectedBackward,
  syncFromSlide,
  replaceAllElements,
  appendLayoutElements,
  addImageFromAi,
  applyImageFitToSelected,
  flushCanvasSave,
  undo,
  redo,
  canUndo,
  canRedo,
  beginHistoryBatch,
  endHistoryBatch,
} = useSlideCanvas(projectId, slideIdRef)

const dragState = ref(null)
const pendingDragElementId = ref(null)

const slideIndex = computed(() => {
  if (!project.value?.slides || !current.value) return 0
  return project.value.slides.findIndex((s) => s.id === current.value.id)
})

async function loadTemplateMeta() {
  if (!adminPresetId.value) {
    templateMeta.value = null
    return
  }
  try {
    templateMeta.value = await api.getAdminTemplate(adminPresetId.value)
  } catch {
    templateMeta.value = null
  }
}

async function loadLayoutMeta() {
  if (!adminLayoutId.value) {
    layoutMeta.value = null
    return
  }
  try {
    layoutMeta.value = await api.getAdminLayout(adminLayoutId.value)
  } catch {
    layoutMeta.value = {
      id: adminLayoutId.value,
      label: adminLayoutId.value,
      icon: 'dashboard',
      group: 'custom',
      placement: 'more',
      sort_order: 100,
      enabled: true,
    }
  }
}

async function openLayoutSave() {
  await flushCanvasSave()
  await loadLayoutMeta()
  layoutSaveOpen.value = true
}

async function onLayoutSaved() {
  toastSuccess('版式已保存')
  await layoutCatalog.reload()
  await loadLayoutMeta()
}

async function openPresetSave() {
  await flushCanvasSave()
  presetSaveOpen.value = true
}

async function onPresetSaved() {
  toastSuccess('模板预设已保存')
  await loadTemplateMeta()
}

async function onAdminPptxImport(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file || !adminPresetId.value) return
  pptImporting.value = true
  try {
    await flushCanvasSave()
    const fd = new FormData()
    fd.append('file', file)
    fd.append('project_id', String(projectId.value))
    fd.append('device', templateMeta.value?.device || 'mobile')
    if (templateMeta.value?.title) fd.append('title', templateMeta.value.title)
    await api.importPptxToTemplateDraft(adminPresetId.value, fd)
    toastSuccess('PPT 已导入到当前草稿')
    await load()
  } catch (err) {
    toastError(err.message)
  } finally {
    pptImporting.value = false
  }
}

async function load() {
  projectLoading.value = true
  loadError.value = ''
  try {
    project.value = await api.getProject(Number(projectId.value))
    applyFromServer(project.value.settings)
    current.value = project.value.slides?.[0] || null
    showDialoguePreview.value = !!current.value?.chat_script?.enabled
    loadElements(current.value?.canvas_elements)
    if (current.value && !elements.value.length) syncFromSlide(current.value)
    const q = await api.getQuota()
    quota.value = { remaining: q.quota_remaining, total: q.quota_total }
  } catch (e) {
    loadError.value = e.message || '加载失败'
  } finally {
    projectLoading.value = false
  }
}

function dismissEditorCoach() {
  showEditorCoach.value = false
  localStorage.setItem(COACH_KEY, '1')
}

function onBgmChange(patch) {
  setBgm(patch)
}

onMounted(() => {
  registerCanvasFlush(flushCanvasSave)
  window.addEventListener('keydown', onKeyDown)
  document.addEventListener('click', onAdminActionsClickOutside)
  layoutMq = window.matchMedia('(min-width: 1024px)')
  isWideLayout.value = layoutMq.matches
  layoutMq.addEventListener('change', onLayoutMqChange)
  layoutCatalog.load()
  if (!isAdminEditorMode.value) {
    showEditorCoach.value = !localStorage.getItem(COACH_KEY)
  }
  loadTemplateMeta()
  loadLayoutMeta()
  load()
})
watch(() => route.query.adminPreset, loadTemplateMeta)
watch(() => route.query.adminLayout, loadLayoutMeta)
watch(() => route.params.id, load)
onBeforeRouteLeave(async () => {
  await flushCanvasSave()
})

function selectSlide(slide) {
  saveElements()
  current.value = slide
  loadElements(slide.canvas_elements)
  if (!elements.value.length) syncFromSlide(slide)
  showDialoguePreview.value = !!slide?.chat_script?.enabled
}

async function addSlide() {
  if (adminLayoutId.value) {
    toastError('版式编辑仅支持单页画布')
    return
  }
  saveElements()
  try {
    const slide = await api.addSlide(project.value.id, {
      title: '新页面',
      subtitle: '',
      bullets: [],
      layout: 'bullets',
      animation: 'fade',
    })
    project.value.slides.push(slide)
    finishNewSlide(slide)
  } catch (e) {
    toastError(e.message)
  }
}

function finishNewSlide(slide) {
  current.value = slide
  loadElements(slide.canvas_elements)
  if (!elements.value.length) syncFromSlide(slide)
}

function applyLayoutBlock(blockId, slideId = null, { mode = 'append' } = {}) {
  const sid = slideId ?? current.value?.id
  if (!sid) return
  if (slideId && slideId !== current.value?.id) {
    current.value = project.value.slides.find((s) => s.id === slideId) || current.value
    loadElements([])
  }
  resetLayoutBlockIds()
  const catalogItem = layoutCatalog.getCatalogBlock(blockId)
  const stored = resolveStoredLayoutElements(catalogItem, settings.value.viewportId)
  const els = stored ?? buildBlock(blockId, settings.value.viewportId, settings.value.themeId || 'zjy-minimal')
  if (mode === 'replace') {
    replaceAllElements(els)
    const bg =
      catalogItem?.canvas_background ||
      getDefaultBlockBackground(settings.value.themeId || 'zjy-minimal')
    setSlideBackground(sid, bg)
  } else {
    appendLayoutElements(els)
  }
}

async function removeSlide(slideId) {
  if (adminLayoutId.value) {
    toastError('版式编辑仅支持单页画布')
    return
  }
  if ((project.value.slides?.length || 0) <= 1) {
    toastError('至少保留一页')
    return
  }
  deleteSlideConfirm.value = slideId
}

async function onDeleteSlideConfirm() {
  const slideId = deleteSlideConfirm.value
  if (!slideId) return
  deleteSlideConfirm.value = null
  saveElements()
  try {
    await api.deleteSlide(project.value.id, slideId)
    localStorage.removeItem(`ai_h5_canvas_${project.value.id}_${slideId}`)
    project.value.slides = project.value.slides.filter((s) => s.id !== slideId)
    if (current.value?.id === slideId) {
      current.value = project.value.slides[0]
      loadElements()
    }
    toastSuccess('页面已删除')
  } catch (e) {
    toastError(e.message)
  }
}

async function saveSlideFields(fields) {
  if (!current.value) return
  try {
    const updated = await api.updateSlide(project.value.id, current.value.id, fields)
    const idx = project.value.slides.findIndex((s) => s.id === updated.id)
    if (idx >= 0) project.value.slides[idx] = updated
    current.value = {
      ...updated,
      chat_script: updated.chat_script ?? fields.chat_script ?? current.value.chat_script,
    }
  } catch (e) {
    toastError(e.message || '保存页面失败')
    console.error(e)
  }
}

function syncCanvasFromSlide() {
  if (!current.value) return
  elements.value = []
  syncFromSlide(current.value)
}

function addMaterial(item) {
  if (item.type === 'text') {
    addElement('text', {
      content: '在此输入文字',
      height: 56,
      style: {
        background: '#ffffff',
        border: '1px solid #c0c7d6',
        borderRadius: 2,
      },
    })
  } else if (item.type === 'shape') {
    addElement('shape', {
      style: { background: '#005daa', borderRadius: 0 },
      width: 120,
      height: 80,
    })
  } else if (item.type === 'table') {
    addElement('table', {
      style: {
        background: '#ffffff',
        headerBackground: '#005daa',
        headerColor: '#ffffff',
        borderColor: '#c0c7d6',
      },
    })
  } else if (item.type === 'icon') {
    addElement('icon', {
      content: item.icon || 'emoji_objects',
      style: {
        background: '#e8f0fe',
        color: '#005daa',
        borderRadius: 8,
      },
    })
  } else if (item.type === 'image') {
    addElement('image', {
      content: 'https://placehold.co/200x120/005daa/white?text=Image',
      width: 200,
      height: 120,
      style: { background: '#f0f0f0' },
    })
  } else if (item.type === 'chart') {
    addElement('chart', {
      style: { background: '#ffffff', chartColor: '#005daa' },
    })
  } else if (item.type === 'chartStack') {
    const vp = viewport.value
    addElement('chartStack', {
      x: Math.round((vp.width - 320) / 2),
      y: 80,
    })
  } else if (item.type === 'wordcloud') {
    wordCloudOpen.value = true
  }
}

function openDialogueGenerator() {
  dialogueGeneratorOpen.value = true
}

async function onInsertDialogue(script) {
  if (!current.value) return
  const serialized = serializeChatScript({ ...normalizeChatScript(script), enabled: true })
  const bg = serialized.style?.background || '#ededed'

  setSlideBackground(current.value.id, bg)
  replaceAllElements([])
  await flushCanvasSave()
  dialogueGeneratorOpen.value = false

  try {
    const updated = await api.updateSlide(project.value.id, current.value.id, {
      chat_script: serialized,
      layout: 'chat',
      title: current.value.title || '对话页',
      subtitle: '',
      bullets: [],
    })
    const idx = project.value.slides.findIndex((s) => s.id === updated.id)
    if (idx >= 0) project.value.slides[idx] = updated
    current.value = { ...updated, chat_script: serialized }
    showDialoguePreview.value = true
  } catch (e) {
    toastError(e.message || '插入对话失败，请重试')
    console.error(e)
  }
}

function onInsertWordCloud(content) {
  wordCloudOpen.value = false
  wordCloudEditContent.value = null
  if (selectedId.value) {
    const el = elements.value.find((e) => e.id === selectedId.value)
    if (el?.type === 'wordcloud') {
      updateElement(selectedId.value, { content })
      return
    }
  }
  const vp = viewport.value
  addElement('wordcloud', {
    x: Math.round((vp.width - 280) / 2),
    y: 80,
    width: 280,
    height: 200,
    content,
  })
}

function onEditWordCloud(el) {
  wordCloudEditContent.value = el.content
  wordCloudOpen.value = true
}

function onEditChartStack(el) {
  if (el?.content) {
    chartStackEditContent.value = el.content
  } else if (selectedId.value) {
    const selected = elements.value.find((e) => e.id === selectedId.value)
    chartStackEditContent.value = selected?.type === 'chartStack' ? selected.content : null
  } else {
    chartStackEditContent.value = null
  }
  chartStackOpen.value = true
}

function onSaveChartStack(content) {
  chartStackOpen.value = false
  const targetId = selectedId.value
  if (targetId) {
    const el = elements.value.find((e) => e.id === targetId)
    if (el?.type === 'chartStack') {
      updateElement(targetId, { content })
      chartStackEditContent.value = null
      return
    }
  }
  const vp = viewport.value
  addElement('chartStack', {
    x: Math.round((vp.width - 320) / 2),
    y: 80,
    content,
  })
  chartStackEditContent.value = null
}

function onInsertWordCloudImage(dataUrl) {
  wordCloudOpen.value = false
  const vp = viewport.value
  addElement('image', {
    x: Math.round((vp.width - 280) / 2),
    y: 80,
    width: 280,
    height: 200,
    content: dataUrl,
    style: { background: 'transparent', objectFit: 'contain' },
  })
}

function onCanvasBgChange(color) {
  if (current.value?.id) setSlideBackground(current.value.id, color)
}

function addImagePlaceholder() {
  addElement('image', {
    content: 'https://placehold.co/200x120/005daa/white?text=Image',
    width: 200,
    height: 120,
  })
}

function onStyleChange(patch) {
  if (!selectedId.value) return
  const el = elements.value.find((e) => e.id === selectedId.value)
  if (!el) return
  updateElement(selectedId.value, { style: { ...el.style, ...patch } })
}

function onDuplicate() {
  if (selectedIds.value.length > 1) duplicateSelected()
  else if (selectedId.value) duplicateElement(selectedId.value)
}

function onDeleteSelected() {
  if (selectedIds.value.length > 1) removeSelected()
  else if (selectedId.value) removeElement(selectedId.value)
}

function onBringFront() {
  if (selectedIds.value.length > 1) bringSelectedToFront()
  else if (selectedId.value) bringToFront(selectedId.value)
}

function onSendBack() {
  sendSelectedToBack()
}

function onBringForward() {
  bringSelectedForward()
}

function onSendBackward() {
  sendSelectedBackward()
}

function onCenterElement(axis) {
  if (!selectedId.value) return
  const el = elements.value.find((e) => e.id === selectedId.value)
  if (!el) return
  const vp = viewport.value
  const chrome = vp.device === 'mobile' ? 28 : 32
  const canvasH = vp.height - chrome
  const patch = {}
  if (axis === 'h' || axis === 'both') {
    patch.x = Math.max(0, Math.round((vp.width - el.width) / 2))
  }
  if (axis === 'v' || axis === 'both') {
    patch.y = Math.max(0, Math.round((canvasH - el.height) / 2))
  }
  updateElement(selectedId.value, patch)
}

function onSelectElement({ id, ctrlKey, shiftKey }) {
  if (ctrlKey) {
    selectElement(id, { toggle: true })
    return
  }
  if (shiftKey) {
    selectElement(id, { additive: true })
    return
  }
  if (!selectedIds.value.includes(id)) {
    selectElement(id)
  }
}

function onMarqueeSelect({ ids, additive }) {
  if (!ids.length && !additive) {
    clearSelection()
    return
  }
  selectElements(ids, { additive })
}

function onBatchStart(dragElementId) {
  beginHistoryBatch()
  pendingDragElementId.value = dragElementId || null
}

function onMoveDelta({ dx, dy }) {
  if (!pendingDragElementId.value) return
  if (!dragState.value) {
    const dragElementId = pendingDragElementId.value
    const ids = selectedIds.value.includes(dragElementId) ? [...selectedIds.value] : [dragElementId]
    dragState.value = {
      ids,
      origins: Object.fromEntries(
        ids.map((sid) => {
          const el = elements.value.find((e) => e.id === sid)
          return [sid, { x: el?.x ?? 0, y: el?.y ?? 0 }]
        })
      ),
    }
  }
  const { ids, origins } = dragState.value
  for (const sid of ids) {
    const origin = origins[sid]
    if (!origin) continue
    updateElement(sid, {
      x: Math.max(0, origin.x + dx),
      y: Math.max(0, origin.y + dy),
    })
  }
}

function onBatchEnd() {
  pendingDragElementId.value = null
  dragState.value = null
  endHistoryBatch()
}

function onKeyDown(e) {
  const editing = ['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)
  if (e.key === 'F1') {
    e.preventDefault()
    shortcutsHelpOpen.value = !shortcutsHelpOpen.value
    return
  }
  if ((e.ctrlKey || e.metaKey) && e.key === '/' && !editing) {
    e.preventDefault()
    shortcutsHelpOpen.value = true
    return
  }
  if (shortcutsHelpOpen.value) return
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z' && !e.shiftKey) {
    if (editing) return
    e.preventDefault()
    undo()
    return
  }
  if ((e.ctrlKey || e.metaKey) && (e.key.toLowerCase() === 'y' || (e.key.toLowerCase() === 'z' && e.shiftKey))) {
    if (editing) return
    e.preventDefault()
    redo()
    return
  }
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'c' && !editing) {
    if (!selectedIds.value.length) return
    e.preventDefault()
    copySelected()
    return
  }
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'v' && !editing) {
    e.preventDefault()
    pasteClipboard()
    return
  }
  if (e.key === 'Delete' && selectedIds.value.length && !editing) {
    e.preventDefault()
    if (selectedIds.value.length > 1) removeSelected()
    else removeElement(selectedId.value)
  }
}

onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown)
  document.removeEventListener('click', onAdminActionsClickOutside)
  layoutMq?.removeEventListener('change', onLayoutMqChange)
  unregisterCanvasFlush()
})

async function refreshQuota() {
  const q = await api.getQuota()
  quota.value = { remaining: q.quota_remaining, total: q.quota_total }
}

async function onGenerateImage({
  prompt,
  channelTier,
  channel,
  style,
  viewportPresetId,
  viewportWidth,
  viewportHeight,
  fitMode: genFitMode,
}) {
  if (!prompt?.trim() || !project.value) return
  imageLoading.value = true
  aiPanelRef.value?.setImageError('')
  try {
    const result = await api.generateImage(project.value.id, {
      prompt,
      tier: channelTier,
      channel: channel || undefined,
      style,
      fit_mode: genFitMode || undefined,
      viewport_preset_id: viewportPresetId || undefined,
      viewport_width: viewportWidth || undefined,
      viewport_height: viewportHeight || undefined,
    })
    aiPanelRef.value?.setGeneratedImage(result)
    await refreshQuota()
  } catch (e) {
    aiPanelRef.value?.setImageError(e.message)
  } finally {
    imageLoading.value = false
  }
}

function onAddImageToPage({ url, width, height, fitMode }) {
  if (!url) return
  addImageFromAi(url, fitMode || 'width', viewport.value, { width, height })
}

function onImageFit(fit) {
  applyImageFitToSelected(fit, viewport.value)
}

function onImageCrop() {
  const id = selectedId.value
  if (!id) return
  const el = elements.value.find((e) => e.id === id)
  if (!el || el.type !== 'image' || !el.content) return
  cropTargetId.value = id
  cropImageUrl.value = el.content
  cropInitial.value = el.style?.crop || null
  cropModalOpen.value = true
}

function onCropConfirm(crop) {
  if (!cropTargetId.value) return
  updateElement(cropTargetId.value, {
    style: { crop },
  })
  cropModalOpen.value = false
}

function onCropReset() {
  if (!cropTargetId.value) return
  updateElement(cropTargetId.value, { style: { crop: null } })
  cropInitial.value = null
}

function onPreviewAnimation(anim) {
  previewAnimation.value = anim
  previewAnimationTick.value += 1
}
</script>

<style scoped>
.editor-workspace {
  scrollbar-width: thin;
}

.editor-workspace--admin-responsive :deep(.editor-canvas-panel) {
  flex: 1 1 auto;
  min-width: 0;
  width: 100%;
}

.admin-drawer-fab {
  position: fixed;
  bottom: 1.25rem;
  z-index: 54;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.5rem 0.75rem;
  border-radius: 9999px;
  background: white;
  border: 1px solid var(--color-outline-variant, #c0c7d6);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  font-size: 0.75rem;
  font-weight: 500;
  color: #1b1b1c;
}

.admin-drawer-fab--left {
  left: 1rem;
}

.admin-drawer-fab--right {
  right: 1rem;
}

.editor-workspace :deep(.editor-canvas-panel) {
  flex: 1 1 22rem;
  min-width: 18rem;
}

@media (min-width: 1024px) {
  .editor-workspace :deep(.editor-canvas-panel) {
    flex: 1 1 28rem;
    min-width: 24rem;
  }

  .editor-workspace--admin-responsive :deep(.editor-canvas-panel) {
    min-width: 24rem;
  }
}
</style>
