<template>
  <section
    class="flex-1 bg-surface-container-low flex items-center justify-center overflow-hidden relative"
    @wheel.prevent="onWheelZoom"
  >
    <EditorCanvasToolbar
      :selected="selectedElement"
      @add-text="$emit('add-text')"
      @add-shape="$emit('add-shape')"
      @add-image="$emit('add-image')"
      @style-change="$emit('style-change', $event)"
      @duplicate="$emit('duplicate')"
      @delete="$emit('delete-selected')"
      @bring-front="$emit('bring-front')"
    />

    <!-- 分辨率选择 -->
    <div class="absolute top-4 right-4 z-20">
      <select
        :value="viewportId"
        class="text-xs border border-outline-variant rounded-lg px-2 py-1.5 bg-white shadow-card max-w-[160px]"
        @change="$emit('viewport-change', $event.target.value)"
      >
        <optgroup label="手机">
          <option v-for="v in mobileViewports" :key="v.id" :value="v.id">{{ v.label }}</option>
        </optgroup>
        <optgroup label="网页">
          <option v-for="v in webViewports" :key="v.id" :value="v.id">{{ v.label }}</option>
        </optgroup>
      </select>
    </div>

    <div class="absolute bottom-6 flex items-center gap-2 bg-white shadow-card rounded-full px-2 py-1 border border-outline-variant z-20">
      <button type="button" class="p-1.5 hover:bg-surface-container rounded-full" title="缩小" @click="zoomOut">
        <span class="material-symbols-outlined text-[18px]">remove</span>
      </button>
      <div class="w-12 text-center">
        <input
          v-if="zoomEditing"
          ref="zoomInputRef"
          v-model="zoomInput"
          type="number"
          min="25"
          max="200"
          class="w-full text-xs text-center border border-primary rounded px-0.5 py-0.5 outline-none"
          @blur="commitZoomInput"
          @keydown.enter="commitZoomInput"
          @keydown.esc="cancelZoomInput"
        />
        <button
          v-else
          type="button"
          class="text-xs w-full hover:text-primary hover:bg-surface-container-low rounded py-0.5"
          title="点击输入缩放比例"
          @click="startZoomEdit"
        >
          {{ zoomPercent }}%
        </button>
      </div>
      <button type="button" class="p-1.5 hover:bg-surface-container rounded-full" title="放大" @click="zoomIn">
        <span class="material-symbols-outlined text-[18px]">add</span>
      </button>
      <span class="text-[10px] text-on-surface-variant pl-1 border-l border-outline-variant whitespace-nowrap">
        {{ safeViewport.width }}×{{ safeViewport.height }}
      </span>
    </div>

    <div
      class="relative transition-transform origin-center"
      :style="{ transform: `scale(${displayScale})` }"
      @mousedown.self="$emit('deselect')"
    >
      <div
        class="bg-white shadow-2xl overflow-hidden flex flex-col transition-all duration-300"
        :class="frameClass"
        :style="{ width: safeViewport.width + 'px', height: safeViewport.height + 'px' }"
      >
        <div v-if="safeViewport.device === 'mobile'" class="h-7 w-full flex justify-between items-center px-4 pt-1 shrink-0 bg-white">
          <span class="text-[12px] font-medium">9:41</span>
          <div class="flex gap-1 items-center opacity-80">
            <span class="material-symbols-outlined text-[14px]">signal_cellular_alt</span>
            <span class="material-symbols-outlined text-[14px]">wifi</span>
            <span class="material-symbols-outlined text-[14px]">battery_full</span>
          </div>
        </div>
        <div v-else class="h-8 shrink-0 bg-gray-100 border-b border-gray-200 flex items-center px-3 gap-1.5">
          <span class="w-2.5 h-2.5 rounded-full bg-red-400" />
          <span class="w-2.5 h-2.5 rounded-full bg-amber-400" />
          <span class="w-2.5 h-2.5 rounded-full bg-green-400" />
          <span class="ml-2 text-[10px] text-gray-500 truncate flex-1">{{ safeViewport.label }}</span>
        </div>

        <div
          ref="canvasRef"
          class="flex-1 relative overflow-hidden"
          :style="{ background: canvasBackground }"
          @mousedown.self="$emit('deselect')"
        >
          <div
            :key="transitionKey"
            class="absolute inset-0"
            :class="previewAnimClass"
          >
            <CanvasElement
              v-for="el in elements"
              :key="el.id"
              :element="el"
              :selected="el.id === selectedId"
              :scale="1"
              @select="$emit('select', $event)"
              @update="(id, patch) => $emit('update-element', id, patch)"
            />

            <div
              v-if="!elements.length && slide"
              class="absolute inset-0 p-6 text-white pointer-events-none"
            >
              <span class="text-xs opacity-80">第 {{ slideIndex + 1 }} 页</span>
              <h2 class="text-xl font-bold mt-2">{{ slide.title }}</h2>
              <p v-if="slide.subtitle" class="text-sm mt-2 opacity-90">{{ slide.subtitle }}</p>
              <ul v-if="slide.bullets?.length" class="mt-4 space-y-2 text-sm">
                <li v-for="(b, j) in slide.bullets" :key="j">• {{ b }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { VIEWPORT_PRESETS, getViewportPreset } from '../constants/editorPresets'
import { animationEnterClass } from '../utils/slideAnimation'
import CanvasElement from './CanvasElement.vue'
import EditorCanvasToolbar from './EditorCanvasToolbar.vue'

const props = defineProps({
  elements: { type: Array, default: () => [] },
  selectedId: { type: String, default: null },
  slide: { type: Object, default: null },
  slideIndex: { type: Number, default: 0 },
  viewport: { type: Object, default: null },
  viewportId: { type: String, default: 'mobile-375' },
  previewAnimation: { type: String, default: '' },
  canvasBackground: { type: String, default: '#005daa' },
})

defineEmits([
  'select',
  'deselect',
  'update-element',
  'add-text',
  'add-shape',
  'add-image',
  'style-change',
  'duplicate',
  'delete-selected',
  'bring-front',
  'viewport-change',
])

const DEFAULT_ZOOM = 90
const MIN_ZOOM = 25
const MAX_ZOOM = 200
const ZOOM_STEP = 10

const zoomPercent = ref(DEFAULT_ZOOM)
const zoomEditing = ref(false)
const zoomInput = ref(String(DEFAULT_ZOOM))
const zoomInputRef = ref(null)
const transitionKey = ref(0)
const canvasRef = ref(null)

const mobileViewports = VIEWPORT_PRESETS.filter((v) => v.device === 'mobile')
const webViewports = VIEWPORT_PRESETS.filter((v) => v.device === 'web')

const selectedElement = computed(() => props.elements.find((el) => el.id === props.selectedId) || null)

/** 防御：viewport 未正确传入时使用默认预设 */
const safeViewport = computed(() => {
  const v = props.viewport
  if (v && typeof v.width === 'number' && typeof v.height === 'number') return v
  return getViewportPreset(props.viewportId || 'mobile-375')
})

const frameClass = computed(() =>
  safeViewport.value.device === 'mobile'
    ? 'rounded-[2rem] border-[8px] border-gray-900'
    : 'rounded-lg border border-gray-300'
)

/** 大分辨率自动缩小以适应编辑区 */
const autoScale = computed(() => {
  const maxW = 520
  const maxH = 680
  const w = safeViewport.value.width
  const h = safeViewport.value.height
  if (!w || !h) return 1
  return Math.min(1, maxW / w, maxH / h)
})

const displayScale = computed(() => {
  const s = autoScale.value * (zoomPercent.value / 100)
  return Number.isFinite(s) && s > 0 ? s : autoScale.value
})

function clampZoom(v) {
  return Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, Math.round(v)))
}

function resetZoom() {
  zoomPercent.value = DEFAULT_ZOOM
  zoomInput.value = String(DEFAULT_ZOOM)
}

const previewAnimClass = computed(() => {
  if (props.previewAnimation) return animationEnterClass(props.previewAnimation)
  return ''
})

watch(
  () => props.previewAnimation,
  (anim) => {
    if (!anim) return
    transitionKey.value += 1
  }
)

watch(
  () => props.slide?.id,
  () => resetZoom()
)

watch(
  () => props.viewportId,
  () => resetZoom()
)

async function startZoomEdit() {
  zoomInput.value = String(zoomPercent.value)
  zoomEditing.value = true
  await nextTick()
  zoomInputRef.value?.focus()
  zoomInputRef.value?.select()
}

function commitZoomInput() {
  const n = Number(zoomInput.value)
  if (Number.isFinite(n)) zoomPercent.value = clampZoom(n)
  zoomEditing.value = false
}

function cancelZoomInput() {
  zoomEditing.value = false
  zoomInput.value = String(zoomPercent.value)
}

function zoomIn() {
  zoomPercent.value = clampZoom(zoomPercent.value + ZOOM_STEP)
}

function zoomOut() {
  zoomPercent.value = clampZoom(zoomPercent.value - ZOOM_STEP)
}

function onWheelZoom(e) {
  const step = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP
  zoomPercent.value = clampZoom(zoomPercent.value + step)
}
</script>
