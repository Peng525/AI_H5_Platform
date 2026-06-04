<template>
  <div
    class="sticky top-0 z-10 shrink-0 border-b border-outline-variant/70 bg-white px-2 sm:px-3 py-2 space-y-2 shadow-sm"
  >
    <div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-on-surface-variant">
      <span class="font-medium text-on-surface shrink-0">
        正在编辑：第 {{ slideIndex + 1 }} 页
        <span v-if="slideLayout" class="text-on-surface-variant font-normal">· {{ slideLayout }}</span>
      </span>
    </div>
    <EditorCanvasToolbar
      :selected="selectedElement"
      :theme-id="themeId"
      :viewport-id="viewportId"
      :slide-id="slideId"
      :can-undo="canUndo"
      :can-redo="canRedo"
      @add-text="$emit('add-text')"
      @add-shape="$emit('add-shape')"
      @add-image="$emit('add-image')"
      @style-change="$emit('style-change', $event)"
      @duplicate="$emit('duplicate')"
      @delete="$emit('delete-selected')"
      @bring-front="$emit('bring-front')"
      @send-back="$emit('send-back')"
      @bring-forward="$emit('bring-forward')"
      @send-backward="$emit('send-backward')"
      @center-element="$emit('center-element', $event)"
      @image-fit="$emit('image-fit', $event)"
      @image-crop="$emit('image-crop')"
      @undo="$emit('undo')"
      @redo="$emit('redo')"
      @edit-chart-stack="$emit('edit-chart-stack')"
    />
    <div class="flex flex-wrap items-center gap-2 px-0.5">
      <span class="text-[10px] text-on-surface-variant shrink-0">页面背景</span>
      <button
        v-for="preset in canvasBgPresets"
        :key="preset.value"
        type="button"
        class="w-6 h-6 rounded-md border-2 transition-transform hover:scale-105"
        :class="canvasBackground === preset.value ? 'border-primary ring-1 ring-primary/30' : 'border-outline-variant/50'"
        :style="{ background: preset.value }"
        :title="preset.label"
        @click="$emit('canvas-bg-change', preset.value)"
      />
    </div>
  </div>
</template>

<script setup>
import EditorCanvasToolbar from '../EditorCanvasToolbar.vue'
import { CANVAS_BACKGROUND_PRESETS } from '../../constants/canvasBackgrounds.js'

defineProps({
  slideIndex: { type: Number, default: 0 },
  slideLayout: { type: String, default: '' },
  slideId: { type: [Number, String], default: '' },
  selectedElement: { type: Object, default: null },
  themeId: { type: String, default: 'zjy-minimal' },
  viewportId: { type: String, default: 'web-1280' },
  canvasBackground: { type: String, default: '' },
  canUndo: { type: Boolean, default: false },
  canRedo: { type: Boolean, default: false },
})

defineEmits([
  'add-text',
  'add-shape',
  'add-image',
  'style-change',
  'duplicate',
  'delete-selected',
  'bring-front',
  'send-back',
  'bring-forward',
  'send-backward',
  'center-element',
  'image-fit',
  'image-crop',
  'undo',
  'redo',
  'edit-chart-stack',
  'canvas-bg-change',
])

const canvasBgPresets = CANVAS_BACKGROUND_PRESETS
</script>
