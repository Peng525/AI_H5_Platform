<template>
  <div class="h-screen flex flex-col bg-background overflow-hidden">
    <EditorTopBar :project-id="projectId" />
    <div class="flex flex-1 min-h-0">
      <EditorToolbox
        :slides="project?.slides || []"
        :current-id="current?.id"
        :current-slide="current"
        :theme="project?.theme"
        :scroll-effect="settings.scrollEffect"
        :canvas-background="canvasBackground"
        :project-settings="settings"
        :project-id="projectId"
        :viewport="viewport"
        :live-slide-id="current?.id ?? null"
        :live-elements="elements"
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
        :elements="elements"
        :selected-id="selectedId"
        :slide="current"
        :slide-index="slideIndex"
        :viewport="viewport"
        :viewport-id="settings.viewportId"
        :preview-animation="previewAnimation"
        :preview-animation-tick="previewAnimationTick"
        :canvas-background="canvasBackground"
        :theme-id="settings.themeId || 'zjy-minimal'"
        :show-dialogue-preview="showDialoguePreview"
        @select="selectedId = $event"
        @deselect="selectedId = null"
        @update-element="updateElement"
        @add-text="addElement('text')"
        @add-shape="addElement('shape')"
        @add-image="addImagePlaceholder"
        @style-change="onStyleChange"
        @duplicate="onDuplicate"
        @delete-selected="onDeleteSelected"
        @bring-front="onBringFront"
        @center-element="onCenterElement"
        @viewport-change="setViewport"
        @batch-start="beginHistoryBatch"
        @batch-end="endHistoryBatch"
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
    <LayoutPickerModal
      :open="layoutPickerOpen"
      @close="layoutPickerOpen = false"
      @pick="onLayoutPickedForNewSlide"
      @blank="onLayoutBlankForNewSlide"
    />
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
import AiPanel from '../components/AiPanel.vue'
import EditorPhoneCanvas from '../components/EditorPhoneCanvas.vue'
import EditorToolbox from '../components/EditorToolbox.vue'
import EditorTopBar from '../components/EditorTopBar.vue'
import EditorShortcutsHelp from '../components/EditorShortcutsHelp.vue'
import LayoutPickerModal from '../components/LayoutPickerModal.vue'
import DialogueGeneratorModal from '../components/dialogue/DialogueGeneratorModal.vue'
import WordCloudEditorModal from '../components/wordcloud/WordCloudEditorModal.vue'
import { buildBlock, getDefaultBlockBackground } from '../constants/layoutBlocks.js'
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
const layoutPickerOpen = ref(false)
const pendingNewSlide = ref(null)
const dialogueGeneratorOpen = ref(false)
const wordCloudOpen = ref(false)
const wordCloudEditContent = ref(null)
const showDialoguePreview = ref(false)

const { settings, viewport, setViewport, setScrollEffect, getSlideBackground, setSlideBackground, applyFromServer, setBgm } = useProjectEditorSettings(projectId)

const canvasBackground = computed(() => getSlideBackground(current.value?.id))

const slideIdRef = computed(() => current.value?.id ?? null)
const {
  elements,
  selectedId,
  saveElements,
  loadElements,
  addElement,
  updateElement,
  removeElement,
  duplicateElement,
  bringToFront,
  syncFromSlide,
  replaceAllElements,
  addImageFromAi,
  flushCanvasSave,
  undo,
  redo,
  beginHistoryBatch,
  endHistoryBatch,
} = useSlideCanvas(projectId, slideIdRef)

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
    pendingNewSlide.value = slide
    layoutPickerOpen.value = true
  } catch (e) {
    alert(e.message)
  }
}

function finishNewSlide(slide, blockId = null) {
  current.value = slide
  loadElements(slide.canvas_elements)
  if (blockId) {
    applyLayoutBlock(blockId, slide.id)
  } else if (!elements.value.length) {
    syncFromSlide(slide)
  }
  pendingNewSlide.value = null
}

function onLayoutPickedForNewSlide(blockId) {
  if (pendingNewSlide.value) finishNewSlide(pendingNewSlide.value, blockId)
}

function onLayoutBlankForNewSlide() {
  if (pendingNewSlide.value) finishNewSlide(pendingNewSlide.value, null)
}

function applyLayoutBlock(blockId, slideId = null) {
  const sid = slideId ?? current.value?.id
  if (!sid) return
  if (slideId && slideId !== current.value?.id) {
    current.value = project.value.slides.find((s) => s.id === slideId) || current.value
    loadElements([])
  }
  const els = buildBlock(blockId, settings.value.viewportId, settings.value.themeId || 'zjy-minimal')
  replaceAllElements(els)
  setSlideBackground(sid, getDefaultBlockBackground(settings.value.themeId || 'zjy-minimal'))
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
  if (selectedId.value) duplicateElement(selectedId.value)
}

function onDeleteSelected() {
  if (selectedId.value) removeElement(selectedId.value)
}

function onBringFront() {
  if (selectedId.value) bringToFront(selectedId.value)
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
  if (e.key === 'Delete' && selectedId.value && !editing) {
    removeElement(selectedId.value)
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

function onPreviewAnimation(anim) {
  previewAnimation.value = anim
  previewAnimationTick.value += 1
}
</script>
