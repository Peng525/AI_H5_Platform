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
        @select-slide="selectSlide"
        @add-slide="addSlide"
        @remove-slide="removeSlide"
        @save-slide="saveSlideFields"
        @sync-canvas="syncCanvasFromSlide"
        @add-material="addMaterial"
        @canvas-bg-change="onCanvasBgChange"
        @scroll-change="setScrollEffect"
        @preview-animation="onPreviewAnimation"
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
        @viewport-change="setViewport"
      />

      <AiPanel
        ref="aiPanelRef"
        :text-loading="aiLoading"
        :image-loading="imageLoading"
        :quota-remaining="quota.remaining"
        :quota-total="quota.total"
        @generate-text="onGenerateText"
        @generate-image="onGenerateImage"
        @add-image-to-page="onAddImageToPage"
      />
    </div>
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

const route = useRoute()
const { user } = useAuth()
const projectId = computed(() => route.params.id)
const project = ref(null)
const current = ref(null)
const aiLoading = ref(false)
const imageLoading = ref(false)
const aiPanelRef = ref(null)
const quota = ref({ remaining: 5, total: 5 })
const previewAnimation = ref('')
const previewAnimationTick = ref(0)

const { settings, viewport, setViewport, setScrollEffect, getSlideBackground, setSlideBackground } = useProjectEditorSettings(projectId)

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
  addImageFromAi,
  flushCanvasSave,
} = useSlideCanvas(projectId, slideIdRef)

const slideIndex = computed(() => {
  if (!project.value?.slides || !current.value) return 0
  return project.value.slides.findIndex((s) => s.id === current.value.id)
})

async function load() {
  project.value = await api.getProject(Number(projectId.value))
  current.value = project.value.slides?.[0] || null
  loadElements(current.value?.canvas_elements)
  if (current.value && !elements.value.length) syncFromSlide(current.value)
  const q = await api.getQuota()
  quota.value = { remaining: q.quota_remaining, total: q.quota_total }
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
    current.value = slide
    loadElements(slide.canvas_elements)
    if (!elements.value.length) syncFromSlide(slide)
  } catch (e) {
    alert(e.message)
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
    current.value = updated
  } catch (e) {
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
  }
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

function onKeyDown(e) {
  if (e.key === 'Delete' && selectedId.value && !['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)) {
    removeElement(selectedId.value)
  }
}

onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown)
  unregisterCanvasFlush()
})

async function onGenerateText({ prompt, channelTier, channel }) {
  if (!prompt?.trim() || !current.value) return
  aiLoading.value = true
  try {
    const updated = await api.generatePage(
      project.value.id,
      current.value.id,
      { instruction: prompt, tier: channelTier, channel: channel || undefined }
    )
    const idx = project.value.slides.findIndex((s) => s.id === updated.id)
    if (idx >= 0) project.value.slides[idx] = updated
    current.value = updated
    syncCanvasFromSlide()
    await refreshQuota()
  } catch (e) {
    alert(e.message)
  } finally {
    aiLoading.value = false
  }
}

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
