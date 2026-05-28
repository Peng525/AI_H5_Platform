<template>
  <aside class="w-[240px] border-r border-outline-variant bg-surface-container-low flex flex-col shrink-0 overflow-hidden">
    <div class="p-3 border-b border-outline-variant flex items-center gap-2">
      <div class="w-8 h-8 rounded bg-primary-container text-on-primary-container flex items-center justify-center shrink-0">
        <span class="material-symbols-outlined text-[20px]">widgets</span>
      </div>
      <div class="min-w-0 flex-1">
        <div class="text-sm font-bold">工具箱</div>
        <div class="text-[10px] text-on-surface-variant">编辑器</div>
      </div>
      <button
        type="button"
        class="shrink-0 h-8 px-2.5 rounded-lg bg-primary text-on-primary text-xs font-medium inline-flex items-center gap-1 hover:bg-primary-container hover:text-on-primary-container transition-colors"
        title="快捷键说明 (F1)"
        @click="$emit('open-help')"
      >
        <span class="material-symbols-outlined text-[16px]">help</span>
        帮助
      </button>
    </div>

    <div class="flex border-b border-outline-variant">
      <button
        v-for="t in tabs"
        :key="t.id"
        class="flex-1 flex flex-col items-center py-2 text-[10px] transition-colors"
        :class="activeTab === t.id ? 'bg-surface-container-highest text-primary font-bold' : 'text-on-surface-variant hover:bg-surface-container'"
        @click="activeTab = t.id"
      >
        <span class="material-symbols-outlined text-[20px]" :style="activeTab === t.id ? { fontVariationSettings: '\'FILL\' 1' } : {}">{{ t.icon }}</span>
        {{ t.label }}
      </button>
    </div>

    <div class="flex-1 overflow-y-auto">
      <SlideThumbList
        v-if="activeTab === 'pages'"
        :slides="slides"
        :current-id="currentId"
        @select="$emit('select-slide', $event)"
        @add="$emit('add-slide')"
        @remove="$emit('remove-slide', $event)"
      />
      <SlideContentPanel
        v-else-if="activeTab === 'text'"
        :slide="currentSlide"
        @save="$emit('save-slide', $event)"
        @sync-canvas="$emit('sync-canvas')"
      />
      <SlideEffectPanel
        v-else-if="activeTab === 'effect'"
        :slide="currentSlide"
        :scroll-effect="scrollEffect"
        :project-settings="projectSettings"
        @save="$emit('save-slide', $event)"
        @scroll-change="$emit('scroll-change', $event)"
        @preview-animation="$emit('preview-animation', $event)"
        @bgm-change="$emit('bgm-change', $event)"
      />
      <MaterialPanel
        v-else-if="activeTab === 'material'"
        :canvas-background="canvasBackground"
        @add="$emit('add-material', $event)"
        @canvas-bg-change="$emit('canvas-bg-change', $event)"
      />
      <div v-else-if="activeTab === 'template'" class="p-4 text-sm">
        <p class="text-on-surface-variant mb-3">当前主题：{{ theme }}</p>
        <router-link to="/templates" class="block w-full py-2 text-center bg-primary text-on-primary rounded-lg text-sm">
          浏览更多模板
        </router-link>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import MaterialPanel from './MaterialPanel.vue'
import SlideContentPanel from './SlideContentPanel.vue'
import SlideEffectPanel from './SlideEffectPanel.vue'
import SlideThumbList from './SlideThumbList.vue'

defineProps({
  slides: { type: Array, default: () => [] },
  currentId: { type: Number, default: null },
  currentSlide: { type: Object, default: null },
  theme: { type: String, default: 'default' },
  scrollEffect: { type: String, default: 'page' },
  canvasBackground: { type: String, default: '#005daa' },
  projectSettings: { type: Object, default: null },
})

defineEmits(['select-slide', 'add-slide', 'remove-slide', 'save-slide', 'sync-canvas', 'add-material', 'canvas-bg-change', 'scroll-change', 'preview-animation', 'open-help', 'bgm-change'])

const activeTab = ref('pages')
const tabs = [
  { id: 'template', label: '模板', icon: 'dashboard' },
  { id: 'pages', label: '页面', icon: 'layers' },
  { id: 'text', label: '文本', icon: 'title' },
  { id: 'effect', label: '动效', icon: 'animation' },
  { id: 'material', label: '素材', icon: 'cloud_upload' },
]
</script>
