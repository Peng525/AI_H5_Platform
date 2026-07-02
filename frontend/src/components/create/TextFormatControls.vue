<template>
  <!-- 多根节点：直接作为父级 flex 子项，避免 contents 兼容问题导致换行 -->
  <select
    :value="currentFontId"
    class="text-xs border border-outline-variant rounded px-1 py-1 max-w-[88px] shrink-0"
    title="字体"
    @change="onStyle({ fontFamily: fontById($event.target.value) })"
  >
    <option v-for="f in FONT_FAMILIES" :key="f.id" :value="f.id">{{ f.label }}</option>
  </select>

  <select
    :value="selected.style?.fontSize || 16"
    class="text-xs border border-outline-variant rounded px-1 py-1 w-14 shrink-0"
    title="字号"
    @change="onStyle({ fontSize: Number($event.target.value) })"
  >
    <option v-for="s in FONT_SIZES" :key="s" :value="s">{{ s }}</option>
  </select>

  <button
    type="button"
    class="p-1.5 rounded hover:bg-surface-container shrink-0"
    :class="isBold ? 'bg-surface-container-high text-primary' : 'text-on-surface-variant'"
    title="加粗"
    @click="toggleBold"
  >
    <span class="material-symbols-outlined text-[18px] font-bold">format_bold</span>
  </button>

  <button
    type="button"
    class="p-1.5 rounded hover:bg-surface-container shrink-0"
    :class="textAlign === 'left' ? 'bg-surface-container-high text-primary' : 'text-on-surface-variant'"
    title="左对齐"
    @click="onStyle({ textAlign: 'left' })"
  >
    <span class="material-symbols-outlined text-[18px]">format_align_left</span>
  </button>
  <button
    type="button"
    class="p-1.5 rounded hover:bg-surface-container shrink-0"
    :class="textAlign === 'center' ? 'bg-surface-container-high text-primary' : 'text-on-surface-variant'"
    title="居中"
    @click="onStyle({ textAlign: 'center' })"
  >
    <span class="material-symbols-outlined text-[18px]">format_align_center</span>
  </button>
  <button
    type="button"
    class="p-1.5 rounded hover:bg-surface-container shrink-0"
    :class="textAlign === 'right' ? 'bg-surface-container-high text-primary' : 'text-on-surface-variant'"
    title="右对齐"
    @click="onStyle({ textAlign: 'right' })"
  >
    <span class="material-symbols-outlined text-[18px]">format_align_right</span>
  </button>

  <select
    class="text-xs border border-outline-variant rounded px-1 py-1 max-w-[72px] shrink-0"
    title="样式"
    @change="applyStylePreset($event.target.value)"
  >
    <option value="" disabled selected hidden>样式</option>
    <option v-for="(p, key) in themePresets" :key="key" :value="key">{{ p.label }}</option>
  </select>

  <select
    :value="lineHeightValue"
    class="text-xs border border-outline-variant rounded px-1 py-1 w-[68px] shrink-0"
    title="间距"
    @change="onStyle({ lineHeight: Number($event.target.value) })"
  >
    <option v-for="lh in LINE_HEIGHTS" :key="lh.value" :value="lh.value">{{ lh.label }}</option>
  </select>

  <WordColorPicker
    class="shrink-0"
    compact
    :model-value="selected.style?.color || '#1b1b1c'"
    :context-key="colorPickerContextKey"
    label="字体颜色"
    icon="format_color_text"
    @change="onStyle({ color: $event })"
  />
  <WordColorPicker
    class="shrink-0"
    compact
    :model-value="selected.style?.background || '#ffffff'"
    :context-key="colorPickerContextKey"
    label="背景颜色"
    icon="format_color_fill"
    @change="onStyle({ background: $event })"
  />
</template>

<script setup>
import { computed } from 'vue'
import {
  FONT_FAMILIES,
  FONT_SIZES,
  LINE_HEIGHTS,
  getThemeTextPresets,
} from '../../constants/textFormats'
import WordColorPicker from '../WordColorPicker.vue'

const props = defineProps({
  selected: { type: Object, required: true },
  themeId: { type: String, default: 'zjy-minimal' },
  viewportId: { type: String, default: 'mobile-375' },
  slideId: { type: [String, Number], default: '' },
})

const emit = defineEmits(['style-change'])

const LINE_HEIGHT_OPTIONS = LINE_HEIGHTS.map((o) => o.value)

const isBold = computed(() => {
  const w = props.selected?.style?.fontWeight
  return w === 'bold' || w === '700' || w === 700
})

const textAlign = computed(() => props.selected?.style?.textAlign || 'left')
const themePresets = computed(() => getThemeTextPresets(props.themeId, props.viewportId))
const colorPickerContextKey = computed(() => `${props.viewportId}:${props.slideId}:${props.selected?.id || ''}`)

const lineHeightValue = computed(() => {
  const raw = props.selected?.style?.lineHeight
  if (raw == null || raw === '') return 1
  const n = Number(raw)
  if (LINE_HEIGHT_OPTIONS.includes(n)) return n
  return LINE_HEIGHT_OPTIONS.reduce((best, v) =>
    (Math.abs(v - n) < Math.abs(best - n) ? v : best), 1)
})

const currentFontId = computed(() => {
  const ff = props.selected?.style?.fontFamily || ''
  const found = FONT_FAMILIES.find((f) => f.value === ff || ff.includes(f.label))
  return found?.id || 'yahei'
})

function fontById(id) {
  return FONT_FAMILIES.find((f) => f.id === id)?.value || FONT_FAMILIES[0].value
}

function onStyle(patch) {
  emit('style-change', patch)
}

function toggleBold() {
  onStyle({ fontWeight: isBold.value ? 'normal' : 'bold' })
}

function applyStylePreset(key) {
  const preset = themePresets.value[key]
  if (preset) onStyle({ ...preset.style })
}
</script>
