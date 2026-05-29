<template>
  <div class="flex flex-col items-center gap-1 w-full max-w-full min-w-0" data-editor-chrome>
    <div class="flex items-center gap-0.5 sm:gap-1 bg-white shadow-card rounded-lg px-1 sm:px-2 py-1 border border-outline-variant flex-wrap justify-center max-w-full overflow-x-auto">
      <!-- 添加 -->
      <div ref="addMenuRef" class="relative">
        <button
          type="button"
          class="p-2 hover:bg-surface-container rounded flex items-center gap-1 text-primary font-medium text-xs"
          :class="addMenuOpen ? 'bg-surface-container' : ''"
          @click.stop="toggleAddMenu"
        >
          <span class="material-symbols-outlined text-[18px]">add_circle</span>
          添加
          <span class="material-symbols-outlined text-[14px] text-on-surface-variant">{{ addMenuOpen ? 'expand_less' : 'expand_more' }}</span>
        </button>
        <div v-show="addMenuOpen" class="absolute left-0 top-[calc(100%-2px)] pt-2 w-44 z-[60]" @click.stop>
          <div class="bg-white border border-outline-variant rounded-lg shadow-lg py-1">
            <button type="button" class="w-full text-left px-3 py-2 text-sm hover:bg-surface-container-low flex items-center gap-2" @click.stop="pickAdd('text')">
              <span class="material-symbols-outlined text-[16px] text-primary">text_fields</span>
              文本框
            </button>
            <button type="button" class="w-full text-left px-3 py-2 text-sm hover:bg-surface-container-low flex items-center gap-2" @click.stop="pickAdd('shape')">
              <span class="material-symbols-outlined text-[16px] text-secondary">category</span>
              形状
            </button>
            <button type="button" class="w-full text-left px-3 py-2 text-sm hover:bg-surface-container-low flex items-center gap-2" @click.stop="pickAdd('image')">
              <span class="material-symbols-outlined text-[16px] text-amber-600">image</span>
              图片占位
            </button>
          </div>
        </div>
      </div>

      <template v-if="selected">
        <div class="w-px h-5 bg-outline-variant" />

        <!-- 文本格式（Word 风格） -->
        <template v-if="isText">
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
            class="text-xs border border-outline-variant rounded px-1 py-1 max-w-[72px]"
            title="样式"
            @change="applyPreset($event.target.value)"
          >
            <option value="" disabled selected hidden>样式</option>
            <option v-for="(p, key) in TEXT_PRESETS" :key="key" :value="key">{{ p.label }}</option>
          </select>

          <select
            :value="selected.style?.lineHeight ?? 1.5"
            class="text-xs border border-outline-variant rounded px-1 py-1 max-w-[72px]"
            title="行距"
            @change="onStyle({ lineHeight: Number($event.target.value) })"
          >
            <option v-for="lh in LINE_HEIGHTS" :key="lh.value" :value="lh.value">行距 {{ lh.label }}</option>
          </select>

          <select
            :value="selected.style?.letterSpacing ?? 0"
            class="text-xs border border-outline-variant rounded px-1 py-1 max-w-[72px]"
            title="字间距"
            @change="onStyle({ letterSpacing: Number($event.target.value) })"
          >
            <option v-for="ls in LETTER_SPACINGS" :key="ls.value" :value="ls.value">间距 {{ ls.label }}</option>
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
        </template>

        <!-- 形状 / 表格 / 图表 / 图标 填充色 -->
        <template v-else-if="isShape">
          <WordColorPicker
            :model-value="selected.style?.background || '#005daa'"
            :context-key="colorPickerContextKey"
            label="填充颜色"
            icon="format_color_fill"
            @change="onStyle({ background: $event })"
          />
          <label class="text-[10px] text-on-surface-variant flex items-center gap-1">
            圆角
            <input
              type="range"
              min="0"
              max="48"
              :value="selected.style?.borderRadius ?? 8"
              class="w-16"
              @input="onStyle({ borderRadius: Number($event.target.value) })"
            />
          </label>
        </template>
        <!-- 表格：双击单元格编辑 -->
        <template v-else-if="selected.type === 'table'">
          <span class="text-xs text-on-surface-variant px-1">双击单元格编辑</span>
          <WordColorPicker
            :model-value="selected.style?.headerBackground || '#005daa'"
            :context-key="colorPickerContextKey"
            label="表头背景"
            icon="format_color_fill"
            @change="onStyle({ headerBackground: $event })"
          />
        </template>
        <template v-else-if="selected.type === 'chart'">
          <WordColorPicker
            :model-value="selected.style?.chartColor || '#005daa'"
            :context-key="colorPickerContextKey"
            label="图表颜色"
            icon="format_color_fill"
            @change="onStyle({ chartColor: $event })"
          />
        </template>
        <template v-else-if="selected.type === 'icon'">
          <WordColorPicker
            :model-value="selected.style?.color || '#005daa'"
            :context-key="colorPickerContextKey"
            label="图标颜色"
            icon="format_color_text"
            @change="onStyle({ color: $event })"
          />
          <WordColorPicker
            :model-value="selected.style?.background || '#e8f0fe'"
            :context-key="colorPickerContextKey"
            label="背景颜色"
            icon="format_color_fill"
            @change="onStyle({ background: $event })"
          />
        </template>
        <template v-else-if="selected.type === 'image'">
          <WordColorPicker
            :model-value="selected.style?.background || '#f0f0f0'"
            :context-key="colorPickerContextKey"
            label="背景颜色"
            icon="format_color_fill"
            @change="onStyle({ background: $event })"
          />
          <div class="w-px h-5 bg-outline-variant" />
          <button
            v-for="m in imageFitModes"
            :key="m.id"
            type="button"
            class="px-1.5 py-1 text-[10px] rounded border whitespace-nowrap"
            :class="m.id === 'width' ? 'border-outline-variant hover:bg-surface-container' : 'border-outline-variant hover:bg-surface-container'"
            :title="m.label"
            @click="$emit('image-fit', m.id)"
          >
            {{ m.short }}
          </button>
        </template>

        <div class="w-px h-5 bg-outline-variant" />

        <button type="button" class="p-1.5 hover:bg-surface-container rounded text-on-surface-variant" title="水平居中" @click="$emit('center-element', 'h')">
          <span class="material-symbols-outlined text-[18px]">align_horizontal_center</span>
        </button>
        <button type="button" class="p-1.5 hover:bg-surface-container rounded text-on-surface-variant" title="垂直居中" @click="$emit('center-element', 'v')">
          <span class="material-symbols-outlined text-[18px]">align_vertical_center</span>
        </button>
        <button type="button" class="p-1.5 hover:bg-surface-container rounded text-on-surface-variant" title="复制" @click="$emit('duplicate')">
          <span class="material-symbols-outlined text-[18px]">content_copy</span>
        </button>
        <button type="button" class="p-1.5 hover:bg-surface-container rounded text-on-surface-variant" title="置顶" @click="$emit('bring-front')">
          <span class="material-symbols-outlined text-[18px]">vertical_align_top</span>
        </button>
        <button type="button" class="p-1.5 hover:bg-surface-container rounded text-on-surface-variant" title="置底" @click="$emit('send-back')">
          <span class="material-symbols-outlined text-[18px]">vertical_align_bottom</span>
        </button>
        <button type="button" class="p-1.5 hover:bg-surface-container rounded text-on-surface-variant" title="上移一层" @click="$emit('bring-forward')">
          <span class="material-symbols-outlined text-[18px]">keyboard_arrow_up</span>
        </button>
        <button type="button" class="p-1.5 hover:bg-surface-container rounded text-on-surface-variant" title="下移一层" @click="$emit('send-backward')">
          <span class="material-symbols-outlined text-[18px]">keyboard_arrow_down</span>
        </button>
        <button type="button" class="p-1.5 hover:bg-red-50 rounded text-red-600" title="删除" @click="$emit('delete')">
          <span class="material-symbols-outlined text-[18px]">delete</span>
        </button>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import {
  FONT_FAMILIES,
  FONT_SIZES,
  LETTER_SPACINGS,
  LINE_HEIGHTS,
  TEXT_PRESETS,
  getThemeTextPresets,
} from '../constants/textFormats'
import WordColorPicker from './WordColorPicker.vue'

const props = defineProps({
  selected: { type: Object, default: null },
  themeId: { type: String, default: 'zjy-minimal' },
  viewportId: { type: String, default: 'mobile-375' },
  slideId: { type: String, default: '' },
})

const emit = defineEmits(['add-text', 'add-shape', 'add-image', 'style-change', 'duplicate', 'delete', 'bring-front', 'send-back', 'bring-forward', 'send-backward', 'center-element', 'image-fit'])

const imageFitModes = [
  { id: 'width', label: '适应宽度', short: '适应宽' },
  { id: 'fill', label: '填充页面', short: '填充' },
  { id: 'original', label: '原始尺寸', short: '原图' },
]

const addMenuOpen = ref(false)
const addMenuRef = ref(null)

const isText = computed(() => props.selected?.type === 'text')
const isShape = computed(() => props.selected?.type === 'shape')
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

function applyPreset(key) {
  const preset = TEXT_PRESETS[key]
  if (preset) onStyle({ ...preset.style })
}

function applyThemePreset(key) {
  const preset = themePresets.value[key]
  if (preset) onStyle({ ...preset.style })
}

function toggleAddMenu() {
  addMenuOpen.value = !addMenuOpen.value
}

function pickAdd(type) {
  addMenuOpen.value = false
  if (type === 'text') emit('add-text')
  else if (type === 'shape') emit('add-shape')
  else emit('add-image')
}

function onDocPointerDown(e) {
  if (!addMenuOpen.value) return
  if (addMenuRef.value?.contains(e.target)) return
  addMenuOpen.value = false
}

function onEsc(e) {
  if (e.key === 'Escape') addMenuOpen.value = false
}

onMounted(() => {
  document.addEventListener('mousedown', onDocPointerDown)
  document.addEventListener('keydown', onEsc)
})
onUnmounted(() => {
  document.removeEventListener('mousedown', onDocPointerDown)
  document.removeEventListener('keydown', onEsc)
})
</script>
