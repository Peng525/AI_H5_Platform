<template>
  <div>
    <p v-if="showLabel" class="text-xs font-semibold text-on-surface mb-1.5">页面背景</p>
    <div class="bg-swatch-board">
      <button
        v-for="item in bgSwatchItems"
        :key="item.key"
        type="button"
        class="bg-swatch"
        :class="[
          item.white ? 'bg-swatch--white' : '',
          isActiveBg(item.value) ? 'bg-swatch--active' : '',
        ]"
        :style="item.style"
        :title="item.label"
        :aria-label="item.label"
        @click="pickCanvasBg(item.value)"
      />
      <label
        class="bg-swatch bg-swatch--picker"
        title="自定义纯色"
        aria-label="自定义纯色"
      >
        <input
          :value="solidPickerValue"
          type="color"
          class="bg-swatch__color-input"
          @input="pickCanvasBg($event.target.value)"
        />
      </label>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getTheme, getThemeGradients } from '../constants/designThemes.js'
import { themePaletteColors } from '../constants/textFormats.js'
import { CANVAS_BACKGROUND_PRESETS, DEFAULT_CANVAS_BG } from '../constants/canvasBackgrounds.js'
import { normalizeSlideBackground, slideBackgroundCSSValue } from '../utils/slideBackground.js'

const props = defineProps({
  canvasBackground: { type: String, default: DEFAULT_CANVAS_BG },
  themeId: { type: String, default: 'zjy-minimal' },
  showLabel: { type: Boolean, default: true },
})

const emit = defineEmits(['canvas-bg-change'])

const themeGradients = computed(() => getThemeGradients(props.themeId))
const canvasBgPresets = CANVAS_BACKGROUND_PRESETS

const extraQuickColors = computed(() => {
  const theme = getTheme(props.themeId)
  return [
    '#FFFFFF',
    theme.colors.accent,
    ...themePaletteColors(props.themeId),
  ].filter((c, i, a) => a.indexOf(c) === i).slice(0, 4)
})

const bgSwatchItems = computed(() => {
  const items = [
    ...canvasBgPresets.map((p) => ({
      key: `bg-${p.value}`,
      label: p.label,
      style: { background: p.value },
      value: p.value,
      white: false,
    })),
    ...extraQuickColors.value.map((c) => ({
      key: `c-${c}`,
      label: quickColorLabel(c),
      style: { background: c },
      value: c,
      white: c === '#FFFFFF',
    })),
    ...themeGradients.value.map((g) => ({
      key: g.id,
      label: g.label,
      style: { background: g.value },
      value: { type: 'gradient', value: g.value },
      white: false,
    })),
  ]
  return items
})

const solidPickerValue = computed(() => {
  const n = normalizeSlideBackground(props.canvasBackground)
  if (n.type === 'solid' && n.value.startsWith('#')) return n.value
  return '#ffffff'
})

function isActiveBg(value) {
  const current = slideBackgroundCSSValue(props.canvasBackground)
  const next = typeof value === 'string' ? value : value?.value
  return current === next
}

function pickCanvasBg(color) {
  emit('canvas-bg-change', color)
}

function quickColorLabel(color) {
  if (color === '#FFFFFF') return '纯白'
  return color
}
</script>

<style scoped>
.bg-swatch-board {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

.bg-swatch {
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 0.25rem;
  border: 1px solid #c0c7d6;
  flex-shrink: 0;
  padding: 0;
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.bg-swatch:hover {
  border-color: #005daa;
}

.bg-swatch--active {
  box-shadow: 0 0 0 2px #fff, 0 0 0 3.5px #005daa;
}

.bg-swatch--white {
  background: #fff !important;
}

.bg-swatch--picker {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: conic-gradient(red, yellow, lime, aqua, blue, magenta, red);
  cursor: pointer;
  vertical-align: top;
}

.bg-swatch__color-input {
  width: 100%;
  height: 100%;
  border: 0;
  padding: 0;
  cursor: pointer;
  opacity: 0;
}
</style>
