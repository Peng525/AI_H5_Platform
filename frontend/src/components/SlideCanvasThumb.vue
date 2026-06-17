<template>
  <div
    ref="shellRef"
    class="slide-canvas-thumb-shell"
    :class="
      fillParent
        ? 'slide-canvas-thumb-shell--fill'
        : size === 'compact'
          ? 'slide-canvas-thumb-shell--compact'
          : 'slide-canvas-thumb-shell--default'
    "
  >
    <div
      class="slide-canvas-thumb-box"
      :style="{
        width: scaledW + 'px',
        height: scaledH + 'px',
      }"
    >
      <div
        class="slide-canvas-thumb-inner"
        :style="{
          width: viewport.width + 'px',
          height: viewport.height + 'px',
          transform: `scale(${scale})`,
        }"
      >
        <PreviewSlideFrame
          :viewport="viewport"
          :elements="resolvedElements"
          :canvas-background="background"
          :slide="slide"
          :slide-index="slideIndex"
          :slide-total="1"
          :show-chrome="false"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import PreviewSlideFrame from './PreviewSlideFrame.vue'
import { resolveSlideCanvasBackground } from '../utils/slideBackground.js'

const THUMB_SIZES = {
  default: { maxW: 208, maxH: 128, shellH: 132, pad: 4 },
  compact: { maxW: 112, maxH: 63, shellH: 72, pad: 2 },
}

const props = defineProps({
  slide: { type: Object, required: true },
  slideIndex: { type: Number, default: 0 },
  projectId: { type: [Number, String], default: null },
  viewport: { type: Object, required: true },
  projectSettings: { type: Object, default: null },
  liveSlideId: { type: Number, default: null },
  liveElements: { type: Array, default: null },
  size: { type: String, default: 'default', validator: (v) => ['default', 'compact'].includes(v) },
  fillParent: { type: Boolean, default: false },
})

const shellRef = ref(null)
const containerSize = ref({ width: 208, height: 128 })
let shellResizeObserver = null

const thumbSize = computed(() => THUMB_SIZES[props.size] || THUMB_SIZES.default)

const scale = computed(() => {
  const vw = props.viewport.width || 1
  const vh = props.viewport.height || 1
  if (props.fillParent) {
    const pad = 4
    const maxW = Math.max(1, containerSize.value.width - pad * 2)
    const maxH = Math.max(1, containerSize.value.height - pad * 2)
    return Math.min(maxW / vw, maxH / vh)
  }
  return Math.min(thumbSize.value.maxW / vw, thumbSize.value.maxH / vh)
})

const scaledW = computed(() => Math.round(props.viewport.width * scale.value))
const scaledH = computed(() => Math.round(props.viewport.height * scale.value))

const resolvedElements = computed(() => {
  if (props.liveSlideId != null && props.slide?.id === props.liveSlideId && props.liveElements) {
    return props.liveElements
  }
  if (props.slide?.canvas_elements?.length) return props.slide.canvas_elements
  return []
})

const background = computed(() =>
  resolveSlideCanvasBackground(props.projectId, props.slide, props.projectSettings)
)

function updateContainerSize() {
  const el = shellRef.value
  if (!el) return
  containerSize.value = {
    width: el.clientWidth || 208,
    height: el.clientHeight || 128,
  }
}

onMounted(() => {
  if (!props.fillParent) return
  updateContainerSize()
  if (shellRef.value && typeof ResizeObserver !== 'undefined') {
    shellResizeObserver = new ResizeObserver(updateContainerSize)
    shellResizeObserver.observe(shellRef.value)
  }
})

onUnmounted(() => {
  shellResizeObserver?.disconnect()
  shellResizeObserver = null
})
</script>

<style scoped>
.slide-canvas-thumb-shell {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eef0f4;
}
.slide-canvas-thumb-shell--default {
  height: 132px;
  padding: 4px;
}
.slide-canvas-thumb-shell--compact {
  height: 72px;
  padding: 2px;
}
.slide-canvas-thumb-shell--fill {
  width: 100%;
  height: 100%;
  padding: 4px;
  background: transparent;
}
.slide-canvas-thumb-box {
  overflow: hidden;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
}
.slide-canvas-thumb-shell--fill .slide-canvas-thumb-box {
  box-shadow: none;
  border-radius: 0;
}
.slide-canvas-thumb-inner {
  transform-origin: top left;
}
</style>
