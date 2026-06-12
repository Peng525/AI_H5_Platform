<template>
  <div
    v-if="active"
    class="fixed inset-0 z-[60] pointer-events-none"
    aria-hidden="true"
  >
    <div
      v-if="brushStyle"
      class="absolute transition-all duration-300 ease-out pointer-events-none"
      :style="brushStyle"
    >
      <div class="relative -translate-x-1/2 -translate-y-1/2">
        <span
          class="material-symbols-outlined text-primary drop-shadow-md text-[32px] animate-pulse"
          style="font-variation-settings: 'FILL' 1"
        >
          draw
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  active: { type: Boolean, default: false },
  /** { slideId, elementId } */
  target: { type: Object, default: null },
  /** (slideId, elementId) => HTMLElement | null */
  resolveElementEl: { type: Function, default: null },
})

const brushStyle = ref(null)
let raf = null

function updatePosition() {
  if (!props.active || !props.target?.elementId || !props.resolveElementEl) {
    brushStyle.value = null
    return
  }
  const el = props.resolveElementEl(props.target.slideId, props.target.elementId)
  if (!el) {
    brushStyle.value = null
    return
  }
  const rect = el.getBoundingClientRect()
  brushStyle.value = {
    left: `${rect.left + rect.width * 0.85}px`,
    top: `${rect.top + rect.height * 0.15}px`,
  }
}

function scheduleUpdate() {
  if (raf) cancelAnimationFrame(raf)
  raf = requestAnimationFrame(updatePosition)
}

watch(
  () => [props.active, props.target?.elementId, props.target?.at],
  scheduleUpdate,
  { immediate: true }
)

onMounted(() => {
  window.addEventListener('scroll', scheduleUpdate, true)
  window.addEventListener('resize', scheduleUpdate)
})

onUnmounted(() => {
  if (raf) cancelAnimationFrame(raf)
  window.removeEventListener('scroll', scheduleUpdate, true)
  window.removeEventListener('resize', scheduleUpdate)
})

const active = computed(() => props.active)
</script>
