<template>
  <div class="h-36 overflow-hidden relative bg-[#eef0f4] flex items-center justify-center group-hover:bg-[#e8ebf0] transition-colors">
    <div
      v-if="hasCover"
      class="w-full h-full flex items-center justify-center transition-transform duration-500 group-hover:scale-[1.03]"
    >
      <SlideCanvasThumb
        :slide="coverSlide"
        :viewport="viewport"
        :project-id="project.id"
        :project-settings="project.settings"
      />
    </div>
    <div
      v-else
      class="w-full h-full bg-gradient-to-br from-slate-200 to-slate-300 flex items-center justify-center transition-transform duration-500 group-hover:scale-105"
    >
      <span class="material-symbols-outlined text-4xl text-slate-400/80">slideshow</span>
    </div>
    <span class="absolute top-2 left-2 text-[10px] px-2 py-0.5 rounded-full bg-black/40 text-white z-10">
      {{ deviceLabel }}
    </span>
    <span class="absolute bottom-2 left-2 text-[10px] px-2 py-0.5 rounded-full bg-black/40 text-white z-10">
      {{ slideCount }} 页
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import SlideCanvasThumb from './SlideCanvasThumb.vue'
import { getViewportPreset } from '../constants/editorPresets'

const props = defineProps({
  project: { type: Object, required: true },
})

const viewport = computed(() =>
  getViewportPreset(props.project.settings?.viewportId || 'mobile-375')
)

const coverSlide = computed(() => {
  const slides = props.project.slides || []
  if (!slides.length) return null
  return slides[0]
})

const hasCover = computed(() => {
  const slide = coverSlide.value
  if (!slide) return false
  if (slide.canvas_elements?.length) return true
  return !!(slide.title || slide.subtitle || slide.bullets?.length)
})

const deviceLabel = computed(() => {
  const id = props.project.settings?.viewportId || 'mobile-375'
  return id.startsWith('web') ? '网页版' : '移动端'
})

const slideCount = computed(() => props.project.slides?.length || 0)
</script>

<style scoped>
:deep(.slide-canvas-thumb-shell) {
  height: 100%;
  background: transparent;
}
</style>
