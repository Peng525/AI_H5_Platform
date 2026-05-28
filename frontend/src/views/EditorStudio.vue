<template>
  <div class="h-screen flex flex-col bg-background overflow-hidden">
    <EditorTopBar :project-title="project?.title" :project-id="projectId" />
    <div class="flex flex-1 min-h-0">
      <EditorToolbox
        :slides="project?.slides || []"
        :current-id="current?.id"
        :current-slide="current"
        :theme="project?.theme"
        @select-slide="selectSlide"
        @add-slide="addSlide"
        @remove-slide="removeSlide"
        @save-slide="saveSlideFields"
        @sync-canvas="syncCanvasFromSlide"
        @add-material="addMaterial"
      />

      <EditorPhoneCanvas
        :elements="elements"
        :selected-id="selectedId"
        :slide="current"
        :slide-index="slideIndex"
        @select="selectedId = $event"
        @deselect="selectedId = null"
        @update-element="updateElement"
        @add-text="addElement('text')"
        @add-shape="addElement('shape')"
        @style-change="onStyleChange"
        @duplicate="onDuplicate"
        @delete-selected="onDeleteSelected"
        @bring-front="onBringFront"
      />

      <AiPanel
        :loading="aiLoading"
        :quota-remaining="quota.remaining"
        :quota-total="quota.total"
        @generate="onGenerate"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/client'
import { useAuth } from '../composables/useAuth'
import { useSlideCanvas } from '../composables/useSlideCanvas'
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
const quota = ref({ remaining: 5, total: 5 })

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
} = useSlideCanvas(projectId, slideIdRef)

const slideIndex = computed(() => {
  if (!project.value?.slides || !current.value) return 0
  return project.value.slides.findIndex((s) => s.id === current.value.id)
})

async function load() {
  project.value = await api.getProject(Number(projectId.value))
  current.value = project.value.slides?.[0] || null
  loadElements()
  if (current.value) syncFromSlide(current.value)
  const q = await api.getQuota(user.value?.user_id)
  quota.value = { remaining: q.quota_remaining, total: q.quota_total }
}

onMounted(load)
watch(() => route.params.id, load)

function selectSlide(slide) {
  saveElements()
  current.value = slide
  loadElements()
}

async function addSlide() {
  saveElements()
  try {
    const slide = await api.addSlide(project.value.id, {
      title: '新页面',
      subtitle: '',
      bullets: [],
      layout: 'bullets',
    })
    project.value.slides.push(slide)
    current.value = slide
    loadElements()
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
  if (item.type === 'shape') {
    addElement('shape', {
      style: { background: item.color, borderRadius: item.borderRadius || 8 },
    })
  } else if (item.type === 'image') {
    addElement('image', { content: item.content, width: 160, height: 100 })
  }
}

function onStyleChange(patch) {
  if (!selectedId.value) return
  const el = elements.value.find((e) => e.id === selectedId.value)
  if (!el) return
  if (patch.fontSize !== undefined) {
    updateElement(selectedId.value, { style: { ...el.style, fontSize: patch.fontSize } })
  } else {
    updateElement(selectedId.value, { style: { ...el.style, ...patch } })
  }
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

onMounted(() => window.addEventListener('keydown', onKeyDown))
onUnmounted(() => window.removeEventListener('keydown', onKeyDown))

async function onGenerate({ prompt, channelTier, channel }) {
  if (!prompt?.trim() || !current.value) return
  aiLoading.value = true
  try {
    const updated = await api.generatePage(
      project.value.id,
      current.value.id,
      { instruction: prompt, tier: channelTier, channel: channel || undefined },
      user.value?.user_id
    )
    const idx = project.value.slides.findIndex((s) => s.id === updated.id)
    if (idx >= 0) project.value.slides[idx] = updated
    current.value = updated
    syncCanvasFromSlide()
    const q = await api.getQuota(user.value?.user_id)
    quota.value = { remaining: q.quota_remaining, total: q.quota_total }
  } catch (e) {
    alert(e.message)
  } finally {
    aiLoading.value = false
  }
}
</script>
