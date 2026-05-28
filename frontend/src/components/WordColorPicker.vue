<template>
  <div ref="rootRef" class="relative">
    <button
      type="button"
      class="flex flex-col items-center gap-0.5 p-1 rounded hover:bg-surface-container"
      :title="label"
      @click.stop="open = !open"
    >
      <span class="material-symbols-outlined text-[18px] text-on-surface-variant">{{ icon }}</span>
      <span
        class="w-5 h-1 rounded-sm border border-outline-variant/50"
        :style="{ background: modelValue || '#000000' }"
      />
    </button>

    <div
      v-show="open"
      class="absolute top-full left-0 mt-1 pt-1 z-[70]"
      @click.stop
    >
      <div class="bg-white border border-outline-variant rounded-lg shadow-lg p-3 w-[220px] text-xs">
        <p class="text-on-surface-variant mb-1.5 font-medium">主题颜色</p>
        <div class="grid grid-cols-8 gap-1 mb-3">
          <button
            v-for="c in THEME_COLORS"
            :key="'t-' + c"
            type="button"
            class="w-5 h-5 rounded-sm border border-black/10 hover:scale-110 transition-transform"
            :style="{ background: c }"
            :title="c"
            @click="pick(c)"
          />
        </div>
        <p class="text-on-surface-variant mb-1.5 font-medium">标准色</p>
        <div class="grid grid-cols-8 gap-1 mb-3">
          <button
            v-for="c in STANDARD_COLORS"
            :key="'s-' + c"
            type="button"
            class="w-5 h-5 rounded-sm border border-black/10 hover:scale-110 transition-transform"
            :class="c === '#FFFFFF' ? 'ring-1 ring-inset ring-gray-300' : ''"
            :style="{ background: c }"
            :title="c"
            @click="pick(c)"
          />
        </div>
        <div class="flex items-center gap-2 pt-2 border-t border-outline-variant">
          <span class="text-on-surface-variant shrink-0">其他</span>
          <input
            type="color"
            :value="modelValue || '#000000'"
            class="w-8 h-8 border-0 cursor-pointer p-0"
            @input="pick($event.target.value)"
          />
          <input
            :value="hexInput"
            type="text"
            maxlength="7"
            placeholder="#000000"
            class="flex-1 border border-outline-variant rounded px-1.5 py-1 text-[11px] uppercase"
            @change="pickHex"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { STANDARD_COLORS, THEME_COLORS } from '../constants/textFormats'

const props = defineProps({
  modelValue: { type: String, default: '#000000' },
  label: { type: String, default: '字体颜色' },
  icon: { type: String, default: 'format_color_text' },
})

const emit = defineEmits(['update:modelValue', 'change'])

const open = ref(false)
const rootRef = ref(null)
const hexInput = ref(props.modelValue || '#000000')

watch(
  () => props.modelValue,
  (v) => {
    hexInput.value = v || '#000000'
  }
)

function pick(c) {
  hexInput.value = c
  emit('update:modelValue', c)
  emit('change', c)
  open.value = false
}

function pickHex(e) {
  let v = e.target.value.trim()
  if (!v.startsWith('#')) v = `#${v}`
  if (/^#[0-9A-Fa-f]{6}$/.test(v)) pick(v)
}

function onDocDown(e) {
  if (!open.value) return
  if (rootRef.value?.contains(e.target)) return
  open.value = false
}

onMounted(() => document.addEventListener('mousedown', onDocDown))
onUnmounted(() => document.removeEventListener('mousedown', onDocDown))
</script>
