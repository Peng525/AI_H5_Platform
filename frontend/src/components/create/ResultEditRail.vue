<template>
  <div class="flex shrink-0 min-h-0 h-full">
    <ResultToolDrawer
      :open="drawerOpen"
      :title="activeTitle"
      @close="closeDrawer"
      @after-leave="onDrawerAfterLeave"
    >
      <MaterialPanel
        v-if="activeTool === 'material'"
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

      <CanvasBackgroundPicker
        v-else-if="activeTool === 'background'"
        class="p-4"
        :canvas-background="canvasBackground"
        :theme-id="projectSettings?.themeId || 'zjy-minimal'"
        @canvas-bg-change="onBackgroundChange"
      />

      <SlideEffectPanel
        v-else-if="activeTool === 'effect'"
        class="p-3"
        :slide="currentSlide"
        :scroll-effect="scrollEffect"
        @save="emit('save-slide', $event)"
        @scroll-change="emit('scroll-change', $event)"
        @preview-animation="emit('preview-animation', $event)"
      />

      <BgmPanel
        v-else-if="activeTool === 'music'"
        class="p-3"
        :project-settings="projectSettings"
        @bgm-change="emit('bgm-change', $event)"
      />

      <AiPanel
        v-else-if="activeTool === 'ai'"
        ref="aiPanelRef"
        :image-loading="imageLoading"
        :quota-remaining="quotaRemaining"
        :quota-total="quotaTotal"
        :canvas-viewport-id="canvasViewportId"
        class="result-ai-panel !w-full !max-w-none !border-0 !h-full min-h-0"
        @generate-image="emit('generate-image', $event)"
        @add-image-to-page="emit('add-image-to-page', $event)"
      />

      <template v-else-if="activeTool === 'chart'">
        <ChartEditorPanel
          ref="chartPanelRef"
          :mode="chartEditMode"
          :initial-content="chartEditContent"
          :chart-color="chartColor"
          @save="onChartSave"
        />
        <div class="px-3 pb-4 pt-2 border-t border-outline-variant/60 shrink-0">
          <button
            type="button"
            class="w-full py-2 text-sm font-medium bg-primary text-on-primary rounded-lg hover:opacity-90"
            @click="onChartSaveClick"
          >
            保存
          </button>
        </div>
      </template>
    </ResultToolDrawer>

    <aside class="w-14 sm:w-[3.75rem] border-l border-outline-variant/60 bg-surface-container-lowest flex flex-col justify-center shrink-0 h-full min-h-0 py-3">
      <div class="flex flex-col items-center gap-2 px-1.5">
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
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import AiPanel from '../AiPanel.vue'
import BgmPanel from '../BgmPanel.vue'
import CanvasBackgroundPicker from '../CanvasBackgroundPicker.vue'
import MaterialPanel from '../MaterialPanel.vue'
import SlideEffectPanel from '../SlideEffectPanel.vue'
import ChartEditorPanel from '../charts/ChartEditorPanel.vue'
import ResultToolDrawer from './ResultToolDrawer.vue'

const props = defineProps({
  currentSlide: { type: Object, default: null },
  canvasBackground: { type: String, default: '' },
  projectSettings: { type: Object, default: null },
  scrollEffect: { type: String, default: 'page' },
  primaryLayouts: { type: Array, default: null },
  moreLayouts: { type: Array, default: null },
  imageLoading: { type: Boolean, default: false },
  quotaRemaining: { type: Number, default: 0 },
  quotaTotal: { type: Number, default: 0 },
  canvasViewportId: { type: String, default: 'mobile-375' },
  chartEditorActive: { type: Boolean, default: false },
  chartEditMode: { type: String, default: 'chartStack' },
  chartEditContent: { type: Object, default: null },
  chartColor: { type: String, default: '#005daa' },
})

const emit = defineEmits([
  'add-material',
  'canvas-bg-change',
  'apply-layout',
  'open-dialogue-generator',
  'open-wordcloud-editor',
  'save-slide',
  'scroll-change',
  'preview-animation',
  'bgm-change',
  'generate-image',
  'add-image-to-page',
  'save-chart',
  'close-chart-editor',
])

const activeTool = ref(null)
const drawerOpen = ref(false)
const aiPanelRef = ref(null)
const chartPanelRef = ref(null)

const railItems = [
  { id: 'material', label: '素材', icon: 'cloud_upload' },
  { id: 'background', label: '页面背景', icon: 'palette' },
  { id: 'effect', label: '动效', icon: 'animation' },
  { id: 'music', label: '音乐', icon: 'music_note' },
  { id: 'ai', label: 'AI 生图', icon: 'image' },
]

const toolTitles = {
  material: '素材',
  background: '页面背景',
  effect: '动效',
  music: '音乐',
  ai: 'AI 生图',
  chart: '编辑图表',
}

const activeTitle = computed(() => {
  if (activeTool.value === 'chart') {
    return props.chartEditMode === 'chartStack' ? '编辑图表卡组' : '编辑图表'
  }
  return toolTitles[activeTool.value] || ''
})

watch(
  () => props.chartEditorActive,
  (active, wasActive) => {
    if (active) {
      activeTool.value = 'chart'
      drawerOpen.value = true
    } else if (wasActive && drawerOpen.value) {
      activeTool.value = 'material'
    }
  }
)

function iconClass(id) {
  const active = activeTool.value === id && drawerOpen.value
  if (active) {
    return 'bg-primary/12 text-primary shadow-[0_2px_8px_rgba(59,130,246,0.22),0_0_0_1px_rgba(59,130,246,0.25)] ring-2 ring-primary/30'
  }
  return 'bg-white text-on-surface-variant shadow-[0_1px_3px_rgba(0,0,0,0.1),0_0_0_1px_rgba(0,0,0,0.06)] hover:shadow-md hover:text-on-surface'
}

function closeDrawer() {
  if (activeTool.value === 'chart') {
    emit('close-chart-editor')
  }
  drawerOpen.value = false
}

function onDrawerAfterLeave() {
  activeTool.value = null
}

function onRailClick(id) {
  if (activeTool.value === 'chart') {
    emit('close-chart-editor')
    activeTool.value = id
    drawerOpen.value = true
    return
  }
  if (activeTool.value === id && drawerOpen.value) {
    closeDrawer()
    return
  }
  activeTool.value = id
  drawerOpen.value = true
}

function onMaterialAdd(payload) {
  emit('add-material', payload)
}

function onBackgroundChange(color) {
  emit('canvas-bg-change', color)
}

function onChartSave(content) {
  emit('save-chart', content)
}

function onChartSaveClick() {
  chartPanelRef.value?.save()
}

function setGeneratedImage(result) {
  aiPanelRef.value?.setGeneratedImage(result)
}

function setImageError(msg) {
  aiPanelRef.value?.setImageError(msg)
}

defineExpose({ setGeneratedImage, setImageError })
</script>

<style scoped>
:deep(.editor-ai-panel) {
  width: 100%;
  max-width: none;
  border: none;
  height: 100%;
}
</style>
