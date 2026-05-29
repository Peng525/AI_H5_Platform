<template>
  <div class="h-screen flex flex-col bg-background overflow-hidden">
    <EditorTopBar :project-id="projectId" />
    <div class="editor-workspace flex flex-1 min-h-0 min-w-0 overflow-x-auto overflow-y-hidden">
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
        @viewport-change="setViewport"
        @batch-start="onBatchStart"
        @batch-end="onBatchEnd"
        @move-delta="onMoveDelta"
        @edit-wordcloud="onEditWordCloud"
        @update:show-dialogue-preview="showDialoguePreview = $event"
      />

      <AiPanel
        ref="aiPanelRef"
        :image-loading="imageLoading"
        :quota-remaining="quota.remaining"
        :quota-total="quota.total"
        @generate-image="onGenerateImage"
        @add-image-to-page="onAddImageToPage"
      />
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
import { buildBlock, getDefaultBlockBackground, resetLayoutBlockIds, resolveStoredLayoutElements } from '../constants/layoutBlocks.js'
import { useLayoutCatalog } from '../composables/useLayoutCatalog.js'
import { normalizeChatScript, serializeChatScript } from '../utils/chatScript.js'

const route = useRoute()
const { user } = useAuth()
const projectId = computed(() => route.params.id)
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
const showDialoguePreview = ref(false)

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
  beginHistoryBatch,
  endHistoryBatch,
} = useSlideCanvas(projectId, slideIdRef)

const dragState = ref(null)
const pendingDragElementId = ref(null)

const slideIndex = computed(() => {
  if (!project.value?.slides || !current.value) return 0
  return project.value.slides.findIndex((s) => s.id === current.value.id)
})

async function load() {
  project.value = await api.getProject(Number(projectId.value))
  applyFromServer(project.value.settings)
  current.value = project.value.slides?.[0] || null
  showDialoguePreview.value = !!current.value?.chat_script?.enabled
  loadElements(current.value?.canvas_elements)
  if (current.value && !elements.value.length) syncFromSlide(current.value)
  const q = await api.getQuota()
  quota.value = { remaining: q.quota_remaining, total: q.quota_total }
}

function onBgmChange(patch) {
  setBgm(patch)
}

onMounted(() => {
  registerCanvasFlush(flushCanvasSave)
  window.addEventListener('keydown', onKeyDown)
  layoutCatalog.load()
  load()
})
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
    alert(e.message)
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
  if ((project.value.slides?.length || 0) <= 1) {
    alert('至少保留一页')
    return
  }
  if (!confirm('确定删除该页面？')) return
  saveElements()
  try {
    await api.deleteSlide(project.value.id, slideId)
    localStorage.removeItem(`ai_h5_canvas_${project.value.id}_${slideId}`)
    project.value.slides = project.value.slides.filter((s) => s.id !== slideId)
    if (current.value?.id === slideId) {
      current.value = project.value.slides[0]
      loadElements()
    }
  } catch (e) {
    alert(e.message)
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
    alert(e.message || '保存页面失败')
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
    alert(e.message || '插入对话失败，请重试')
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
  unregisterCanvasFlush()
})

async function refreshQuota() {
  const q = await api.getQuota()
  quota.value = { remaining: q.quota_remaining, total: q.quota_total }
}

async function onGenerateImage({ prompt, channelTier, channel, style }) {
  if (!prompt?.trim() || !project.value) return
  imageLoading.value = true
  aiPanelRef.value?.setImageError('')
  try {
    const result = await api.generateImage(project.value.id, {
      prompt,
      tier: channelTier,
      channel: channel || undefined,
      style,
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

function onPreviewAnimation(anim) {
  previewAnimation.value = anim
  previewAnimationTick.value += 1
}
</script>

<style scoped>
.editor-workspace {
  scrollbar-width: thin;
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
}
</style>
