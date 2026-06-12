<template>
  <div
    class="absolute select-none"
    :data-element-id="element.id"
    :class="[
      readonly && element.type !== 'chartStack' ? 'pointer-events-none' : readonly ? '' : 'touch-none',
      selectionRingClass,
      staggerClass,
    ]"
    :style="{
      left: element.x + 'px',
      top: element.y + 'px',
      width: element.width + 'px',
      height: element.height + 'px',
      zIndex: element.zIndex ?? CANVAS_Z.CONTENT_BASE,
      animationDelay: staggerDelay,
      ...selectionStyle,
    }"
    @mousedown.stop="onRootMouseDown"
  >
    <div
      v-if="element.type === 'text'"
      class="w-full h-full overflow-hidden px-1"
      :class="readonly ? '' : 'cursor-move'"
      :style="textStyle"
      @dblclick.stop="startEdit"
    >
      <textarea
        v-if="editing"
        ref="inputRef"
        v-model="editText"
        class="w-full h-full bg-white/90 border border-primary outline-none text-inherit px-1 resize-none"
        :style="{
          fontSize: (element.style?.fontSize || 16) + 'px',
          color: element.style?.color || '#1b1b1c',
          fontWeight: element.style?.fontWeight || 'normal',
          fontFamily: element.style?.fontFamily || 'inherit',
          lineHeight: element.style?.lineHeight ?? 1.5,
          letterSpacing: (element.style?.letterSpacing ?? 0) + 'px',
          textAlign: element.style?.textAlign || 'left',
        }"
        @blur="commitEdit"
        @mousedown.stop
      />
      <span v-else class="block w-full h-full whitespace-pre-wrap break-words">{{ element.content }}</span>
    </div>

    <div
      v-else-if="element.type === 'shape'"
      class="w-full h-full cursor-move"
      :style="shapeStyle"
    />

    <div
      v-else-if="element.type === 'chartPlaceholder'"
      class="w-full h-full pointer-events-none flex flex-col items-center justify-center gap-2 box-border"
      :style="chartPlaceholderStyle"
      aria-hidden="true"
    >
      <span class="material-symbols-outlined text-[40px] text-on-surface-variant/50 pointer-events-none">analytics</span>
      <span class="text-xs text-on-surface-variant pointer-events-none">图表占位</span>
    </div>

    <div
      v-else-if="element.type === 'icon'"
      class="w-full h-full cursor-move flex items-center justify-center"
      :style="iconStyle"
    >
      <span class="material-symbols-outlined select-none pointer-events-none" :style="{ fontSize: iconSize + 'px' }">{{ element.content || 'star' }}</span>
    </div>

    <div
      v-else-if="element.type === 'table'"
      class="w-full h-full cursor-move box-border overflow-hidden"
      :style="tableWrapStyle"
      @dblclick.stop
    >
      <table class="w-full h-full table-fixed border-collapse text-xs">
        <tbody>
          <tr v-for="(row, ri) in tableRows" :key="ri">
            <td
              v-for="(cell, ci) in row"
              :key="ci"
              class="px-1 py-0.5 align-top"
              :class="[
                editingCell?.ri === ri && editingCell?.ci === ci ? 'p-0' : 'truncate',
                cellBorderClass(ri, ci, row.length, tableRows.length),
              ]"
              :style="cellStyle(ri)"
              @dblclick.stop="startCellEdit(ri, ci)"
            >
              <input
                v-if="editingCell?.ri === ri && editingCell?.ci === ci"
                ref="cellInputRef"
                v-model="editCellValue"
                class="w-full h-full min-h-[22px] bg-white border border-primary outline-none px-1 text-inherit text-xs"
                @blur="commitCellEdit"
                @keydown.enter="commitCellEdit"
                @mousedown.stop
              />
              <span v-else class="block min-h-[18px]">{{ cell }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div
      v-else-if="element.type === 'chart'"
      class="w-full h-full cursor-move flex flex-col p-2"
      :style="{ background: element.style?.background || '#fff' }"
    >
      <div class="flex-1 flex items-end justify-around gap-1 min-h-0">
        <div
          v-for="(v, i) in chartValues"
          :key="i"
          class="flex-1 max-w-[20%] rounded-t-sm"
          :style="{ height: barHeight(v) + '%', background: element.style?.chartColor || '#005daa', minHeight: '4px' }"
        />
      </div>
    </div>

    <div
      v-else-if="element.type === 'image'"
      class="w-full h-full cursor-move flex items-center justify-center overflow-hidden"
      :style="{ background: element.style?.background || '#f0f0f0' }"
    >
      <img
        v-if="element.content && !imageCrop"
        :src="element.content"
        alt="素材"
        class="w-full h-full pointer-events-none"
        :class="imageObjectFitClass"
        draggable="false"
      />
      <div
        v-else-if="element.content && imageCrop"
        class="w-full h-full overflow-hidden relative"
      >
        <img
          :src="element.content"
          alt="素材"
          class="absolute pointer-events-none max-w-none"
          :style="croppedImageStyle"
          draggable="false"
        />
      </div>
      <span v-else class="material-symbols-outlined text-3xl text-on-surface-variant/50 pointer-events-none">image</span>
    </div>

    <div
      v-else-if="element.type === 'chartStack'"
      class="w-full h-full relative flex flex-col min-h-0"
      @dblclick.stop="openChartStackEditor"
    >
      <div
        v-if="selected && !readonly"
        class="shrink-0 z-30 h-6 px-3 cursor-move bg-white/95 border-b border-primary/25 shadow-sm flex items-center justify-center"
        @mousedown.stop="startDragFromHandle"
      >
        <span class="material-symbols-outlined text-[14px] text-primary pointer-events-none">drag_indicator</span>
      </div>
      <div class="flex-1 min-h-0 overflow-hidden">
        <ChartStack
          :cards="chartStackCards"
          :chart-color="element.style?.chartColor || '#005daa'"
          :interactive="true"
        />
      </div>
    </div>

    <div
      v-else-if="element.type === 'wordcloud'"
      class="w-full h-full cursor-move overflow-hidden"
      @dblclick.stop="openWordCloudEditor"
    >
      <canvas
        ref="wordCloudCanvasRef"
        class="w-full h-full pointer-events-none block"
      />
    </div>

    <template v-if="selected && !readonly">
      <span
        v-if="element.type === 'image'"
        class="absolute top-0 left-0 z-[60] text-[10px] leading-none bg-primary text-white px-1.5 py-0.5 rounded-br pointer-events-none antialiased"
      >已选中</span>
      <div
        v-for="handle in resizeHandles"
        :key="handle.corner"
        data-resize-handle
        class="absolute z-[70] w-2.5 h-2.5 rounded-sm shadow-sm"
        :class="handle.class"
        :style="handle.style"
        @mousedown.stop="(e) => startResize(e, handle.corner)"
      />
    </template>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { CANVAS_Z } from '../composables/useSlideCanvas.js'
import { renderWordCloud } from './wordcloud/WordCloudRenderer.js'
import ChartStack from './charts/ChartStack.vue'
import { selectionChromeForBackground } from '../utils/selectionChrome.js'

const props = defineProps({
  element: { type: Object, required: true },
  selected: { type: Boolean, default: false },
  readonly: { type: Boolean, default: false },
  scale: { type: Number, default: 1 },
  staggerIndex: { type: Number, default: -1 },
  themeId: { type: String, default: 'zjy-minimal' },
  canvasBackground: { type: String, default: '' },
  canvasBounds: { type: Object, default: () => ({ width: 9999, height: 9999 }) },
})

const emit = defineEmits(['select', 'update', 'remove', 'batch-start', 'batch-end', 'edit-wordcloud', 'edit-chart-stack', 'move-delta'])

const wordCloudCanvasRef = ref(null)

const editing = ref(false)
const editText = ref('')
const inputRef = ref(null)
const editingCell = ref(null)
const editCellValue = ref('')
const cellInputRef = ref(null)

const textStyle = computed(() => ({
  fontSize: (props.element.style?.fontSize || 16) + 'px',
  color: props.element.style?.color || '#1b1b1c',
  fontWeight: props.element.style?.fontWeight || 'normal',
  textAlign: props.element.style?.textAlign || 'left',
  background: props.element.style?.background || 'transparent',
  borderRadius: (props.element.style?.borderRadius || 0) + 'px',
  border: props.element.style?.border || 'none',
  fontFamily: props.element.style?.fontFamily || '"Microsoft YaHei", "PingFang SC", sans-serif',
  lineHeight: props.element.style?.lineHeight ?? 1.5,
  letterSpacing: (props.element.style?.letterSpacing ?? 0) + 'px',
}))

const shapeStyle = computed(() => ({
  background: props.element.style?.background || '#005daa',
  borderRadius: (props.element.style?.borderRadius || 8) + 'px',
  border: props.element.style?.border || 'none',
}))

const chartPlaceholderStyle = computed(() => ({
  background: props.element.style?.background || '#f0f2f5',
  borderRadius: (props.element.style?.borderRadius || 12) + 'px',
  border: props.element.style?.border || '2px dashed #636E72',
}))

const iconStyle = computed(() => ({
  background: props.element.style?.background || '#e8f0fe',
  color: props.element.style?.color || '#005daa',
  borderRadius: (props.element.style?.borderRadius || 8) + 'px',
}))

const iconSize = computed(() => Math.min(props.element.width, props.element.height) * 0.55)

const selectionChrome = computed(() =>
  selectionChromeForBackground(props.canvasBackground, props.themeId)
)

const selectionStyle = computed(() => {
  if (!props.selected || props.readonly) return {}
  const chrome = selectionChrome.value
  return {
    outline: `${chrome.outlineWidth}px solid ${chrome.ringColor}`,
    outlineOffset: '0px',
    boxShadow: chrome.shadow,
  }
})

const selectionRingClass = computed(() => {
  if (!props.selected || props.readonly) return ''
  return 'z-50'
})

const resizeHandles = computed(() => {
  if (!props.selected || props.readonly) return []
  const chrome = selectionChrome.value
  const baseStyle = {
    background: chrome.handleBg,
    border: `2px solid ${chrome.handleBorder}`,
  }
  return [
    { corner: 'nw', class: '-top-1.5 -left-1.5 cursor-nw-resize', style: baseStyle },
    { corner: 'ne', class: '-top-1.5 -right-1.5 cursor-ne-resize', style: baseStyle },
    { corner: 'sw', class: '-bottom-1.5 -left-1.5 cursor-sw-resize', style: baseStyle },
    { corner: 'se', class: '-bottom-1.5 -right-1.5 cursor-se-resize', style: baseStyle },
  ]
})

const imageCrop = computed(() => {
  const c = props.element.style?.crop
  if (!c || c.width == null) return null
  return c
})

const imageObjectFitClass = computed(() => {
  const fit = props.element.style?.objectFit
  if (fit === 'cover') return 'object-cover'
  if (fit === 'fill') return 'object-fill'
  return 'object-contain'
})

const croppedImageStyle = computed(() => {
  const c = imageCrop.value
  if (!c) return {}
  const invW = 1 / Math.max(c.width, 0.01)
  const invH = 1 / Math.max(c.height, 0.01)
  return {
    width: `${invW * 100}%`,
    height: `${invH * 100}%`,
    left: `${-c.x * invW * 100}%`,
    top: `${-c.y * invH * 100}%`,
    objectFit: 'fill',
  }
})

const staggerClass = computed(() =>
  props.readonly && props.staggerIndex >= 0 ? 'canvas-stagger-in' : ''
)
const staggerDelay = computed(() =>
  props.staggerIndex >= 0 ? `${props.staggerIndex * 80}ms` : undefined
)

const tableRows = computed(() => {
  const c = props.element.content
  if (c?.rows?.length) return c.rows
  return [['', '', ''], ['', '', ''], ['', '', '']]
})

const tableBorderColor = computed(() => props.element.style?.borderColor || '#c0c7d6')

const tableWrapStyle = computed(() => ({
  border: `1px solid ${tableBorderColor.value}`,
  background: props.element.style?.background || '#fff',
}))

function cellBorderClass(ri, ci, colCount, rowCount) {
  const parts = []
  if (ci < colCount - 1) parts.push('border-r')
  if (ri < rowCount - 1) parts.push('border-b')
  return parts.join(' ')
}

function cellStyle(ri) {
  const isHeader = ri === 0
  const color = tableBorderColor.value
  return {
    borderColor: color,
    background: isHeader
      ? props.element.style?.headerBackground || '#005daa'
      : props.element.style?.background || '#fff',
    color: isHeader ? props.element.style?.headerColor || '#fff' : props.element.style?.color || '#1b1b1c',
    fontWeight: isHeader ? '600' : 'normal',
  }
}

const chartValues = computed(() => {
  const c = props.element.content
  return c?.values?.length ? c.values : [35, 65, 45, 80, 55]
})

const chartStackCards = computed(() => {
  const c = props.element.content
  return c?.cards?.length ? c.cards : []
})

function openChartStackEditor() {
  if (props.readonly) return
  emit('edit-chart-stack', props.element)
}

function barHeight(v) {
  const max = Math.max(...chartValues.value, 1)
  return Math.max(8, (v / max) * 100)
}

function onRootMouseDown(e) {
  if (props.readonly) return
  if (props.element.type === 'chartPlaceholder') return
  const skipDrag = props.element.type === 'chartStack' && e.target.closest('.chart-stack')
  onSelect(e, !skipDrag)
}

function onSelect(e, allowDrag = true) {
  const payload = {
    id: props.element.id,
    ctrlKey: e.ctrlKey || e.metaKey,
    shiftKey: e.shiftKey,
  }
  emit('select', payload)
  if (e.target.closest('[data-resize-handle]')) return
  if (!allowDrag) return
  if (payload.ctrlKey || payload.shiftKey) return
  startDrag(e)
}

function startEdit() {
  if (props.readonly) return
  editing.value = true
  editText.value = props.element.content ?? ''
  nextTick(() => {
    inputRef.value?.focus()
    if (inputRef.value?.select) inputRef.value.select()
  })
}

function commitEdit() {
  editing.value = false
  emit('update', props.element.id, { content: editText.value })
}

function startCellEdit(ri, ci) {
  if (props.readonly) return
  editingCell.value = { ri, ci }
  editCellValue.value = tableRows.value[ri]?.[ci] ?? ''
  nextTick(() => cellInputRef.value?.focus())
}

function commitCellEdit() {
  if (!editingCell.value) return
  const { ri, ci } = editingCell.value
  const rows = tableRows.value.map((row) => [...row])
  if (rows[ri]) rows[ri][ci] = editCellValue.value
  editingCell.value = null
  emit('update', props.element.id, { content: { rows } })
}

function startDragFromHandle(e) {
  emit('select', { id: props.element.id, ctrlKey: false, shiftKey: false })
  startDrag(e)
}

function startDrag(e) {
  emit('batch-start', props.element.id)
  const startX = e.clientX
  const startY = e.clientY
  const s = props.scale

  function onMove(ev) {
    emit('move-delta', {
      dx: (ev.clientX - startX) / s,
      dy: (ev.clientY - startY) / s,
    })
  }
  function onUp() {
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
    emit('batch-end')
  }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

function startResize(e, corner = 'se') {
  emit('batch-start', props.element.id)
  const startX = e.clientX
  const startY = e.clientY
  const origX = props.element.x
  const origY = props.element.y
  const origW = props.element.width
  const origH = props.element.height
  const s = props.scale
  const minSize = 24
  const bounds = props.canvasBounds || { width: 9999, height: 9999 }

  function onMove(ev) {
    const dx = (ev.clientX - startX) / s
    const dy = (ev.clientY - startY) / s

    let x = origX
    let y = origY
    let w = origW
    let h = origH

    if (corner.includes('e')) {
      w = Math.max(minSize, origW + dx)
    }
    if (corner.includes('w')) {
      const newW = Math.max(minSize, origW - dx)
      x = origX + (origW - newW)
      w = newW
    }
    if (corner.includes('s')) {
      h = Math.max(minSize, origH + dy)
    }
    if (corner.includes('n')) {
      const newH = Math.max(minSize, origH - dy)
      y = origY + (origH - newH)
      h = newH
    }

    x = Math.max(0, x)
    y = Math.max(0, y)
    if (x + w > bounds.width) {
      if (corner.includes('w')) {
        x = Math.max(0, bounds.width - w)
        w = Math.min(w, bounds.width)
      } else {
        w = Math.max(minSize, bounds.width - x)
      }
    }
    if (y + h > bounds.height) {
      if (corner.includes('n')) {
        y = Math.max(0, bounds.height - h)
        h = Math.min(h, bounds.height)
      } else {
        h = Math.max(minSize, bounds.height - y)
      }
    }
    w = Math.max(minSize, Math.min(w, bounds.width - x))
    h = Math.max(minSize, Math.min(h, bounds.height - y))

    emit('update', props.element.id, { x, y, width: w, height: h })
  }
  function onUp() {
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
    emit('batch-end')
    if (props.element.type === 'wordcloud') nextTick(() => paintWordCloud())
  }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

watch(
  () => props.selected,
  (v) => {
    if (!v) {
      editing.value = false
      editingCell.value = null
    }
  }
)

function paintWordCloud() {
  if (props.element.type !== 'wordcloud' || !wordCloudCanvasRef.value) return
  const c = props.element.content
  if (!c || typeof c !== 'object') return
  const canvas = wordCloudCanvasRef.value
  const w = Math.max(100, Math.round(props.element.width))
  const h = Math.max(80, Math.round(props.element.height))
  canvas.width = w
  canvas.height = h
  renderWordCloud(canvas, c, props.themeId)
}

function openWordCloudEditor() {
  if (props.readonly) return
  emit('edit-wordcloud', props.element)
}

watch(
  () => [props.element.type, props.element.content],
  () => {
    if (props.element.type === 'wordcloud') nextTick(() => paintWordCloud())
  },
  { deep: true }
)

onMounted(() => {
  if (props.element.type === 'wordcloud') paintWordCloud()
})
</script>
