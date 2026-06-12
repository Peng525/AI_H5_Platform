<template>
  <div class="flex shrink-0 min-h-0 h-full">
    <aside class="w-14 sm:w-[3.75rem] border-l border-outline-variant/60 bg-surface-container-lowest flex flex-col shrink-0 h-full min-h-0 py-3">
      <div class="flex-1 flex flex-col items-center gap-2 px-1.5 overflow-y-auto">
        <button
          v-for="item in railItems"
          :key="item.id"
          type="button"
          class="w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-150"
          :class="iconClass(item.id)"
          :title="item.label"
          @click="onRailClick(item.id)"
        >
          <span class="material-symbols-outlined text-[22px]">{{ item.icon }}</span>
        </button>
      </div>
    </aside>

    <ResultToolModal :open="materialOpen" title="素材" @close="closeModal('material')">
      <MaterialPanel
        class="p-3"
        :canvas-background="canvasBackground"
        :theme-id="projectSettings?.themeId || 'zjy-minimal'"
        :primary-layouts="primaryLayouts"
        :more-layouts="moreLayouts"
        :show-background-picker="false"
        @add="onMaterialAdd"
        @apply-layout="emit('apply-layout', $event)"
        @open-dialogue-generator="emit('open-dialogue-generator')"
        @open-wordcloud-editor="emit('open-wordcloud-editor')"
      />
    </ResultToolModal>

    <ResultToolModal :open="backgroundOpen" title="页面背景" @close="closeModal('background')">
      <CanvasBackgroundPicker
        class="p-4"
        :canvas-background="canvasBackground"
        :theme-id="projectSettings?.themeId || 'zjy-minimal'"
        @canvas-bg-change="onBackgroundChange"
      />
    </ResultToolModal>

    <ResultToolModal :open="effectOpen" title="动效" @close="closeModal('effect')">
      <SlideEffectPanel
        class="p-3"
        :slide="currentSlide"
        :scroll-effect="scrollEffect"
        @save="emit('save-slide', $event)"
        @scroll-change="emit('scroll-change', $event)"
        @preview-animation="emit('preview-animation', $event)"
      />
    </ResultToolModal>

    <ResultToolModal :open="musicOpen" title="音乐" @close="closeModal('music')">
      <BgmPanel
        class="p-3"
        :project-settings="projectSettings"
        @bgm-change="emit('bgm-change', $event)"
      />
    </ResultToolModal>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import BgmPanel from '../BgmPanel.vue'
import CanvasBackgroundPicker from '../CanvasBackgroundPicker.vue'
import MaterialPanel from '../MaterialPanel.vue'
import SlideEffectPanel from '../SlideEffectPanel.vue'
import ResultToolModal from './ResultToolModal.vue'

defineProps({
  currentSlide: { type: Object, default: null },
  canvasBackground: { type: String, default: '' },
  projectSettings: { type: Object, default: null },
  scrollEffect: { type: String, default: 'page' },
  primaryLayouts: { type: Array, default: null },
  moreLayouts: { type: Array, default: null },
})

const emit = defineEmits([
  'open-ai-image',
  'add-material',
  'canvas-bg-change',
  'apply-layout',
  'open-dialogue-generator',
  'open-wordcloud-editor',
  'save-slide',
  'scroll-change',
  'preview-animation',
  'bgm-change',
])

const activeTool = ref(null)
const materialOpen = ref(false)
const backgroundOpen = ref(false)
const effectOpen = ref(false)
const musicOpen = ref(false)

const railItems = [
  { id: 'material', label: '素材', icon: 'cloud_upload' },
  { id: 'background', label: '页面背景', icon: 'palette' },
  { id: 'effect', label: '动效', icon: 'animation' },
  { id: 'music', label: '音乐', icon: 'music_note' },
  { id: 'ai', label: 'AI 生图', icon: 'image' },
]

function iconClass(id) {
  const active = activeTool.value === id
  if (active) {
    return 'bg-primary/12 text-primary shadow-[0_2px_8px_rgba(59,130,246,0.22),0_0_0_1px_rgba(59,130,246,0.25)] ring-2 ring-primary/30'
  }
  return 'bg-white text-on-surface-variant shadow-[0_1px_3px_rgba(0,0,0,0.1),0_0_0_1px_rgba(0,0,0,0.06)] hover:shadow-md hover:text-on-surface'
}

function closeAllModals() {
  materialOpen.value = false
  backgroundOpen.value = false
  effectOpen.value = false
  musicOpen.value = false
}

function closeModal(id) {
  if (id === 'material') materialOpen.value = false
  if (id === 'background') backgroundOpen.value = false
  if (id === 'effect') effectOpen.value = false
  if (id === 'music') musicOpen.value = false
  if (activeTool.value === id) activeTool.value = null
}

function onRailClick(id) {
  if (id === 'ai') {
    closeAllModals()
    activeTool.value = 'ai'
    emit('open-ai-image')
    return
  }

  const toggles = {
    material: materialOpen,
    background: backgroundOpen,
    effect: effectOpen,
    music: musicOpen,
  }

  const target = toggles[id]
  if (!target) return

  const willOpen = !target.value
  closeAllModals()
  target.value = willOpen
  activeTool.value = willOpen ? id : null
}

function onMaterialAdd(payload) {
  emit('add-material', payload)
  closeModal('material')
}

function onBackgroundChange(color) {
  emit('canvas-bg-change', color)
}

function clearAiHighlight() {
  if (activeTool.value === 'ai') activeTool.value = null
}

defineExpose({ clearAiHighlight })
</script>
