<template>
  <div ref="rootRef" class="relative inline-flex">
    <button
      type="button"
      class="inline-flex items-center gap-1.5 rounded-full border border-outline-variant bg-white pl-2.5 pr-7 py-0.5 text-xs leading-5 text-on-surface hover:bg-surface-container-low/50 transition"
      @click.stop="open = !open"
    >
      <span
        class="inline-block shrink-0 border border-on-surface/60 rounded-sm"
        :style="iconStyle(selectedOpt.iconW, selectedOpt.iconH)"
      />
      <span>{{ selectedOpt.label }}</span>
      <span class="material-symbols-outlined absolute right-1.5 text-[15px] text-on-surface-variant pointer-events-none">
        expand_more
      </span>
    </button>
    <div
      v-if="open"
      class="absolute left-0 top-full mt-1 z-50 min-w-[9rem] bg-white border border-outline-variant rounded-xl shadow-lg py-1"
    >
      <button
        v-for="opt in IMAGE_RATIO_OPTIONS"
        :key="opt.value"
        type="button"
        class="w-full flex items-center gap-2 px-3 py-2 text-xs text-on-surface hover:bg-surface-container-low/60 transition text-left"
        @click="pick(opt.value)"
      >
        <span class="w-4 shrink-0 flex justify-center">
          <span
            v-if="modelValue === opt.value"
            class="material-symbols-outlined text-[16px] text-primary"
          >check</span>
        </span>
        <span
          class="inline-block shrink-0 border border-on-surface/60 rounded-sm"
          :style="iconStyle(opt.iconW, opt.iconH)"
        />
        <span>{{ opt.label }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import {
  IMAGE_RATIO_OPTIONS,
  getImageRatioOption,
  scaleRatioIcon,
} from '../../constants/imageGenerateOptions.js'

const props = defineProps({
  modelValue: { type: String, default: '9:16' },
})

const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const rootRef = ref(null)

const selectedOpt = computed(() => getImageRatioOption(props.modelValue))

function iconStyle(iconW, iconH) {
  const { width, height } = scaleRatioIcon(iconW, iconH)
  return { width: `${width}px`, height: `${height}px` }
}

function pick(value) {
  emit('update:modelValue', value)
  open.value = false
}

function onDocClick(e) {
  if (!open.value) return
  if (rootRef.value && !rootRef.value.contains(e.target)) {
    open.value = false
  }
}

onMounted(() => document.addEventListener('click', onDocClick))
onUnmounted(() => document.removeEventListener('click', onDocClick))
</script>
