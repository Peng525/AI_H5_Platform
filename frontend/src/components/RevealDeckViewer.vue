<template>
  <div class="fixed inset-0 z-50 bg-black flex flex-col">
    <div class="absolute top-4 right-4 z-20 flex gap-2">
      <span class="text-white text-sm">{{ index + 1 }} / {{ slides.length }}</span>
      <button type="button" class="text-white text-sm px-3 py-1 rounded bg-white/10" @click="emit('exit')">退出 Reveal</button>
    </div>
    <div ref="deckRef" class="flex-1 flex items-center justify-center p-6">
      <div
        class="bg-white shadow-2xl overflow-hidden"
        :style="{ width: viewport.width + 'px', height: viewport.height + 'px', transform: `scale(${scale})` }"
      >
        <SlideTemplateRenderer v-if="current" :slide="current" class="w-full h-full" />
      </div>
    </div>
    <div class="shrink-0 flex justify-center gap-4 py-4 bg-black/80">
      <button type="button" class="text-white px-4 py-2 disabled:opacity-30" :disabled="index <= 0" @click="index--">上一页</button>
      <button type="button" class="text-white px-4 py-2 disabled:opacity-30" :disabled="index >= slides.length - 1" @click="index++">下一页</button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { DEFAULT_WEB_VIEWPORT_ID, getViewportPreset } from '../constants/editorPresets.js'
import SlideTemplateRenderer from '../slide-templates/SlideTemplateRenderer.vue'
import { resolveSlideStructured } from '../utils/compileStructuredSlide.js'

const props = defineProps({
  project: { type: Object, required: true },
})

const emit = defineEmits(['exit'])

const index = ref(0)
const scale = ref(1)
const deckRef = ref(null)

const settings = computed(() => props.project?.settings || {})
const viewport = computed(() => getViewportPreset(settings.value.viewportId || DEFAULT_WEB_VIEWPORT_ID))

const slides = computed(() =>
  (props.project?.slides || []).filter((s) => resolveSlideStructured(s))
)

const current = computed(() => slides.value[index.value] || null)

function onKey(e) {
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') {
    if (index.value < slides.value.length - 1) index.value++
  }
  if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
    if (index.value > 0) index.value--
  }
  if (e.key === 'Escape') emitExit()
}

function emitExit() {
  emit('exit')
}

function updateScale() {
  if (!deckRef.value) return
  const vw = deckRef.value.clientWidth - 48
  const vh = deckRef.value.clientHeight - 48
  scale.value = Math.min(1, vw / viewport.value.width, vh / viewport.value.height)
}

onMounted(() => {
  window.addEventListener('keydown', onKey)
  updateScale()
  window.addEventListener('resize', updateScale)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKey)
  window.removeEventListener('resize', updateScale)
})
</script>
