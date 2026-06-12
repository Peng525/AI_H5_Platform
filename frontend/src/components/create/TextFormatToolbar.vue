<template>
  <div
    v-if="visible && selected"
    data-editor-chrome
    class="flex items-center gap-0.5 sm:gap-1 flex-wrap bg-white shadow-lg rounded-lg px-1.5 sm:px-2 py-1.5 border border-outline-variant pointer-events-auto"
    :style="barStyle"
    @mousedown.stop
  >
    <select
      :value="currentFontId"
      class="text-xs border border-outline-variant rounded px-1 py-1 max-w-[88px]"
      title="字体"
      @change="onStyle({ fontFamily: fontById($event.target.value) })"
    >
      <option v-for="f in FONT_FAMILIES" :key="f.id" :value="f.id">{{ f.label }}</option>
    </select>

    <select
      :value="selected.style?.fontSize || 16"
      class="text-xs border border-outline-variant rounded px-1 py-1 w-14"
      title="字号"
      @change="onStyle({ fontSize: Number($event.target.value) })"
    >
      <option v-for="s in FONT_SIZES" :key="s" :value="s">{{ s }}</option>
    </select>

    <button
      type="button"
      class="p-1.5 rounded hover:bg-surface-container"
      :class="isBold ? 'bg-surface-container-high text-primary' : 'text-on-surface-variant'"
      title="加粗"
      @click="toggleBold"
    >
      <span class="material-symbols-outlined text-[18px] font-bold">format_bold</span>
    </button>

    <button
      type="button"
      class="p-1.5 rounded hover:bg-surface-container"
      :class="textAlign === 'left' ? 'bg-surface-container-high text-primary' : 'text-on-surface-variant'"
      title="左对齐"
      @click="onStyle({ textAlign: 'left' })"
    >
      <span class="material-symbols-outlined text-[18px]">format_align_left</span>
    </button>
    <button
      type="button"
      class="p-1.5 rounded hover:bg-surface-container"
      :class="textAlign === 'center' ? 'bg-surface-container-high text-primary' : 'text-on-surface-variant'"
      title="居中"
      @click="onStyle({ textAlign: 'center' })"
    >
      <span class="material-symbols-outlined text-[18px]">format_align_center</span>
    </button>
    <button
      type="button"
      class="p-1.5 rounded hover:bg-surface-container"
      :class="textAlign === 'right' ? 'bg-surface-container-high text-primary' : 'text-on-surface-variant'"
      title="右对齐"
      @click="onStyle({ textAlign: 'right' })"
    >
      <span class="material-symbols-outlined text-[18px]">format_align_right</span>
    </button>

    <select
      class="text-xs border border-outline-variant rounded px-1 py-1 max-w-[72px]"
      title="主题样式"
      @change="applyThemePreset($event.target.value)"
    >
      <option value="" disabled selected hidden>主题</option>
      <option v-for="(p, key) in themePresets" :key="'th-' + key" :value="key">{{ p.label }}</option>
    </select>

    <select
      :value="selected.style?.lineHeight ?? 1.5"
      class="text-xs border border-outline-variant rounded px-1 py-1 max-w-[72px]"
      title="行距"
      @change="onStyle({ lineHeight: Number($event.target.value) })"
    >
      <option v-for="lh in LINE_HEIGHTS" :key="lh.value" :value="lh.value">行距 {{ lh.label }}</option>
    </select>

    <WordColorPicker
      :model-value="selected.style?.color || '#1b1b1c'"
      :context-key="colorPickerContextKey"
      label="字体颜色"
      icon="format_color_text"
      @change="onStyle({ color: $event })"
    />
    <WordColorPicker
      :model-value="selected.style?.background || '#ffffff'"
      :context-key="colorPickerContextKey"
      label="背景颜色"
      icon="format_color_fill"
      @change="onStyle({ background: $event })"
    />
  </div>
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
import { floatingBarStyle } from '../../composables/useElementAnchor.js'

const props = defineProps({
  selected: { type: Object, default: null },
  visible: { type: Boolean, default: false },
  anchorRect: { type: Object, default: null },
  themeId: { type: String, default: 'zjy-minimal' },
  viewportId: { type: String, default: 'mobile-375' },
  slideId: { type: [String, Number], default: '' },
})

const emit = defineEmits(['style-change'])

const barStyle = computed(() => floatingBarStyle(props.anchorRect, 'above', 10))

const isBold = computed(() => {
  const w = props.selected?.style?.fontWeight
  return w === 'bold' || w === '700' || w === 700
})

const textAlign = computed(() => props.selected?.style?.textAlign || 'left')
const themePresets = computed(() => getThemeTextPresets(props.themeId, props.viewportId))
const colorPickerContextKey = computed(() => `${props.viewportId}:${props.slideId}:${props.selected?.id || ''}`)

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

function applyThemePreset(key) {
  const preset = themePresets.value[key]
  if (preset) onStyle({ ...preset.style })
}
</script>
