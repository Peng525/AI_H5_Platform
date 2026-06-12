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
        class="relative overflow-visible"
        :class="fillCard ? '' : 'rounded-lg bg-white'"
        :style="{ width: viewport.width + 'px', height: viewport.height + 'px', background: canvasBackground }"
        @click.stop
      >
        <div
          ref="canvasRef"
          class="absolute inset-0 overflow-visible"
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
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import CanvasElement from '../CanvasElement.vue'
import PreviewSlideFrame from '../PreviewSlideFrame.vue'

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
])

const canvasRef = ref(null)
const marqueeRect = ref(null)

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

function elementIntersectsRect(el, rect) {
  const ex = el.x ?? 0
  const ey = el.y ?? 0
  const ew = el.width ?? 0
  const eh = el.height ?? 0
  return !(ex + ew < rect.x || rect.x + rect.w < ex || ey + eh < rect.y || rect.y + rect.h < ey)
}

function onCanvasPointerDown(e) {
  if (e.button !== 0) return
  e.preventDefault()
  e.stopPropagation()

  const startClient = { x: e.clientX, y: e.clientY }
  const startLocal = clientToCanvasLocal(startClient.x, startClient.y)
  let dragging = false
  const DRAG_THRESHOLD = 4

  marqueeRect.value = { x: startLocal.x, y: startLocal.y, w: 0, h: 0 }

  function onMove(ev) {
    const dx = ev.clientX - startClient.x
    const dy = ev.clientY - startClient.y
    if (!dragging && Math.hypot(dx, dy) < DRAG_THRESHOLD) return
    dragging = true
    const cur = clientToCanvasLocal(ev.clientX, ev.clientY)
    const x = Math.min(startLocal.x, cur.x)
    const y = Math.min(startLocal.y, cur.y)
    marqueeRect.value = {
      x,
      y,
      w: Math.abs(cur.x - startLocal.x),
      h: Math.abs(cur.y - startLocal.y),
    }
  }

  function onUp(ev) {
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
    const rect = marqueeRect.value
    marqueeRect.value = null

    if (!dragging) {
      emit('deselect')
      return
    }

    if (!rect || rect.w < 2 || rect.h < 2) {
      emit('deselect')
      return
    }

    const ids = props.elements.filter((el) => elementIntersectsRect(el, rect)).map((el) => el.id)
    emit('marquee-select', {
      ids,
      additive: ev.ctrlKey || ev.metaKey || ev.shiftKey,
    })
  }

  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

defineExpose({ canvasRef })
</script>
