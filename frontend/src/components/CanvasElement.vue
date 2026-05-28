<template>
  <div
    class="absolute touch-none select-none"
    :class="selected ? 'ring-2 ring-primary ring-offset-1 z-50' : ''"
    :style="{
      left: element.x + 'px',
      top: element.y + 'px',
      width: element.width + 'px',
      height: element.height + 'px',
      zIndex: element.zIndex || 1,
    }"
    @mousedown.stop="onSelect"
  >
    <div
      v-if="element.type === 'text'"
      class="w-full h-full overflow-hidden px-1 cursor-move"
      :style="textStyle"
      @dblclick.stop="startEdit"
    >
      <input
        v-if="editing"
        ref="inputRef"
        v-model="editText"
        class="w-full h-full bg-white/90 border border-primary outline-none text-inherit px-1"
        :style="{ fontSize: element.style.fontSize + 'px', color: element.style.color }"
        @blur="commitEdit"
        @keydown.enter="commitEdit"
      />
      <span v-else class="block w-full h-full whitespace-pre-wrap break-words">{{ element.content }}</span>
    </div>

    <div
      v-else-if="element.type === 'shape'"
      class="w-full h-full cursor-move"
      :style="shapeStyle"
    />

    <img
      v-else-if="element.type === 'image'"
      :src="element.content"
      alt="素材"
      class="w-full h-full object-cover cursor-move pointer-events-none"
      draggable="false"
    />

    <template v-if="selected">
      <div
        class="absolute -bottom-1 -right-1 w-3 h-3 bg-primary rounded-sm cursor-se-resize"
        @mousedown.stop="startResize"
      />
    </template>
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'

const props = defineProps({
  element: { type: Object, required: true },
  selected: { type: Boolean, default: false },
  scale: { type: Number, default: 1 },
})

const emit = defineEmits(['select', 'update', 'remove'])

const editing = ref(false)
const editText = ref('')
const inputRef = ref(null)

const textStyle = computed(() => ({
  fontSize: (props.element.style?.fontSize || 16) + 'px',
  color: props.element.style?.color || '#1b1b1c',
  fontWeight: props.element.style?.fontWeight || 'normal',
  textAlign: props.element.style?.textAlign || 'left',
  background: props.element.style?.background || 'transparent',
  borderRadius: (props.element.style?.borderRadius || 0) + 'px',
}))

const shapeStyle = computed(() => ({
  background: props.element.style?.background || '#005daa',
  borderRadius: (props.element.style?.borderRadius || 8) + 'px',
}))

function onSelect(e) {
  emit('select', props.element.id)
  if (e.target.closest('.cursor-se-resize')) return
  startDrag(e)
}

function startEdit() {
  editing.value = true
  editText.value = props.element.content
  nextTick(() => inputRef.value?.focus())
}

function commitEdit() {
  editing.value = false
  emit('update', props.element.id, { content: editText.value })
}

function startDrag(e) {
  const startX = e.clientX
  const startY = e.clientY
  const origX = props.element.x
  const origY = props.element.y
  const s = props.scale

  function onMove(ev) {
    emit('update', props.element.id, {
      x: Math.max(0, origX + (ev.clientX - startX) / s),
      y: Math.max(0, origY + (ev.clientY - startY) / s),
    })
  }
  function onUp() {
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
  }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

function startResize(e) {
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
  }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

watch(
  () => props.selected,
  (v) => {
    if (!v) editing.value = false
  }
)
</script>
