<template>
  <div
    class="overflow-hidden flex flex-col"
    :class="rootShellClass"
    :style="rootStyle"
  >
    <div v-if="showChrome && viewport.device === 'mobile'" class="h-7 w-full flex justify-between items-center px-4 pt-1 shrink-0 bg-white">
      <span class="text-[12px] font-medium text-gray-900">9:41</span>
      <div class="flex gap-1 items-center opacity-80 text-gray-900">
        <span class="material-symbols-outlined text-[14px]">signal_cellular_alt</span>
        <span class="material-symbols-outlined text-[14px]">wifi</span>
        <span class="material-symbols-outlined text-[14px]">battery_full</span>
      </div>
    </div>
    <div v-else-if="showChrome" class="h-8 shrink-0 bg-gray-100 border-b border-gray-200 flex items-center px-3 gap-1.5">
      <span class="w-2.5 h-2.5 rounded-full bg-red-400" />
      <span class="w-2.5 h-2.5 rounded-full bg-amber-400" />
      <span class="w-2.5 h-2.5 rounded-full bg-green-400" />
      <span class="ml-2 text-[10px] text-gray-500 truncate flex-1">{{ viewport.label }}</span>
    </div>

    <div class="flex-1 relative overflow-hidden min-h-0" :style="{ background: canvasBackground }">
      <div class="absolute inset-0" :class="animClass">
        <template v-if="elements.length">
          <CanvasElement
            v-for="(el, idx) in sortedElements"
            :key="el.id"
            :element="el"
            :readonly="true"
            :selected="false"
            :stagger-index="enableStagger ? idx : -1"
          />
        </template>
        <div
          v-else-if="structuredSlide"
          class="absolute inset-0 overflow-hidden pointer-events-none"
        >
          <SlideTemplateRenderer :slide="slide" class="w-full h-full" />
        </div>
        <div
          v-else-if="slide"
          class="absolute inset-0 p-6 sm:p-10 pointer-events-none flex items-start justify-center"
        >
          <div
            v-if="directTextOnCanvas"
            class="w-full max-w-[92%] text-left"
            :style="{ color: directTextColor }"
          >
            <span class="text-xs opacity-60">{{ slideIndex + 1 }} / {{ slideTotal }}</span>
            <h2 class="text-xl sm:text-2xl font-bold mt-2">{{ slide.title }}</h2>
            <p v-if="slide.subtitle" class="text-sm sm:text-base mt-2 opacity-85">{{ slide.subtitle }}</p>
          </div>
          <div
            v-else
            class="w-full max-w-[92%] rounded-xl bg-white/92 backdrop-blur-sm shadow-sm border border-black/5 p-5 text-gray-900"
          >
            <span class="text-xs text-gray-500">{{ slideIndex + 1 }} / {{ slideTotal }}</span>
            <h2 class="text-xl font-bold mt-2 text-gray-900">{{ slide.title }}</h2>
            <p v-if="slide.subtitle" class="text-sm mt-2 text-gray-700">{{ slide.subtitle }}</p>
          </div>
        </div>
        <BgmPlayerButton
          v-if="showBgmPlayer"
          class="absolute top-2 right-2 z-30"
          :muted="bgmMuted"
          :spinning="bgmSpinning"
          @toggle="$emit('toggle-bgm-mute')"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import CanvasElement from './CanvasElement.vue'
import BgmPlayerButton from './BgmPlayerButton.vue'
import { animationEnterClass, getSlideAnimation } from '../utils/slideAnimation'
import { DEFAULT_CANVAS_BG } from '../constants/canvasBackgrounds.js'
import { isLightSlideBackground, textColorForSlideBackground } from '../utils/slideBackground.js'
import SlideTemplateRenderer from '../slide-templates/SlideTemplateRenderer.vue'
import { resolveSlideStructured } from '../utils/compileStructuredSlide.js'

const props = defineProps({
  viewport: { type: Object, required: true },
  elements: { type: Array, default: () => [] },
  canvasBackground: { type: String, default: DEFAULT_CANVAS_BG },
  slide: { type: Object, default: null },
  slideIndex: { type: Number, default: 0 },
  slideTotal: { type: Number, default: 1 },
  animation: { type: String, default: '' },
  enableStagger: { type: Boolean, default: false },
  showBgmPlayer: { type: Boolean, default: false },
  bgmMuted: { type: Boolean, default: false },
  bgmSpinning: { type: Boolean, default: false },
  showChrome: { type: Boolean, default: true },
  plainCard: { type: Boolean, default: false },
})

defineEmits(['toggle-bgm-mute'])

const rootShellClass = computed(() => {
  if (props.plainCard || !props.showChrome) {
    return 'w-full h-full overflow-hidden'
  }
  if (props.showChrome && props.viewport.device === 'mobile') {
    return 'bg-white shadow-2xl rounded-[2rem] border-[8px] border-gray-900'
  }
  return 'bg-white shadow-2xl rounded-lg border border-gray-300'
})

const rootStyle = computed(() => ({
  width: `${props.viewport.width}px`,
  height: `${props.viewport.height}px`,
}))

const directTextOnCanvas = computed(
  () => !props.elements.length && props.slide && isLightSlideBackground(props.canvasBackground)
)

const directTextColor = computed(() => textColorForSlideBackground(props.canvasBackground))

const structuredSlide = computed(
  () => !props.elements.length && props.slide && resolveSlideStructured(props.slide)
)

const sortedElements = computed(() =>
  [...props.elements].sort((a, b) => (a.zIndex || 0) - (b.zIndex || 0))
)

const animClass = computed(() => {
  if (props.animation === 'none') return ''
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
