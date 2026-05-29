<template>
  <div class="material-panel p-3 flex flex-col gap-3 min-h-0">
    <div>
      <p class="text-xs font-semibold text-on-surface mb-1.5">页面背景</p>
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

    <div>
      <p class="text-xs font-semibold text-on-surface mb-1.5">版式</p>
      <div class="material-grid">
        <button
          v-for="item in primaryLayouts"
          :key="item.id"
          type="button"
          class="material-card group"
          @click="onPrimaryLayoutClick(item)"
        >
          <div class="material-preview">
            <div
              v-if="item.addType === 'table'"
              class="w-10 h-8 grid grid-cols-3 grid-rows-2 gap-px bg-outline-variant p-px rounded-sm overflow-hidden"
            >
              <span v-for="n in 6" :key="n" class="bg-white" :class="n <= 3 ? 'bg-primary' : ''" />
            </div>
            <span v-else class="material-symbols-outlined text-xl text-primary">{{ item.icon }}</span>
          </div>
          <span class="material-label">{{ item.label }}</span>
        </button>
        <button
          type="button"
          class="material-card group"
          @click="layoutMoreOpen = true"
        >
          <div class="material-preview">
            <span class="material-symbols-outlined text-xl text-on-surface-variant">more_horiz</span>
          </div>
          <span class="material-label">其他</span>
        </button>
      </div>
    </div>

    <div>
      <p class="text-xs font-semibold text-on-surface mb-1.5">特殊组件</p>
      <div class="material-grid">
        <button
          v-for="item in specialComponents"
          :key="item.id"
          type="button"
          class="material-card group"
          @click="onSpecialClick(item)"
        >
          <div class="material-preview">
            <span class="material-symbols-outlined text-2xl" :class="item.colorClass">{{ item.icon }}</span>
          </div>
          <span class="material-label">{{ item.label }}</span>
        </button>
      </div>
    </div>

    <div>
      <p class="text-xs font-semibold text-on-surface mb-1.5">基础组件</p>
      <div class="material-grid">
        <button
          v-for="item in basicComponents"
          :key="item.id"
          type="button"
          class="material-card group"
          @click="$emit('add', item)"
        >
          <div class="material-preview">
            <span
              v-if="item.kind === 'text'"
              class="text-[10px] text-on-surface-variant px-1 border border-dashed border-outline-variant rounded w-full text-center py-1 bg-white"
            >
              Aa
            </span>
            <span
              v-else-if="item.kind === 'rect'"
              class="w-9 h-7 rounded-sm border border-black/10 bg-primary"
            />
            <span
              v-else-if="item.kind === 'icon'"
              class="material-symbols-outlined text-2xl text-primary"
            >{{ item.icon }}</span>
            <span
              v-else-if="item.kind === 'image'"
              class="material-symbols-outlined text-2xl text-primary"
            >image</span>
            <div v-else-if="item.kind === 'chart'" class="flex items-end gap-0.5 h-8 px-1">
              <span
                v-for="(h, i) in chartPreviewBars"
                :key="i"
                class="w-1.5 rounded-t-sm bg-primary"
                :style="{ height: h + 'px' }"
              />
            </div>
          </div>
          <span class="material-label">{{ item.label }}</span>
        </button>
      </div>
    </div>

    <LayoutMoreModal
      :open="layoutMoreOpen"
      :blocks="moreLayoutsForModal"
      @close="layoutMoreOpen = false"
      @pick="emitLayout"
    />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import LayoutMoreModal from './LayoutMoreModal.vue'
import { getTheme, getThemeGradients } from '../constants/designThemes.js'
import { PRIMARY_LAYOUT_SHORTCUTS } from '../constants/layoutBlocks.js'
import { themePaletteColors } from '../constants/textFormats.js'
import { CANVAS_BACKGROUND_PRESETS, DEFAULT_CANVAS_BG } from '../constants/canvasBackgrounds.js'
import { normalizeSlideBackground, slideBackgroundCSSValue } from '../utils/slideBackground.js'

const props = defineProps({
  canvasBackground: { type: String, default: DEFAULT_CANVAS_BG },
  themeId: { type: String, default: 'zjy-minimal' },
  primaryLayouts: { type: Array, default: null },
  moreLayouts: { type: Array, default: null },
})

const emit = defineEmits(['add', 'canvas-bg-change', 'apply-layout', 'open-dialogue-generator', 'open-wordcloud-editor'])

const layoutMoreOpen = ref(false)
const primaryLayouts = computed(() => props.primaryLayouts || PRIMARY_LAYOUT_SHORTCUTS)
const moreLayoutsForModal = computed(() => props.moreLayouts)
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

function emitLayout(blockId) {
  emit('apply-layout', blockId)
}

function onPrimaryLayoutClick(item) {
  if (item.addType === 'table') {
    emit('add', { id: 'table', kind: 'table', label: '表格', type: 'table' })
    return
  }
  emitLayout(item.id)
}

function onSpecialClick(item) {
  if (item.action === 'dialogue') emit('open-dialogue-generator')
  else if (item.action === 'wordcloud') emit('open-wordcloud-editor')
}

const chartPreviewBars = [10, 18, 12, 22]

const specialComponents = [
  { id: 'dialogue', label: '对话生成器', icon: 'forum', colorClass: 'text-primary', action: 'dialogue' },
  { id: 'wordcloud', label: '文字云', icon: 'cloud', colorClass: 'text-secondary', action: 'wordcloud' },
]

const basicComponents = [
  { id: 'textbox', kind: 'text', label: '文本框', type: 'text' },
  { id: 'rect', kind: 'rect', label: '矩形', type: 'shape' },
  { id: 'icon', kind: 'icon', label: '图标', type: 'icon', icon: 'emoji_objects' },
  { id: 'image', kind: 'image', label: '图片', type: 'image' },
  { id: 'chart', kind: 'chart', label: '图表', type: 'chart' },
]
</script>

<style scoped>
.material-panel {
  -webkit-font-smoothing: auto;
  -moz-osx-font-smoothing: auto;
}

.material-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 6px;
}

@media (max-width: 220px) {
  .material-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.material-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 4px;
  border-radius: 6px;
  border: 1px solid #c0c7d6;
  background: white;
  transition: border-color 0.15s, background-color 0.15s;
}

.material-card:hover {
  border-color: #005daa;
  background: #f8fbff;
}

.material-preview {
  width: 100%;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f6f3f2;
  border-radius: 4px;
  border: 1px solid #e8e4e3;
}

.material-label {
  font-size: 11px;
  font-weight: 500;
  color: #1b1b1c;
  text-align: center;
  line-height: 1.25;
}

.group:hover .material-label {
  color: #005daa;
}

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
