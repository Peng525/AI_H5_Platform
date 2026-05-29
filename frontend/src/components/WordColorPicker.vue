<template>
  <div ref="rootRef" class="relative shrink-0">
    <button
      ref="btnRef"
      type="button"
      class="flex flex-col items-center gap-0.5 p-1 rounded hover:bg-surface-container"
      :class="open ? 'bg-surface-container-high ring-1 ring-primary/30' : ''"
      :title="label"
      @mousedown.stop
      @click.stop="toggleOpen"
    >
      <span class="material-symbols-outlined text-[18px] text-on-surface-variant">{{ icon }}</span>
      <span
        class="w-5 h-1 rounded-sm border border-outline-variant/50"
        :style="{ background: modelValue || '#000000' }"
      />
    </button>

    <Teleport to="body">
      <div v-if="open">
        <div
          class="fixed inset-0 z-[1200] bg-transparent"
          aria-hidden="true"
          @click.self="close"
          @mousedown.self.prevent
        />
        <div
          ref="panelRef"
          class="fixed z-[1210] bg-white border border-outline-variant rounded-lg shadow-xl p-3 w-[220px] text-xs"
          :style="panelStyle"
          role="dialog"
          :aria-label="label"
          @mousedown.stop
          @click.stop
        >
          <p class="text-on-surface-variant mb-1.5 font-medium">主题颜色</p>
          <div class="grid grid-cols-8 gap-1 mb-3">
            <button
              v-for="c in THEME_COLORS"
              :key="'t-' + c"
              type="button"
              class="w-5 h-5 rounded-sm border border-black/10 hover:scale-110 transition-transform"
              :style="{ background: c }"
              :title="c"
              @mousedown.prevent
              @click="pick(c)"
            />
          </div>
          <p class="text-on-surface-variant mb-1.5 font-medium">标准色</p>
          <div class="grid grid-cols-8 gap-1 mb-3">
            <button
              v-for="c in STANDARD_COLORS"
              :key="'s-' + c"
              type="button"
              class="w-5 h-5 rounded-sm border border-black/10 hover:scale-110 transition-transform"
              :class="c === '#FFFFFF' ? 'ring-1 ring-inset ring-gray-300' : ''"
              :style="{ background: c }"
              :title="c"
              @mousedown.prevent
              @click="pick(c)"
            />
          </div>
          <div class="flex items-center gap-2 pt-2 border-t border-outline-variant">
            <span class="text-on-surface-variant shrink-0">其他</span>
            <input
              type="color"
              :value="modelValue || '#000000'"
              class="w-8 h-8 border-0 cursor-pointer p-0"
              @input="pick($event.target.value)"
            />
            <input
              :value="hexInput"
              type="text"
              maxlength="7"
              placeholder="#000000"
              class="flex-1 border border-outline-variant rounded px-1.5 py-1 text-[11px] uppercase"
              @change="pickHex"
            />
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import {
  closeColorPickerSession,
  openColorPickerSession,
} from '../composables/useColorPickerSession'
import { STANDARD_COLORS, THEME_COLORS } from '../constants/textFormats'

const props = defineProps({
  modelValue: { type: String, default: '#000000' },
  label: { type: String, default: '字体颜色' },
  icon: { type: String, default: 'format_color_text' },
  /** 画布上下文变化时自动关闭（如切换视口 / 页面 / 选中元素） */
  contextKey: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue', 'change'])

const open = ref(false)
const rootRef = ref(null)
const btnRef = ref(null)
const panelRef = ref(null)
const hexInput = ref(props.modelValue || '#000000')
const panelStyle = ref({ top: '0px', left: '0px', visibility: 'hidden' })

const PANEL_WIDTH = 220
const PANEL_HEIGHT = 280

watch(
  () => props.modelValue,
  (v) => {
    hexInput.value = v || '#000000'
  }
)

watch(
  () => props.contextKey,
  () => {
    if (open.value) close()
  }
)

function positionFromButton(btn) {
  const anchor = btn || btnRef.value
  if (!anchor) return false
  const rect = anchor.getBoundingClientRect()
  if (!rect.width && !rect.height) return false

  let top = rect.bottom + 6
  let left = rect.left

  if (left + PANEL_WIDTH > window.innerWidth - 8) {
    left = Math.max(8, window.innerWidth - PANEL_WIDTH - 8)
  }
  if (top + PANEL_HEIGHT > window.innerHeight - 8) {
    top = Math.max(8, rect.top - PANEL_HEIGHT - 6)
  }

  panelStyle.value = {
    top: `${top}px`,
    left: `${left}px`,
    visibility: 'visible',
  }
  return true
}

async function schedulePosition(btn) {
  await nextTick()
  requestAnimationFrame(() => {
    positionFromButton(btn)
    requestAnimationFrame(() => positionFromButton(btn))
  })
}

async function toggleOpen(event) {
  if (open.value) {
    close()
    return
  }
  open.value = true
  openColorPickerSession(close)
  panelStyle.value = { top: '0px', left: '0px', visibility: 'hidden' }
  await schedulePosition(event?.currentTarget)
}

function close() {
  if (!open.value) return
  open.value = false
  closeColorPickerSession(close)
}

function pick(c) {
  hexInput.value = c
  emit('update:modelValue', c)
  emit('change', c)
  close()
}

function pickHex(e) {
  let v = e.target.value.trim()
  if (!v.startsWith('#')) v = `#${v}`
  if (/^#[0-9A-Fa-f]{6}$/.test(v)) pick(v)
}

function onKeyDown(e) {
  if (e.key === 'Escape') close()
}

function onReposition() {
  if (open.value) positionFromButton()
}

onMounted(() => {
  window.addEventListener('keydown', onKeyDown)
  window.addEventListener('resize', onReposition)
  window.addEventListener('scroll', onReposition, true)
})
onUnmounted(() => {
  close()
  window.removeEventListener('keydown', onKeyDown)
  window.removeEventListener('resize', onReposition)
  window.removeEventListener('scroll', onReposition, true)
})
</script>
