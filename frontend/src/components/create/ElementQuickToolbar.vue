<template>
  <div
    v-if="selected && anchorRect"
    data-editor-chrome
    class="inline-flex flex-nowrap items-center gap-1 overflow-x-auto bg-white shadow-lg rounded-xl px-2 py-1.5 border border-outline-variant pointer-events-auto w-max max-w-[calc(100vw-16px)]"
    :style="barStyle"
    @mousedown.stop
  >
    <template v-if="isText">
      <TextFormatControls
        :selected="selected"
        :theme-id="themeId"
        :viewport-id="viewportId"
        :slide-id="slideId"
        @style-change="$emit('style-change', $event)"
      />
      <div class="w-px h-5 bg-outline-variant shrink-0 mx-0.5" />
    </template>

    <template v-if="isImage">
      <button
        v-for="m in imageFitModes"
        :key="m.id"
        type="button"
        class="p-1.5 rounded hover:bg-surface-container text-on-surface-variant"
        :class="activeImageFit === m.id ? 'bg-primary/10 text-primary' : ''"
        :title="m.label"
        @click="$emit('image-fit', m.id)"
      >
        <span class="material-symbols-outlined text-[18px]">{{ m.icon }}</span>
      </button>
      <button
        type="button"
        class="p-1.5 rounded hover:bg-surface-container text-on-surface-variant"
        title="裁切"
        @click="$emit('image-crop')"
      >
        <span class="material-symbols-outlined text-[18px]">crop</span>
      </button>
      <div ref="layoutMenuRef" class="relative">
        <button
          type="button"
          class="px-2 py-1 text-xs font-medium rounded border border-outline-variant hover:bg-surface-container inline-flex items-center gap-0.5"
          @click.stop="layoutMenuOpen = !layoutMenuOpen"
        >
          布局
          <span class="material-symbols-outlined text-[14px]">{{ layoutMenuOpen ? 'expand_less' : 'expand_more' }}</span>
        </button>
        <div
          v-show="layoutMenuOpen"
          class="absolute bottom-full left-0 mb-1 w-36 bg-white border border-outline-variant rounded-lg shadow-lg py-1 z-[80]"
          @click.stop
        >
          <button type="button" class="w-full text-left px-3 py-2 text-xs hover:bg-surface-container-low" @click="pickLayout('top')">顶部布局</button>
          <button type="button" class="w-full text-left px-3 py-2 text-xs hover:bg-surface-container-low" @click="pickLayout('left')">左侧布局</button>
          <button type="button" class="w-full text-left px-3 py-2 text-xs hover:bg-surface-container-low" @click="pickLayout('right')">右侧布局</button>
        </div>
      </div>
      <div class="w-px h-5 bg-outline-variant shrink-0" />
    </template>

    <button type="button" class="p-1.5 rounded hover:bg-surface-container text-on-surface-variant shrink-0" title="复制" @click="$emit('duplicate')">
      <span class="material-symbols-outlined text-[18px]">content_copy</span>
    </button>
    <button type="button" class="p-1.5 rounded hover:bg-surface-container text-on-surface-variant shrink-0" title="置顶" @click="$emit('bring-front')">
      <span class="material-symbols-outlined text-[18px]">vertical_align_top</span>
    </button>
    <button type="button" class="p-1.5 rounded hover:bg-surface-container text-on-surface-variant shrink-0" title="置底" @click="$emit('send-back')">
      <span class="material-symbols-outlined text-[18px]">vertical_align_bottom</span>
    </button>
    <button type="button" class="p-1.5 rounded hover:bg-red-50 text-red-600 shrink-0" title="删除" @click="$emit('delete-selected')">
      <span class="material-symbols-outlined text-[18px]">delete</span>
    </button>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { floatingBarStyle } from '../../composables/useElementAnchor.js'
import TextFormatControls from './TextFormatControls.vue'

const props = defineProps({
  selected: { type: Object, default: null },
  anchorRect: { type: Object, default: null },
  themeId: { type: String, default: 'zjy-minimal' },
  viewportId: { type: String, default: 'mobile-375' },
  slideId: { type: [String, Number], default: '' },
  viewport: { type: Object, default: () => ({ width: 375, height: 667 }) },
})

const emit = defineEmits([
  'style-change',
  'image-fit',
  'image-crop',
  'image-layout',
  'duplicate',
  'bring-front',
  'send-back',
  'delete-selected',
  'edit-chart-stack',
])

const layoutMenuOpen = ref(false)
const layoutMenuRef = ref(null)

const isText = computed(() => props.selected?.type === 'text')
const isImage = computed(() => props.selected?.type === 'image')

const barStyle = computed(() =>
  floatingBarStyle(props.anchorRect, 'above', 6, {
    compact: true,
    barHeight: 40,
  }),
)

const imageFitModes = [
  { id: 'width', label: '适应宽度', icon: 'fit_width' },
  { id: 'fill', label: '填充', icon: 'crop_free' },
  { id: 'original', label: '原图', icon: 'photo_size_select_large' },
]

const activeImageFit = computed(() => {
  const el = props.selected
  if (!el || el.type !== 'image') return 'width'
  if (el.fitIntent) return el.fitIntent
  if ((el.zIndex ?? 10) === 0) return 'fill'
  return 'width'
})

function pickLayout(mode) {
  layoutMenuOpen.value = false
  emit('image-layout', mode)
}

function onDocPointerDown(e) {
  if (!layoutMenuOpen.value) return
  if (layoutMenuRef.value?.contains(e.target)) return
  layoutMenuOpen.value = false
}

onMounted(() => document.addEventListener('mousedown', onDocPointerDown))
onUnmounted(() => document.removeEventListener('mousedown', onDocPointerDown))
</script>
