<template>
  <div
    v-if="selectedElement"
    class="shrink-0 border-b border-outline-variant/70 bg-white px-2 sm:px-3 py-2 shadow-sm"
  >
    <EditorCanvasToolbar
      hide-base-bar
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
      @delete-selected="$emit('delete-selected')"
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
  </div>
</template>

<script setup>
import { DEFAULT_WEB_VIEWPORT_ID } from '../../constants/editorPresets.js'
import EditorCanvasToolbar from '../EditorCanvasToolbar.vue'

defineProps({
  slideId: { type: [Number, String], default: '' },
  selectedElement: { type: Object, default: null },
  themeId: { type: String, default: 'zjy-minimal' },
  viewportId: { type: String, default: DEFAULT_WEB_VIEWPORT_ID },
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
])
</script>
