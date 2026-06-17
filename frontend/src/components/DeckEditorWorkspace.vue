<template>
  <div class="flex flex-col flex-1 min-h-0 min-w-0 overflow-hidden">
  <div v-if="projectLoading" class="flex-1 flex items-center justify-center min-h-0">
    <PageLoading message="加载项目中…" />
  </div>
  <div v-else-if="loadError" class="flex-1 flex items-center justify-center p-6 min-h-0">
    <EmptyState icon="error" title="无法加载项目" :description="loadError" action-label="重试" @action="load" />
  </div>
  <div
    v-else
    class="editor-workspace flex flex-1 min-h-0 min-w-0 relative"
    :class="[
      layoutMode === 'result' ? 'flex-row' : '',
      isAdminEditorMode ? 'editor-workspace--admin-responsive overflow-hidden' : 'overflow-hidden',
    ]"
  >
    <template v-if="isAdminEditorMode && !isWideLayout">
      <button type="button" class="admin-drawer-fab admin-drawer-fab--left" @click="aiDrawerOpen = false; toolboxDrawerOpen = true">
        <span class="material-symbols-outlined text-[18px]">widgets</span>
        工具箱
      </button>
      <button type="button" class="admin-drawer-fab admin-drawer-fab--right" @click="toolboxDrawerOpen = false; aiDrawerOpen = true">
        <span class="material-symbols-outlined text-[18px]">auto_awesome</span>
        AI
      </button>
      <div v-if="toolboxDrawerOpen || aiDrawerOpen" class="fixed inset-0 top-14 bg-black/30 z-[55]" @click="closeAdminDrawers" />
    </template>

    <div
      v-if="showEditorCoach && layoutMode === 'studio'"
      class="absolute top-3 left-1/2 -translate-x-1/2 z-[70] max-w-sm w-[calc(100%-2rem)] bg-white border border-outline-variant/60 rounded-xl px-4 py-3.5 shadow-md"
    >
      <div class="flex items-start justify-between gap-3 mb-3">
        <p class="text-sm font-medium text-on-surface">首次使用 AI 配图</p>
        <button type="button" class="shrink-0 text-on-surface-variant hover:text-on-surface material-symbols-outlined text-lg leading-none" aria-label="关闭" @click="dismissEditorCoach">close</button>
      </div>
      <button type="button" class="mt-3 w-full py-1.5 text-xs font-medium text-primary hover:bg-primary/5 rounded-lg" @click="dismissEditorCoach">知道了</button>
    </div>

    <!-- 左栏 -->
    <aside
      v-if="layoutMode === 'result'"
      class="w-[7.5rem] sm:w-[8.5rem] border-r border-outline-variant bg-surface-container-low shrink-0 min-h-0 overflow-y-auto"
    >
      <SlideThumbList
        compact
        :slides="project?.slides || []"
        :current-id="current?.id"
        :project-id="projectId"
        :viewport="resultDisplayViewport"
        :project-settings="settings"
        :live-slide-id="current?.id ?? null"
        :live-elements="elements"
        @select="onResultSelectSlide"
        @add="addSlide"
        @remove="removeSlide"
      />
    </aside>
    <div v-else :class="toolboxPanelClass">
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

    <!-- 中栏 -->
    <div v-if="layoutMode === 'result'" class="flex flex-col flex-1 min-w-0 min-h-0 relative">
      <div
        v-if="reveal.isRevealing.value"
        class="shrink-0 px-4 py-2 bg-primary/8 border-b border-primary/20 flex items-center justify-between gap-3 text-sm"
      >
        <span class="text-on-surface font-medium inline-flex items-center gap-2">
          <span class="material-symbols-outlined text-primary text-[20px] animate-pulse">draw</span>
          正在绘制…
        </span>
        <button
          type="button"
          class="text-xs font-medium text-primary hover:underline shrink-0"
          @click="onSkipReveal"
        >
          跳过动画
        </button>
      </div>
      <div class="relative flex-1 min-h-0 min-w-0">
        <ResultSlidesOverview
          ref="overviewRef"
          class="h-full"
          :slides="project?.slides || []"
          :current-id="current?.id ?? null"
          :project-id="projectId"
          :project-settings="settings"
          :display-viewport="resultDisplayViewport"
          :viewport-id="effectiveViewportId"
          :theme-id="settings.themeId || 'zjy-minimal'"
          :elements="elements"
          :selected-ids="selectedIds"
          :canvas-background="canvasBackground"
          :reveal-active="reveal.isRevealing.value"
          :interaction-locked="reveal.isRevealing.value"
          :visible-slide-count="reveal.visibleSlideCount.value"
          :visible-element-ids-by-slide="reveal.visibleElementIdsBySlide.value"
          @select="onResultSelectSlide"
          @select-element="onSelectElement"
          @deselect="clearSelection"
          @marquee-select="onMarqueeSelect"
          @update-element="updateElement"
          @batch-start="onBatchStart"
          @batch-end="onBatchEnd"
          @move-delta="onMoveDelta"
          @edit-wordcloud="onEditWordCloud"
          @edit-chart-stack="onEditChartStack"
          @text-edit-start="onTextEditStart"
          @text-edit-end="onTextEditEnd"
          @add-slide-after="onAddSlideAfter"
          @open-generate-card="onOpenGenerateCard"
          @close-generate-panel="onCloseGeneratePanel"
          @generate-card="onGenerateCardSubmit"
          :generate-panel-slide-id="generatePanelSlideId"
          :generate-loading="slideGenerating"
          :quota-remaining="quota.remaining"
          :quota-total="quota.total"
          @deselect-slide="deselectCurrentSlide"
        />
        <EditorContextLayer
          :hidden="reveal.isRevealing.value"
          :selected-element="selectedElementForToolbar"
          :slide-id="current?.id ?? null"
          :text-editing="!!textEditingId"
          :theme-id="settings.themeId || 'zjy-minimal'"
          :viewport-id="effectiveViewportId"
          :viewport="resultDisplayViewport"
          :resolve-element-el="resolveRevealElementEl"
          :scroll-root-ref="overviewScrollRoot"
          @style-change="onStyleChange"
          @image-fit="onImageFit"
          @image-crop="onImageCrop"
          @image-layout="onImageLayout"
          @duplicate="onDuplicate"
          @bring-front="onBringFront"
          @send-back="onSendBack"
          @delete-selected="onDeleteSelected"
          @edit-chart-stack="onEditChartStack"
        />
        <DeckRevealBrush
          :active="reveal.isRevealing.value"
          :target="reveal.brushTarget.value"
          :resolve-element-el="resolveRevealElementEl"
        />
      </div>
    </div>
    <EditorPhoneCanvas
      v-else
      class="editor-canvas-panel flex-1 min-w-0"
      :elements="elements"
      :selected-ids="selectedIds"
      :slide="current"
      :slide-index="slideIndex"
      :viewport="viewport"
      :viewport-id="effectiveViewportId"
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
      @viewport-change="onViewportChange"
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

    <!-- 右栏 -->
    <ElementMediaPanel
      v-if="layoutMode === 'result' && showMediaPanel"
      :selected-element="selectedElementForToolbar"
      :image-loading="imageLoading"
      :quota-remaining="quota.remaining"
      :quota-total="quota.total"
      @close="clearSelection"
      @image-fit="onImageFit"
      @image-crop="onImageCrop"
      @regenerate-image="onRegenerateSelectedImage"
    />
    <ResultEditRail
      v-else-if="layoutMode === 'result'"
      ref="resultRailRef"
      :current-slide="current"
      :canvas-background="canvasBackground"
      :project-settings="settings"
      :scroll-effect="settings.scrollEffect"
      :primary-layouts="primaryLayoutItems"
      :more-layouts="moreLayoutItems"
      @open-ai-image="aiImageOpen = true"
      @add-material="addMaterial"
      @canvas-bg-change="onCanvasBgChange"
      @apply-layout="applyLayoutBlock"
      @open-dialogue-generator="openDialogueGenerator"
      @open-wordcloud-editor="wordCloudOpen = true"
      @save-slide="saveSlideFields"
      @scroll-change="setScrollEffect"
      @preview-animation="onPreviewAnimation"
      @bgm-change="onBgmChange"
    />
    <div v-else-if="layoutMode !== 'result'" :class="aiPanelClass">
      <AiPanel
        ref="aiPanelRef"
        :image-loading="imageLoading"
        :quota-remaining="quota.remaining"
        :quota-total="quota.total"
        :canvas-viewport-id="effectiveViewportId"
        @generate-image="onGenerateImage"
        @add-image-to-page="onAddImageToPage"
      />
    </div>
  </div>

  <EditorShortcutsHelp v-model:open="shortcutsHelpOpen" />
  <DialogueGeneratorModal :open="dialogueGeneratorOpen" :initial-script="current?.chat_script" @close="dialogueGeneratorOpen = false" @insert="onInsertDialogue" />
  <WordCloudEditorModal :open="wordCloudOpen" :theme-id="settings.themeId || 'zjy-minimal'" :initial-content="wordCloudEditContent" @close="wordCloudOpen = false; wordCloudEditContent = null" @insert-vector="onInsertWordCloud" @insert-image="onInsertWordCloudImage" />
  <ChartStackEditorModal :open="chartStackOpen" :initial-content="chartStackEditContent" @close="chartStackOpen = false; chartStackEditContent = null" @save="onSaveChartStack" />
  <ImageCropModal :open="cropModalOpen" :image-url="cropImageUrl" :initial-crop="cropInitial" @close="cropModalOpen = false" @confirm="onCropConfirm" @reset="onCropReset" />
  <ConfirmDialog :open="!!deleteSlideConfirm" title="删除页面" message="确定删除该页面？此操作不可撤销。" confirm-text="删除" cancel-text="取消" danger @confirm="onDeleteSlideConfirm" @cancel="deleteSlideConfirm = null" />
  <AiImageModal
    v-if="layoutMode === 'result'"
    ref="aiImageModalRef"
    :open="aiImageOpen"
    :image-loading="imageLoading"
    :quota-remaining="quota.remaining"
    :quota-total="quota.total"
    :canvas-viewport-id="effectiveViewportId"
    @close="aiImageOpen = false; resultRailRef?.clearAiHighlight?.()"
    @generate-image="onGenerateImage"
    @add-image-to-page="onAddImageToPage"
  />
  <AdminPresetSaveDialog
    v-if="adminPresetId"
    :open="presetSaveOpen"
    :template-id="adminPresetId"
    :project-id="projectId"
    :initial="templateMeta"
    @close="presetSaveOpen = false"
    @saved="onPresetSaved"
  />
  <AdminLayoutSaveDialog
    v-if="adminLayoutId"
    :open="layoutSaveOpen"
    :layout-id="adminLayoutId"
    :project-id="projectId"
    :initial="layoutMeta"
    @close="layoutSaveOpen = false"
    @saved="onLayoutSaved"
  />
  <ThemeSidebarDrawer
    v-if="layoutMode === 'result'"
    :open="themeDrawerOpen"
    :active-theme-id="settings.themeId || 'zjy-minimal'"
    :disabled="reveal.isRevealing.value"
    @close="emit('close-theme-drawer')"
    @select="onThemeDrawerSelect"
  />
  </div>
</template>

<script setup>
import { ref, toRef, watch, computed } from 'vue'
import { getViewportPreset, DEFAULT_WEB_VIEWPORT_ID } from '../constants/editorPresets.js'
import { useDeckEditor } from '../composables/useDeckEditor.js'
import { useDeckRevealAnimation } from '../composables/useDeckRevealAnimation.js'
import { ensureSlideCompiled } from '../utils/compileStructuredSlide.js'
import ResultSlidesOverview from './create/ResultSlidesOverview.vue'
import EditorContextLayer from './create/EditorContextLayer.vue'
import ElementMediaPanel from './create/ElementMediaPanel.vue'
import AiPanel from './AiPanel.vue'
import EditorPhoneCanvas from './EditorPhoneCanvas.vue'
import EditorToolbox from './EditorToolbox.vue'
import SlideThumbList from './SlideThumbList.vue'
import EditorShortcutsHelp from './EditorShortcutsHelp.vue'
import DialogueGeneratorModal from './dialogue/DialogueGeneratorModal.vue'
import WordCloudEditorModal from './wordcloud/WordCloudEditorModal.vue'
import ChartStackEditorModal from './charts/ChartStackEditorModal.vue'
import ImageCropModal from './ImageCropModal.vue'
import PageLoading from './PageLoading.vue'
import EmptyState from './EmptyState.vue'
import ConfirmDialog from './ConfirmDialog.vue'
import ResultEditRail from './create/ResultEditRail.vue'
import DeckRevealBrush from './create/DeckRevealBrush.vue'
import AiImageModal from './create/AiImageModal.vue'
import AdminPresetSaveDialog from './admin/AdminPresetSaveDialog.vue'
import AdminLayoutSaveDialog from './admin/AdminLayoutSaveDialog.vue'
import ThemeSidebarDrawer from './create/ThemeSidebarDrawer.vue'

const props = defineProps({
  projectId: { type: [String, Number], required: true },
  initialProject: { type: Object, default: null },
  layoutMode: { type: String, default: 'studio', validator: (v) => ['studio', 'result'].includes(v) },
  adminPresetId: { type: String, default: '' },
  adminLayoutId: { type: String, default: '' },
  autoRevealOnLoad: { type: Boolean, default: false },
  themeDrawerOpen: { type: Boolean, default: false },
})

const emit = defineEmits(['project-loaded', 'project-load-error', 'reveal-complete', 'close-theme-drawer'])

const initialProjectRef = toRef(props, 'initialProject')

const editor = useDeckEditor(toRef(props, 'projectId'), {
  layoutMode: props.layoutMode,
  adminPresetId: toRef(props, 'adminPresetId'),
  adminLayoutId: toRef(props, 'adminLayoutId'),
  initialProject: initialProjectRef,
  onProjectLoaded: (p) => emit('project-loaded', p),
  onProjectLoadError: (err) => emit('project-load-error', err),
})

const {
  project,
  current,
  projectLoading,
  loadError,
  load,
  addSlide,
  addSlideAfter,
  generateSlideAfter,
  slideGenerating,
  selectSlide,
  deselectCurrentSlide,
  removeSlide,
  saveSlideFields,
  syncCanvasFromSlide,
  addMaterial,
  applyLayoutBlock,
  onCanvasBgChange,
  setScrollEffect,
  onPreviewAnimation,
  onBgmChange,
  openDialogueGenerator,
  elements,
  selectedIds,
  slideIndex,
  viewport,
  settings,
  previewAnimation,
  previewAnimationTick,
  canvasBackground,
  showDialoguePreview,
  bgmActive,
  bgmMuted,
  bgmSpinning,
  toggleBgmMute,
  onSelectElement,
  clearSelection,
  onMarqueeSelect,
  updateElement,
  addElement,
  addImagePlaceholder,
  onStyleChange,
  onDuplicate,
  onDeleteSelected,
  onBringFront,
  onSendBack,
  onBringForward,
  onSendBackward,
  onCenterElement,
  onImageFit,
  onImageLayout,
  onRegenerateSelectedImage,
  onImageCrop,
  onTextEditStart,
  onTextEditEnd,
  textEditingId,
  setViewport,
  onViewportChange,
  undo,
  redo,
  canUndo,
  canRedo,
  onBatchStart,
  onBatchEnd,
  onMoveDelta,
  onEditWordCloud,
  onEditChartStack,
  imageLoading,
  aiPanelRef,
  aiImageModalRef,
  aiImageOpen,
  quota,
  onGenerateImage,
  onAddImageToPage,
  shortcutsHelpOpen,
  dialogueGeneratorOpen,
  wordCloudOpen,
  wordCloudEditContent,
  chartStackOpen,
  chartStackEditContent,
  onInsertDialogue,
  onInsertWordCloud,
  onInsertWordCloudImage,
  onSaveChartStack,
  cropModalOpen,
  cropImageUrl,
  cropInitial,
  onCropConfirm,
  onCropReset,
  deleteSlideConfirm,
  onDeleteSlideConfirm,
  dismissEditorCoach,
  showEditorCoach,
  isAdminEditorMode,
  isWideLayout,
  toolboxDrawerOpen,
  aiDrawerOpen,
  closeAdminDrawers,
  toolboxPanelClass,
  aiPanelClass,
  primaryLayoutItems,
  moreLayoutItems,
  presetSaveOpen,
  layoutSaveOpen,
  templateMeta,
  layoutMeta,
  onPresetSaved,
  onLayoutSaved,
  openLayoutSave,
  openPresetSave,
  pptImporting,
  onAdminPptxImport,
  applyGlobalTheme,
  compileAllSlidesLazy,
} = editor

const reveal = useDeckRevealAnimation()
let revealStarted = false

function getSlideElementsForReveal(slide) {
  if (!slide) return []
  return ensureSlideCompiled(
    slide,
    settings.value.viewportId || DEFAULT_WEB_VIEWPORT_ID,
    settings.value.themeId || 'zjy-minimal'
  )
}

function resolveRevealElementEl(slideId, elementId) {
  return overviewRef.value?.resolveElementEl?.(slideId, elementId) || null
}

function onSkipReveal() {
  reveal.skipReveal()
}

function tryStartReveal() {
  if (!props.autoRevealOnLoad || revealStarted) return
  if (reveal.isDone.value) return
  if (props.layoutMode !== 'result') return
  if (projectLoading.value || !project.value?.slides?.length) return
  revealStarted = true
  compileAllSlidesLazy(false)
  reveal.startReveal({
    slides: project.value.slides,
    getElements: getSlideElementsForReveal,
    scrollToSlide: (id) => overviewRef.value?.scrollToSlide?.(id, false),
    onComplete: () => {
      emit('reveal-complete')
    },
  })
}

const selectedElementForToolbar = computed(() => {
  const primaryId = selectedIds.value[selectedIds.value.length - 1]
  return elements.value.find((el) => el.id === primaryId) || null
})

const showMediaPanel = computed(
  () =>
    !reveal.isRevealing.value &&
    selectedElementForToolbar.value?.type === 'image' &&
    !textEditingId.value,
)

const overviewRef = ref(null)
const overviewScrollRoot = computed(() => {
  const exposed = overviewRef.value?.scrollRootRef
  if (!exposed) return null
  return exposed.value ?? exposed
})
const resultRailRef = ref(null)
const generatePanelSlideId = ref(null)
const generateCardAfterSlideId = ref(null)
const resultDisplayViewport = computed(() =>
  getViewportPreset(settings.value.viewportId || DEFAULT_WEB_VIEWPORT_ID)
)
const effectiveViewportId = computed(
  () => settings.value.viewportId || DEFAULT_WEB_VIEWPORT_ID
)

async function onAddSlideAfter(afterSlideId) {
  const slide = await addSlideAfter(afterSlideId)
  if (slide?.id) {
    overviewRef.value?.scrollToSlide?.(slide.id)
  }
}

async function onOpenGenerateCard(afterSlideId) {
  generateCardAfterSlideId.value = afterSlideId
  generatePanelSlideId.value = afterSlideId
  const slide = project.value?.slides?.find((s) => s.id === afterSlideId)
  if (slide) {
    await selectSlide(slide)
  }
  overviewRef.value?.scrollToSlide?.(afterSlideId)
}

function onCloseGeneratePanel() {
  generatePanelSlideId.value = null
}

async function onGenerateCardSubmit(payload) {
  const slide = await generateSlideAfter(generateCardAfterSlideId.value, payload)
  generatePanelSlideId.value = null
  if (slide?.id) {
    overviewRef.value?.scrollToSlide?.(slide.id)
  }
}

async function onResultSelectSlide(slide) {
  const sameSlide = current.value?.id === slide.id
  if (!sameSlide) {
    await selectSlide(slide)
  }
  overviewRef.value?.scrollToSlide?.(slide.id)
}

async function onThemeDrawerSelect(themeId) {
  await applyGlobalTheme(themeId)
  emit('close-theme-drawer')
}

watch(
  [projectLoading, loadError, project],
  ([loading, err, p]) => {
    if (!loading && err) emit('project-load-error', err)
    else if (!loading && !err && p) {
      emit('project-loaded', p)
      tryStartReveal()
    }
  },
  { flush: 'post', immediate: true }
)

watch(
  () => props.projectId,
  () => {
    revealStarted = false
    reveal.resetReveal()
  }
)

defineExpose({
  project,
  projectLoading,
  loadError,
  load,
  flushCanvasSave: editor.flushCanvasSave,
  openLayoutSave,
  openPresetSave,
  pptImporting,
  onAdminPptxImport,
  applyGlobalTheme,
  reveal,
})
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

.admin-drawer-fab--left { left: 1rem; }
.admin-drawer-fab--right { right: 1rem; }

.editor-workspace :deep(.editor-canvas-panel) {
  flex: 1 1 22rem;
  min-width: 18rem;
}

@media (min-width: 1024px) {
  .editor-workspace :deep(.editor-canvas-panel) {
    flex: 1 1 28rem;
    min-width: 24rem;
  }
}
</style>
