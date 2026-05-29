<template>
  <section
    class="flex-1 bg-surface-container-low overflow-hidden relative select-none"
    @wheel.prevent="onWheelZoom"
  >
    <EditorCanvasToolbar
      :selected="selectedElement"
      :theme-id="themeId"
      :viewport-id="viewportId"
      :slide-id="slide?.id || ''"
      @add-text="$emit('add-text')"
      @add-shape="$emit('add-shape')"
      @add-image="$emit('add-image')"
      @style-change="$emit('style-change', $event)"
      @duplicate="$emit('duplicate')"
      @delete="$emit('delete-selected')"
      @bring-front="$emit('bring-front')"
      @center-element="$emit('center-element', $event)"
    />

    <!-- 分辨率选择 -->
    <div class="absolute top-2 right-2 sm:top-4 sm:right-4 z-20 flex items-center gap-1.5 sm:gap-2 max-w-[calc(100%-1rem)]" data-editor-chrome>
      <button
        v-if="slide?.chat_script?.enabled"
        type="button"
        class="text-[10px] sm:text-xs border border-outline-variant rounded-lg px-1.5 sm:px-2 py-1 sm:py-1.5 bg-white shadow-card whitespace-nowrap"
        :class="dialoguePreviewOn ? 'text-primary border-primary' : ''"
        @click="toggleDialoguePreview"
      >
        {{ dialoguePreviewOn ? '隐藏对话' : '预览对话' }}
      </button>
      <select
        :value="viewportId"
        class="text-[10px] sm:text-xs border border-outline-variant rounded-lg px-1.5 sm:px-2 py-1 sm:py-1.5 bg-white shadow-card max-w-[7.5rem] sm:max-w-[10rem] min-w-0"
        @change="onViewportChange($event.target.value)"
      >
        <optgroup label="手机">
          <option v-for="v in mobileViewports" :key="v.id" :value="v.id">{{ v.label }}</option>
        </optgroup>
        <optgroup label="网页">
          <option v-for="v in webViewports" :key="v.id" :value="v.id">{{ v.label }}</option>
        </optgroup>
      </select>
    </div>

    <div class="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-1 sm:gap-2 bg-white shadow-card rounded-full px-1.5 sm:px-2 py-1 border border-outline-variant z-20 max-w-[calc(100%-1rem)]" data-editor-chrome>
      <button
        type="button"
        class="p-1.5 rounded-full transition-colors"
        :class="panMode ? 'bg-primary text-on-primary' : 'hover:bg-surface-container text-on-surface-variant'"
        title="手型工具 · 拖动画布 (H)"
        @click="togglePanMode"
      >
        <span class="material-symbols-outlined text-[18px]">pan_tool</span>
      </button>
      <span class="w-px h-4 bg-outline-variant" />
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
          title="点击输入缩放；双击重置视图"
          @click="startZoomEdit"
          @dblclick.stop="resetView"
        >
          {{ zoomPercent }}%
        </button>
      </div>
      <button type="button" class="p-1.5 hover:bg-surface-container rounded-full" title="放大" @click="zoomIn">
        <span class="material-symbols-outlined text-[18px]">add</span>
      </button>
      <span class="hidden sm:inline text-[10px] text-on-surface-variant pl-1 border-l border-outline-variant whitespace-nowrap">
        {{ safeViewport.width }}×{{ safeViewport.height }}
      </span>
    </div>

    <div
      v-show="panActive"
      class="absolute inset-0 z-[15]"
      :class="isPanning ? 'cursor-grabbing' : 'cursor-grab'"
      @mousedown="startPanDrag"
    />

    <div
      class="absolute left-1/2 top-1/2 will-change-transform"
      :style="canvasTransformStyle"
    >
      <div
        class="bg-white shadow-2xl overflow-hidden flex flex-col"
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
        >
          <div
            :key="transitionKey"
            class="absolute inset-0"
            :class="previewAnimClass"
          >
            <div
              class="absolute inset-0 z-[1] cursor-crosshair"
              aria-hidden="true"
              @mousedown="onCanvasPointerDown"
            />

            <div
              v-if="marqueeRect"
              class="absolute z-[45] border-2 border-[#4a4a4a] bg-[#4a4a4a]/12 pointer-events-none rounded-sm"
              :style="marqueeStyle"
            />

            <CanvasElement
              v-for="el in elements"
              :key="el.id"
              :element="el"
              :selected="selectedIds.includes(el.id)"
              :scale="1"
              :theme-id="themeId"
              @select="$emit('select', $event)"
              @update="(id, patch) => $emit('update-element', id, patch)"
              @batch-start="(id) => $emit('batch-start', id)"
              @batch-end="$emit('batch-end')"
              @move-delta="$emit('move-delta', $event)"
              @edit-wordcloud="$emit('edit-wordcloud', $event)"
            />

            <div
              v-if="!elements.length && slide && !slide?.chat_script?.enabled"
              class="absolute inset-0 p-6 text-white pointer-events-none"
            >
              <span class="text-xs opacity-80">第 {{ slideIndex + 1 }} 页</span>
              <h2 class="text-xl font-bold mt-2">{{ slide.title }}</h2>
              <p v-if="slide.subtitle" class="text-sm mt-2 opacity-90">{{ slide.subtitle }}</p>
              <ul v-if="slide.bullets?.length" class="mt-4 space-y-2 text-sm">
                <li v-for="(b, j) in slide.bullets" :key="j">• {{ b }}</li>
              </ul>
            </div>

            <div
              v-if="dialoguePreviewOn && chatScriptForPreview"
              class="absolute inset-0 z-20 pointer-events-none"
            >
              <DialoguePreviewCanvas :model-value="chatScriptForPreview" :editable="false" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { closeActiveColorPicker } from '../composables/useColorPickerSession'
import { VIEWPORT_PRESETS, getViewportPreset } from '../constants/editorPresets'
import { DEFAULT_CANVAS_BG } from '../constants/canvasBackgrounds.js'
import { animationEnterClass } from '../utils/slideAnimation'
import CanvasElement from './CanvasElement.vue'
import EditorCanvasToolbar from './EditorCanvasToolbar.vue'
import DialoguePreviewCanvas from './dialogue/DialoguePreviewCanvas.vue'
import { normalizeChatScript } from '../utils/chatScript.js'

const props = defineProps({
  elements: { type: Array, default: () => [] },
  selectedIds: { type: Array, default: () => [] },
  slide: { type: Object, default: null },
  slideIndex: { type: Number, default: 0 },
  viewport: { type: Object, default: null },
  viewportId: { type: String, default: 'mobile-375' },
  previewAnimation: { type: String, default: '' },
  previewAnimationTick: { type: Number, default: 0 },
  canvasBackground: { type: String, default: DEFAULT_CANVAS_BG },
  themeId: { type: String, default: 'zjy-minimal' },
  showDialoguePreview: { type: Boolean, default: false },
})

const emit = defineEmits([
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
  'center-element',
  'viewport-change',
  'batch-start',
  'batch-end',
  'move-delta',
  'edit-wordcloud',
  'marquee-select',
  'update:show-dialogue-preview',
])

const DEFAULT_ZOOM = 90
const MIN_ZOOM = 25
const MAX_ZOOM = 200
const ZOOM_STEP = 10

const zoomPercent = ref(DEFAULT_ZOOM)
const zoomEditing = ref(false)

const dialoguePreviewOn = computed({
  get: () => props.showDialoguePreview,
  set: (v) => emit('update:show-dialogue-preview', v),
})

function toggleDialoguePreview() {
  dialoguePreviewOn.value = !dialoguePreviewOn.value
}

const chatScriptForPreview = computed(() => {
  if (!props.slide?.chat_script?.enabled) return null
  return normalizeChatScript(props.slide.chat_script)
})

watch(
  () => props.slide?.id,
  () => {
    if (props.slide?.chat_script?.enabled) {
      emit('update:show-dialogue-preview', true)
    }
  }
)
const zoomInput = ref(String(DEFAULT_ZOOM))
const zoomInputRef = ref(null)
const transitionKey = ref(0)
const canvasRef = ref(null)
const marqueeRect = ref(null)
const panMode = ref(false)
const spaceHeld = ref(false)
const isPanning = ref(false)
const panX = ref(0)
const panY = ref(0)

const panActive = computed(() => panMode.value || spaceHeld.value)

const mobileViewports = VIEWPORT_PRESETS.filter((v) => v.device === 'mobile')
const webViewports = VIEWPORT_PRESETS.filter((v) => v.device === 'web')

const selectedElement = computed(() => {
  const primaryId = props.selectedIds[props.selectedIds.length - 1]
  return props.elements.find((el) => el.id === primaryId) || null
})

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

const canvasTransformStyle = computed(() => ({
  transform: `translate3d(calc(-50% + ${panX.value}px), calc(-50% + ${panY.value}px), 0) scale(${displayScale.value})`,
  transformOrigin: 'center center',
}))

const marqueeStyle = computed(() => {
  const r = marqueeRect.value
  if (!r) return {}
  return {
    left: `${r.x}px`,
    top: `${r.y}px`,
    width: `${r.w}px`,
    height: `${r.h}px`,
  }
})

function clientToCanvasLocal(clientX, clientY) {
  const el = canvasRef.value
  if (!el) return { x: 0, y: 0 }
  const rect = el.getBoundingClientRect()
  const lw = el.clientWidth || el.offsetWidth || 1
  const lh = el.clientHeight || el.offsetHeight || 1
  return {
    x: ((clientX - rect.left) / rect.width) * lw,
    y: ((clientY - rect.top) / rect.height) * lh,
  }
}

function elementIntersectsRect(el, rect) {
  const ex = el.x ?? 0
  const ey = el.y ?? 0
  const ew = el.width ?? 0
  const eh = el.height ?? 0
  return !(ex + ew < rect.x || rect.x + rect.w < ex || ey + eh < rect.y || rect.y + rect.h < ey)
}

function onCanvasPointerDown(e) {
  if (panActive.value || e.button !== 0) return
  e.preventDefault()
  e.stopPropagation()

  const startClient = { x: e.clientX, y: e.clientY }
  const startLocal = clientToCanvasLocal(startClient.x, startClient.y)
  let dragging = false
  const DRAG_THRESHOLD = 4

  marqueeRect.value = { x: startLocal.x, y: startLocal.y, w: 0, h: 0 }

  function onMove(ev) {
    const dx = ev.clientX - startClient.x
    const dy = ev.clientY - startClient.y
    if (!dragging && Math.hypot(dx, dy) < DRAG_THRESHOLD) return
    dragging = true
    const cur = clientToCanvasLocal(ev.clientX, ev.clientY)
    const x = Math.min(startLocal.x, cur.x)
    const y = Math.min(startLocal.y, cur.y)
    marqueeRect.value = {
      x,
      y,
      w: Math.abs(cur.x - startLocal.x),
      h: Math.abs(cur.y - startLocal.y),
    }
  }

  function onUp(ev) {
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
    const rect = marqueeRect.value
    marqueeRect.value = null

    if (!dragging) {
      emit('deselect')
      return
    }

    if (!rect || rect.w < 2 || rect.h < 2) {
      emit('deselect')
      return
    }

    const ids = props.elements.filter((el) => elementIntersectsRect(el, rect)).map((el) => el.id)
    emit('marquee-select', {
      ids,
      additive: ev.ctrlKey || ev.metaKey || ev.shiftKey,
    })
  }

  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

function togglePanMode() {
  panMode.value = !panMode.value
}

function resetView() {
  resetZoom()
  panX.value = 0
  panY.value = 0
}

function startPanDrag(e) {
  if (e.button !== 0) return
  e.preventDefault()
  e.stopPropagation()
  isPanning.value = true
  const startX = e.clientX
  const startY = e.clientY
  const origX = panX.value
  const origY = panY.value

  function onMove(ev) {
    ev.preventDefault()
    panX.value = origX + (ev.clientX - startX)
    panY.value = origY + (ev.clientY - startY)
  }
  function onUp() {
    isPanning.value = false
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
  }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

function onPanKeyDown(e) {
  const editing = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName)
  if (editing) return
  if (e.code === 'Space' && !e.repeat) {
    e.preventDefault()
    spaceHeld.value = true
  }
  if (e.key.toLowerCase() === 'h' && !e.repeat && !e.ctrlKey && !e.metaKey && !e.altKey) {
    e.preventDefault()
    togglePanMode()
  }
}

function onPanKeyUp(e) {
  if (e.code === 'Space') {
    spaceHeld.value = false
    isPanning.value = false
  }
}

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
  () => props.previewAnimationTick,
  () => {
    if (props.previewAnimation) transitionKey.value += 1
  }
)

watch(
  () => props.slide?.id,
  () => {
    closeActiveColorPicker()
    resetView()
  }
)

watch(
  () => props.viewportId,
  () => {
    closeActiveColorPicker()
    resetView()
  }
)

function onViewportChange(id) {
  closeActiveColorPicker()
  emit('viewport-change', id)
}

onMounted(() => {
  window.addEventListener('keydown', onPanKeyDown)
  window.addEventListener('keyup', onPanKeyUp)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onPanKeyDown)
  window.removeEventListener('keyup', onPanKeyUp)
})

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
