<template>
  <div
    class="bg-white shadow-2xl overflow-hidden flex flex-col"
    :class="frameClass"
    :style="{ width: viewport.width + 'px', height: viewport.height + 'px' }"
  >
    <div v-if="viewport.device === 'mobile'" class="h-7 w-full flex justify-between items-center px-4 pt-1 shrink-0 bg-white">
      <span class="text-[12px] font-medium text-gray-900">9:41</span>
      <div class="flex gap-1 items-center opacity-80 text-gray-900">
        <span class="material-symbols-outlined text-[14px]">signal_cellular_alt</span>
        <span class="material-symbols-outlined text-[14px]">wifi</span>
        <span class="material-symbols-outlined text-[14px]">battery_full</span>
      </div>
    </div>
    <div v-else class="h-8 shrink-0 bg-gray-100 border-b border-gray-200 flex items-center px-3 gap-1.5">
      <span class="w-2.5 h-2.5 rounded-full bg-red-400" />
      <span class="w-2.5 h-2.5 rounded-full bg-amber-400" />
      <span class="w-2.5 h-2.5 rounded-full bg-green-400" />
      <span class="ml-2 text-[10px] text-gray-500 truncate flex-1">{{ viewport.label }}</span>
    </div>

    <div class="flex-1 relative overflow-hidden min-h-0" :style="{ background: canvasBackground }">
      <div class="absolute inset-0" :class="animClass">
        <CanvasElement
          v-for="(el, idx) in sortedElements"
          :key="el.id"
          :element="el"
          :readonly="true"
          :selected="false"
          :stagger-index="enableStagger ? idx : -1"
        />
        <div
          v-if="!elements.length && slide"
          class="absolute inset-0 p-6 text-white pointer-events-none"
        >
          <span class="text-xs opacity-80">{{ slideIndex + 1 }} / {{ slideTotal }}</span>
          <h2 class="text-xl font-bold mt-2">{{ slide.title }}</h2>
          <p v-if="slide.subtitle" class="text-sm mt-2 opacity-90">{{ slide.subtitle }}</p>
          <ul v-if="slide.bullets?.length" class="mt-4 space-y-2 text-sm">
            <li v-for="(b, j) in slide.bullets" :key="j">• {{ b }}</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import CanvasElement from './CanvasElement.vue'
import { animationEnterClass, getSlideAnimation } from '../utils/slideAnimation'

const props = defineProps({
  viewport: { type: Object, required: true },
  elements: { type: Array, default: () => [] },
  canvasBackground: { type: String, default: '#005daa' },
  slide: { type: Object, default: null },
  slideIndex: { type: Number, default: 0 },
  slideTotal: { type: Number, default: 1 },
  animation: { type: String, default: '' },
  enableStagger: { type: Boolean, default: false },
})

const frameClass = computed(() =>
  props.viewport.device === 'mobile'
    ? 'rounded-[2rem] border-[8px] border-gray-900'
    : 'rounded-lg border border-gray-300'
)

const sortedElements = computed(() =>
  [...props.elements].sort((a, b) => (a.zIndex || 0) - (b.zIndex || 0))
)

const animClass = computed(() => {
  const id = props.animation || getSlideAnimation(props.slide)
  return animationEnterClass(id)
})
</script>

<style scoped>
:deep(.canvas-stagger-in) {
  animation: canvasStaggerFade 0.45s ease both;
}

@keyframes canvasStaggerFade {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
