<template>
  <div class="h-36 overflow-hidden relative bg-[#eef0f4] flex items-center justify-center group-hover:bg-[#e8ebf0] transition-colors">
    <div
      v-if="hasCover"
      class="w-full h-full flex items-center justify-center transition-transform duration-500 group-hover:scale-[1.03]"
    >
      <SlideCanvasThumb
        :slide="coverSlide"
        :viewport="viewport"
        :project-id="null"
      />
    </div>
    <div
      v-else
      class="w-full h-full bg-gradient-to-br transition-transform duration-500 group-hover:scale-105"
      :class="template.cover_gradient || 'from-primary to-primary-container'"
    />
    <span class="absolute top-2 left-2 text-[10px] px-2 py-0.5 rounded-full bg-black/40 text-white z-10">
      {{ deviceLabel }}
    </span>
    <span
      v-if="template.featured"
      class="absolute top-2 right-2 text-[10px] px-2 py-0.5 rounded-full bg-amber-500 text-white z-10"
    >
      可试看
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import SlideCanvasThumb from './SlideCanvasThumb.vue'
import { getViewportPreset } from '../constants/editorPresets'

const props = defineProps({
  template: { type: Object, required: true },
})

const viewport = computed(() =>
  getViewportPreset(
    props.template.default_viewport || (props.template.device === 'web' ? 'web-1280' : 'mobile-375')
  )
)

const coverSlide = computed(() => {
  const slide = props.template.cover_slide
  if (!slide) return null
  return { id: 'cover', ...slide }
})

const hasCover = computed(() => {
  const slide = coverSlide.value
  if (!slide) return false
  if (slide.canvas_elements?.length) return true
  return !!(slide.title || slide.subtitle || slide.bullets?.length)
})

const deviceLabel = computed(() => (props.template.device === 'web' ? '网页版' : '移动端'))
</script>

<style scoped>
:deep(.slide-canvas-thumb-shell) {
  height: 100%;
  background: transparent;
}
</style>
