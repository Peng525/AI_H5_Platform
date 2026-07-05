<template>
  <div class="relative w-full max-w-full min-w-0 overflow-visible" data-editor-chrome>
    <!-- 基础行：撤销 / 重做 / 添加（结果页可隐藏） -->
    <div
      v-if="!hideBaseBar"
      class="flex items-center gap-0.5 sm:gap-1 bg-white shadow-card rounded-lg px-1 sm:px-2 py-1 border border-outline-variant justify-center max-w-full mx-auto overflow-visible"
    >
      <button
        type="button"
        class="p-1.5 rounded hover:bg-surface-container text-on-surface-variant disabled:opacity-35"
        title="撤销 (Ctrl+Z)"
        :disabled="!canUndo"
        @click="$emit('undo')"
      >
        <span class="material-symbols-outlined text-[18px]">undo</span>
      </button>
      <button
        type="button"
        class="p-1.5 rounded hover:bg-surface-container text-on-surface-variant disabled:opacity-35"
        title="重做 (Ctrl+Y)"
        :disabled="!canRedo"
        @click="$emit('redo')"
      >
        <span class="material-symbols-outlined text-[18px]">redo</span>
      </button>
      <div class="w-px h-5 bg-outline-variant" />
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
        <div v-show="addMenuOpen" class="absolute left-0 top-full mt-1 w-44 z-[80]" @click.stop>
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
    </div>

    <!-- 上下文行：选中组件时显示；结果页无基础行时独立浮层 -->
    <div
      v-if="selected"
      class="left-0 right-0 z-[40] inline-flex flex-nowrap items-center gap-0.5 sm:gap-1 overflow-x-auto justify-start bg-white/98 backdrop-blur-sm shadow-lg rounded-lg px-1 sm:px-2 py-1.5 border border-outline-variant w-max max-w-full mx-auto pointer-events-auto"
      :class="hideBaseBar ? 'relative' : 'absolute top-full mt-1'"
    >
      <!-- 文本格式（Word 风格） -->
      <template v-if="isText">
        <TextFormatControls
          :selected="selected"
          :theme-id="themeId"
          :viewport-id="viewportId"
          :slide-id="slideId"
          @style-change="onStyle"
        />
      </template>

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
      <template v-else-if="selected.type === 'chartStack'">
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
        <button
          v-for="m in imageFitModes"
          :key="m.id"
          type="button"
          class="px-2 py-1 text-xs font-medium rounded border whitespace-nowrap antialiased"
          :class="activeImageFit === m.id
            ? 'bg-primary/10 border-primary text-primary'
            : 'border-outline-variant hover:bg-surface-container'"
          :title="m.label"
          @click="$emit('image-fit', m.id)"
        >
          {{ m.short }}
        </button>
        <button
          type="button"
          class="px-2 py-1 text-xs font-medium rounded border border-outline-variant hover:bg-surface-container whitespace-nowrap antialiased"
          title="裁切图片"
          @click="$emit('image-crop')"
        >
          裁切
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
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import WordColorPicker from './WordColorPicker.vue'
import TextFormatControls from './create/TextFormatControls.vue'

const props = defineProps({
  selected: { type: Object, default: null },
  themeId: { type: String, default: 'zjy-minimal' },
  viewportId: { type: String, default: 'mobile-375' },
  slideId: { type: String, default: '' },
  canUndo: { type: Boolean, default: false },
  canRedo: { type: Boolean, default: false },
  hideBaseBar: { type: Boolean, default: false },
})

const emit = defineEmits(['add-text', 'add-shape', 'add-image', 'style-change', 'duplicate', 'delete', 'bring-front', 'send-back', 'bring-forward', 'send-backward', 'center-element', 'image-fit', 'image-crop', 'undo', 'redo', 'edit-chart-stack'])

const imageFitModes = [
  { id: 'width', label: '适应宽度', short: '适应宽' },
  { id: 'fill', label: '填充页面', short: '填充' },
  { id: 'original', label: '原始尺寸', short: '原图' },
]

const activeImageFit = computed(() => {
  const el = props.selected
  if (!el || el.type !== 'image') return 'width'
  if (el.fitIntent) return el.fitIntent
  if ((el.zIndex ?? 10) === 0) return 'fill'
  return 'width'
})

const addMenuOpen = ref(false)
const addMenuRef = ref(null)

const isText = computed(() => props.selected?.type === 'text')
const isShape = computed(() => props.selected?.type === 'shape')

const colorPickerContextKey = computed(() => `${props.viewportId}:${props.slideId}:${props.selected?.id || ''}`)

function onStyle(patch) {
  emit('style-change', patch)
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
