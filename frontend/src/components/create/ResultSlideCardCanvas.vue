<template>
  <div
    class="mx-auto overflow-hidden"
    :class="fillCard ? 'w-full' : 'rounded-lg border border-outline-variant/50 bg-white shadow-sm'"
    :style="boxStyle"
  >
    <div class="origin-top-left" :style="innerScaleStyle">
      <PreviewSlideFrame
        v-show="!active"
        plain-card
        :animation="'none'"
        :enable-stagger="revealStagger"
        :viewport="viewport"
        :elements="previewElements"
        :canvas-background="canvasBackground"
        :slide="slide"
        :slide-index="slideIndex"
        :slide-total="slideTotal"
        :show-chrome="false"
      />
      <div
        v-show="active"
        class="relative overflow-hidden"
        :class="fillCard ? '' : 'rounded-lg bg-white'"
        :style="{ width: viewport.width + 'px', height: viewport.height + 'px', background: canvasBackground }"
        @click.stop
      >
        <div
          ref="canvasRef"
          data-editable-canvas
          class="absolute inset-0 overflow-hidden"
        >
          <div
            class="absolute inset-0 z-[1] cursor-crosshair"
            aria-hidden="true"
            @mousedown="onCanvasPointerDown"
          />
          <div
            v-if="marqueeRect"
            class="absolute z-[45] border-2 border-[#4a4a4a] bg-[#4a4a4a]/12 pointer-events-none rounded-sm"
            :style="marqueeStyle"
          />
          <CanvasElement
            v-for="(el, idx) in sortedElements"
            :key="el.id"
            :element="el"
            :selected="selectedIds.includes(el.id)"
            :scale="scale"
            :canvas-background="canvasBackground"
            :canvas-bounds="canvasBounds"
            :theme-id="themeId"
            :readonly="revealStagger"
            :stagger-index="revealStagger ? idx : -1"
            @select="$emit('select', $event)"
            @update="(id, patch) => $emit('update-element', id, patch)"
            @batch-start="(id) => $emit('batch-start', id)"
            @batch-end="$emit('batch-end')"
            @move-delta="$emit('move-delta', $event)"
            @edit-wordcloud="$emit('edit-wordcloud', $event)"
            @edit-chart-stack="$emit('edit-chart-stack', $event)"
            @text-edit-start="$emit('text-edit-start', $event)"
            @text-edit-end="$emit('text-edit-end', $event)"
          />
          <div
            v-if="chatScriptForPreview && !elements.length"
            class="absolute inset-0 z-10 pointer-events-none"
          >
            <DialoguePreviewCanvas :model-value="chatScriptForPreview" :editable="false" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import CanvasElement from '../CanvasElement.vue'
import PreviewSlideFrame from '../PreviewSlideFrame.vue'
import DialoguePreviewCanvas from '../dialogue/DialoguePreviewCanvas.vue'
import { normalizeChatScript } from '../../utils/chatScript.js'
import { useMarqueeSelect } from '../../composables/useMarqueeSelect.js'

const props = defineProps({
  active: { type: Boolean, default: false },
  fillCard: { type: Boolean, default: false },
  scale: { type: Number, required: true },
  viewport: { type: Object, required: true },
  previewElements: { type: Array, default: () => [] },
  elements: { type: Array, default: () => [] },
  selectedIds: { type: Array, default: () => [] },
  canvasBackground: { type: String, default: '' },
  themeId: { type: String, default: 'zjy-minimal' },
  slide: { type: Object, default: null },
  slideIndex: { type: Number, default: 0 },
  slideTotal: { type: Number, default: 1 },
  revealStagger: { type: Boolean, default: false },
})

const emit = defineEmits([
  'select',
  'deselect',
  'update-element',
  'marquee-select',
  'batch-start',
  'batch-end',
  'move-delta',
  'edit-wordcloud',
  'edit-chart-stack',
  'text-edit-start',
  'text-edit-end',
])

const canvasRef = ref(null)

function clientToCanvasLocal(clientX, clientY) {
  const el = canvasRef.value
  if (!el) return { x: 0, y: 0 }
  const rect = el.getBoundingClientRect()
  const lw = props.viewport.width || 1
  const lh = props.viewport.height || 1
  return {
    x: ((clientX - rect.left) / rect.width) * lw,
    y: ((clientY - rect.top) / rect.height) * lh,
  }
}

const { marqueeRect, onCanvasPointerDown } = useMarqueeSelect({
  clientToLocal: clientToCanvasLocal,
  getElements: () => props.elements,
  onDeselect: () => emit('deselect'),
  onMarqueeSelect: (payload) => emit('marquee-select', payload),
})

const boxStyle = computed(() => {
  if (props.fillCard) {
    return {
      width: '100%',
      height: `${Math.round(props.viewport.height * props.scale)}px`,
      aspectRatio: `${props.viewport.width} / ${props.viewport.height}`,
    }
  }
  return {
    width: `${Math.round(props.viewport.width * props.scale)}px`,
    height: `${Math.round(props.viewport.height * props.scale)}px`,
  }
})

const innerScaleStyle = computed(() => ({
  transform: `scale(${props.scale})`,
  transformOrigin: 'top left',
  width: `${props.viewport.width}px`,
  height: `${props.viewport.height}px`,
}))

const sortedElements = computed(() =>
  [...props.elements].sort((a, b) => (a.zIndex || 0) - (b.zIndex || 0))
)

const canvasBounds = computed(() => ({
  width: props.viewport.width,
  height: props.viewport.height,
}))

const chatScriptForPreview = computed(() => {
  if (!props.slide?.chat_script?.enabled) return null
  return normalizeChatScript(props.slide.chat_script)
})

const marqueeStyle = computed(() => {
  const r = marqueeRect.value
  if (!r) return {}
  return {
    left: `${r.x}px`,
    top: `${r.y}px`,
    width: `${r.w}px`,
    height: `${r.h}px`,
  }
})

function resolveElementEl(elementId) {
  if (!props.active || !canvasRef.value || elementId == null) return null
  return canvasRef.value.querySelector(`[data-element-id="${elementId}"]`)
}

defineExpose({ canvasRef, resolveElementEl })
</script>
