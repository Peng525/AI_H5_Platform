<template>
  <div
    class="absolute select-none"
    :class="[
      readonly ? 'pointer-events-none' : 'touch-none',
      selected && !readonly ? 'ring-2 ring-primary ring-offset-1 z-50' : '',
      staggerClass,
    ]"
    :style="{
      left: element.x + 'px',
      top: element.y + 'px',
      width: element.width + 'px',
      height: element.height + 'px',
      zIndex: element.zIndex || 1,
      animationDelay: staggerDelay,
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
        v-if="element.content"
        :src="element.content"
        alt="素材"
        class="w-full h-full pointer-events-none"
        :class="element.style?.objectFit === 'cover' ? 'object-cover' : 'object-contain'"
        draggable="false"
      />
      <span v-else class="material-symbols-outlined text-3xl text-on-surface-variant/50 pointer-events-none">image</span>
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
      <div
        class="absolute -bottom-1 -right-1 w-3 h-3 bg-primary rounded-sm cursor-se-resize"
        @mousedown.stop="startResize"
      />
    </template>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { renderWordCloud } from './wordcloud/WordCloudRenderer.js'

const props = defineProps({
  element: { type: Object, required: true },
  selected: { type: Boolean, default: false },
  readonly: { type: Boolean, default: false },
  scale: { type: Number, default: 1 },
  staggerIndex: { type: Number, default: -1 },
  themeId: { type: String, default: 'zjy-minimal' },
})

const emit = defineEmits(['select', 'update', 'remove', 'batch-start', 'batch-end', 'edit-wordcloud', 'move-delta'])

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
}))

const iconStyle = computed(() => ({
  background: props.element.style?.background || '#e8f0fe',
  color: props.element.style?.color || '#005daa',
  borderRadius: (props.element.style?.borderRadius || 8) + 'px',
}))

const iconSize = computed(() => Math.min(props.element.width, props.element.height) * 0.55)

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

function barHeight(v) {
  const max = Math.max(...chartValues.value, 1)
  return Math.max(8, (v / max) * 100)
}

function onRootMouseDown(e) {
  if (props.readonly) return
  onSelect(e)
}

function onSelect(e) {
  const payload = {
    id: props.element.id,
    ctrlKey: e.ctrlKey || e.metaKey,
    shiftKey: e.shiftKey,
  }
  emit('select', payload)
  if (e.target.closest('.cursor-se-resize')) return
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

function startResize(e) {
  emit('batch-start', props.element.id)
  const startX = e.clientX
  const startY = e.clientY
  const origW = props.element.width
  const origH = props.element.height
  const s = props.scale

  function onMove(ev) {
    emit('update', props.element.id, {
      width: Math.max(24, origW + (ev.clientX - startX) / s),
      height: Math.max(24, origH + (ev.clientY - startY) / s),
    })
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
