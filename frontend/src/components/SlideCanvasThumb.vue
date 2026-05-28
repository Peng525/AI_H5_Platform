<template>
  <div class="slide-canvas-thumb-shell">
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
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import PreviewSlideFrame from './PreviewSlideFrame.vue'
import { resolveSlideBackground } from '../composables/usePresentationPlayback'
import { resolvePreviewElements } from '../composables/useSlideCanvas'

const THUMB_MAX_W = 208
const THUMB_MAX_H = 128

const props = defineProps({
  slide: { type: Object, required: true },
  slideIndex: { type: Number, default: 0 },
  projectId: { type: [Number, String], default: null },
  viewport: { type: Object, required: true },
  projectSettings: { type: Object, default: null },
  liveSlideId: { type: Number, default: null },
  liveElements: { type: Array, default: null },
})

const scale = computed(() =>
  Math.min(THUMB_MAX_W / props.viewport.width, THUMB_MAX_H / props.viewport.height)
)

const scaledW = computed(() => Math.round(props.viewport.width * scale.value))
const scaledH = computed(() => Math.round(props.viewport.height * scale.value))

const resolvedElements = computed(() => {
  if (props.liveSlideId != null && props.slide?.id === props.liveSlideId && props.liveElements) {
    return props.liveElements
  }
  return resolvePreviewElements(props.projectId, props.slide)
})

const background = computed(() => {
  if (props.slide?.canvas_background) return props.slide.canvas_background
  return resolveSlideBackground(props.projectId, props.slide?.id, props.projectSettings)
})
</script>

<style scoped>
.slide-canvas-thumb-shell {
  width: 100%;
  height: 132px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eef0f4;
  padding: 4px;
}
.slide-canvas-thumb-box {
  overflow: hidden;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
}
.slide-canvas-thumb-inner {
  transform-origin: top left;
}
</style>
