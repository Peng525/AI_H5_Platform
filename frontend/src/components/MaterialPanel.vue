<template>
  <div class="material-panel p-3 flex flex-col gap-3 min-h-0">
    <div>
      <p class="text-xs font-semibold text-on-surface mb-1.5">页面背景</p>
      <div class="flex flex-wrap gap-1 mb-2">
        <button
          v-for="preset in canvasBgPresets"
          :key="'bg-' + preset.value"
          type="button"
          class="h-7 px-2 rounded border border-outline-variant shrink-0 hover:border-primary transition-colors text-[11px] font-medium text-on-surface"
          :class="isActiveBg(preset.value) ? 'ring-2 ring-primary ring-offset-1' : ''"
          :style="{ background: preset.value }"
          :title="preset.label"
          @click="pickCanvasBg(preset.value)"
        >
          {{ preset.label }}
        </button>
        <button
          v-for="c in extraQuickColors"
          :key="'c-' + c"
          type="button"
          class="w-7 h-7 rounded border border-outline-variant shrink-0 hover:border-primary transition-colors"
          :class="[c === '#FFFFFF' ? 'ring-1 ring-inset ring-gray-300' : '', isActiveBg(c) ? 'ring-2 ring-primary ring-offset-1' : '']"
          :style="{ background: c }"
          :title="c"
          @click="pickCanvasBg(c)"
        />
        <input
          :value="solidPickerValue"
          type="color"
          class="w-5 h-5 border-0 cursor-pointer p-0 shrink-0"
          title="自定义纯色"
          @input="pickCanvasBg($event.target.value)"
        />
      </div>
      <div v-if="themeGradients.length" class="flex flex-wrap gap-1">
        <button
          v-for="g in themeGradients"
          :key="g.id"
          type="button"
          class="h-7 px-2 rounded border text-[11px] font-medium shrink-0 hover:border-primary transition-colors"
          :class="isActiveBg(g.value) ? 'ring-2 ring-primary ring-offset-1 border-primary' : 'border-outline-variant'"
          :style="{ background: g.value }"
          :title="g.label"
          @click="pickCanvasBg({ type: 'gradient', value: g.value })"
        >
          {{ g.label }}
        </button>
      </div>
    </div>

    <div>
      <p class="text-xs font-semibold text-on-surface mb-1.5">商务版式</p>
      <div class="material-grid">
        <button
          v-for="item in businessBlocks"
          :key="item.id"
          type="button"
          class="material-card group"
          @click="emitLayout(item.id)"
        >
          <div class="material-preview">
            <span class="material-symbols-outlined text-xl text-primary">{{ item.icon }}</span>
          </div>
          <span class="material-label">{{ item.label }}</span>
        </button>
      </div>
    </div>

    <div>
      <p class="text-xs font-semibold text-on-surface mb-1.5">叙事版式</p>
      <div class="material-grid">
        <button
          v-for="item in storyBlocks"
          :key="item.id"
          type="button"
          class="material-card group"
          @click="emitLayout(item.id)"
        >
          <div class="material-preview">
            <span class="material-symbols-outlined text-xl text-secondary">{{ item.icon }}</span>
          </div>
          <span class="material-label">{{ item.label }}</span>
        </button>
      </div>
    </div>

    <div>
      <p class="text-xs font-semibold text-on-surface mb-1.5">互动组件</p>
      <div class="material-grid">
        <button
          v-for="item in interactiveTools"
          :key="item.id"
          type="button"
          class="material-card group"
          @click="$emit(item.event)"
        >
          <div class="material-preview">
            <span class="material-symbols-outlined text-2xl" :class="item.colorClass">{{ item.icon }}</span>
          </div>
          <span class="material-label">{{ item.label }}</span>
        </button>
      </div>
    </div>

    <p class="text-xs font-semibold text-on-surface">基础组件</p>

    <div class="material-grid">
      <button
        v-for="item in presets"
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
          <div
            v-else-if="item.kind === 'table'"
            class="w-10 h-8 grid grid-cols-3 grid-rows-2 gap-px bg-outline-variant p-px rounded-sm overflow-hidden"
          >
            <span v-for="n in 6" :key="n" class="bg-white" :class="n <= 3 ? 'bg-primary' : ''" />
          </div>
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
          <span
            v-else-if="item.kind === 'wordcloud'"
            class="material-symbols-outlined text-2xl text-secondary"
          >cloud</span>
        </div>
        <span class="material-label">{{ item.label }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getTheme, getThemeGradients } from '../constants/designThemes.js'
import { BUSINESS_LAYOUT_BLOCKS, STORY_LAYOUT_BLOCKS } from '../constants/layoutBlocks.js'
import { themePaletteColors } from '../constants/textFormats.js'
import { CANVAS_BACKGROUND_PRESETS, DEFAULT_CANVAS_BG } from '../constants/canvasBackgrounds.js'
import { normalizeSlideBackground, slideBackgroundCSSValue } from '../utils/slideBackground.js'

const props = defineProps({
  canvasBackground: { type: String, default: DEFAULT_CANVAS_BG },
  themeId: { type: String, default: 'zjy-minimal' },
})

const emit = defineEmits(['add', 'canvas-bg-change', 'apply-layout', 'open-dialogue-generator', 'open-wordcloud-editor'])

const themeGradients = computed(() => getThemeGradients(props.themeId))
const businessBlocks = BUSINESS_LAYOUT_BLOCKS
const storyBlocks = STORY_LAYOUT_BLOCKS

const canvasBgPresets = CANVAS_BACKGROUND_PRESETS

const extraQuickColors = computed(() => {
  const theme = getTheme(props.themeId)
  return [
    '#FFFFFF',
    theme.colors.accent,
    ...themePaletteColors(props.themeId),
  ].filter((c, i, a) => a.indexOf(c) === i).slice(0, 4)
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

function emitLayout(blockId) {
  emit('apply-layout', blockId)
}

const chartPreviewBars = [10, 18, 12, 22]

const interactiveTools = [
  { id: 'dialogue', label: '对话生成器', icon: 'forum', colorClass: 'text-primary', event: 'open-dialogue-generator' },
  { id: 'wordcloud', label: '文字云', icon: 'cloud', colorClass: 'text-secondary', event: 'open-wordcloud-editor' },
]

const presets = [
  { id: 'textbox', kind: 'text', label: '文本框', type: 'text' },
  { id: 'rect', kind: 'rect', label: '矩形', type: 'shape' },
  { id: 'table', kind: 'table', label: '表格', type: 'table' },
  { id: 'icon', kind: 'icon', label: '图标', type: 'icon', icon: 'emoji_objects' },
  { id: 'image', kind: 'image', label: '图片', type: 'image' },
  { id: 'chart', kind: 'chart', label: '图表', type: 'chart' },
  { id: 'wordcloud', kind: 'wordcloud', label: '文字云', type: 'wordcloud' },
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
</style>
