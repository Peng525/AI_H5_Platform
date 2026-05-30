<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 z-[110] flex items-center justify-center p-4 bg-black/50"
        @click.self="$emit('close')"
      >
        <div
          class="bg-white rounded-xl shadow-elevated border border-outline-variant w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]"
          role="dialog"
          aria-modal="true"
          aria-labelledby="crop-modal-title"
        >
          <div class="px-4 py-3 border-b border-outline-variant flex items-center justify-between shrink-0">
            <h2 id="crop-modal-title" class="font-semibold text-sm">裁切图片</h2>
            <button type="button" class="p-1 rounded hover:bg-surface-container" @click="$emit('close')">
              <span class="material-symbols-outlined text-lg">close</span>
            </button>
          </div>

          <div class="p-4 overflow-auto flex-1 min-h-0">
            <div
              ref="stageRef"
              class="relative mx-auto bg-surface-container-low rounded-lg overflow-hidden select-none"
              :style="stageStyle"
              @mousedown="onStageMouseDown"
            >
              <img
                ref="imgRef"
                :src="imageUrl"
                alt="裁切预览"
                class="block w-full h-full object-contain pointer-events-none"
                draggable="false"
                @load="onImageLoad"
              />
              <div class="absolute inset-0 bg-black/45 pointer-events-none" />
              <div
                class="absolute border-2 border-white shadow-[0_0_0_9999px_rgba(0,0,0,0.45)] cursor-move"
                :style="cropBoxStyle"
                @mousedown.stop="startMoveCrop"
              >
                <div
                  class="absolute -bottom-1 -right-1 w-3 h-3 bg-white border border-black/40 rounded-sm cursor-se-resize"
                  @mousedown.stop="startResizeCrop"
                />
              </div>
            </div>
            <p class="text-[11px] text-on-surface-variant mt-2 text-center">
              拖拽框体移动，右下角调整大小
            </p>
          </div>

          <div class="flex gap-2 px-4 py-3 border-t border-outline-variant bg-surface-container-low shrink-0">
            <button
              type="button"
              class="px-3 py-2 text-sm rounded-lg border border-outline-variant hover:bg-white"
              @click="$emit('reset')"
            >
              重置裁切
            </button>
            <button
              type="button"
              class="flex-1 py-2 text-sm rounded-lg border border-outline-variant hover:bg-white"
              @click="$emit('close')"
            >
              取消
            </button>
            <button
              type="button"
              class="flex-1 py-2 text-sm rounded-lg bg-primary text-on-primary font-medium"
              @click="confirm"
            >
              应用裁切
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  imageUrl: { type: String, default: '' },
  initialCrop: { type: Object, default: null },
})

const emit = defineEmits(['close', 'confirm', 'reset'])

const stageRef = ref(null)
const imgRef = ref(null)
const stageW = ref(320)
const stageH = ref(400)
const imageNatural = ref({ w: 1, h: 1 })
const displayRect = ref({ x: 0, y: 0, w: 320, h: 400 })

const cropNorm = ref({ x: 0.1, y: 0.1, width: 0.8, height: 0.8 })

const stageStyle = computed(() => ({
  width: stageW.value + 'px',
  height: stageH.value + 'px',
  maxWidth: '100%',
}))

const cropBoxStyle = computed(() => {
  const d = displayRect.value
  const c = cropNorm.value
  return {
    left: d.x + c.x * d.w + 'px',
    top: d.y + c.y * d.h + 'px',
    width: c.width * d.w + 'px',
    height: c.height * d.h + 'px',
  }
})

function clampCrop(c) {
  const min = 0.05
  let { x, y, width, height } = c
  width = Math.max(min, Math.min(1, width))
  height = Math.max(min, Math.min(1, height))
  x = Math.max(0, Math.min(1 - width, x))
  y = Math.max(0, Math.min(1 - height, y))
  return { x, y, width, height }
}

function updateDisplayRect() {
  const nw = imageNatural.value.w
  const nh = imageNatural.value.h
  if (!nw || !nh) return
  const sw = stageW.value
  const sh = stageH.value
  const scale = Math.min(sw / nw, sh / nh)
  const w = nw * scale
  const h = nh * scale
  displayRect.value = {
    x: (sw - w) / 2,
    y: (sh - h) / 2,
    w,
    h,
  }
}

function onImageLoad() {
  const img = imgRef.value
  if (!img) return
  imageNatural.value = { w: img.naturalWidth || 1, h: img.naturalHeight || 1 }
  const ratio = imageNatural.value.w / imageNatural.value.h
  stageW.value = Math.min(360, Math.round(400 * ratio))
  stageH.value = Math.min(480, Math.round(stageW.value / ratio))
  updateDisplayRect()
}

function normFromPointer(clientX, clientY) {
  const stage = stageRef.value
  const d = displayRect.value
  if (!stage) return { x: 0, y: 0 }
  const rect = stage.getBoundingClientRect()
  const px = clientX - rect.left - d.x
  const py = clientY - rect.top - d.y
  return {
    x: Math.max(0, Math.min(1, px / d.w)),
    y: Math.max(0, Math.min(1, py / d.h)),
  }
}

function startMoveCrop(e) {
  const start = { ...cropNorm.value }
  const origin = normFromPointer(e.clientX, e.clientY)

  function onMove(ev) {
    const cur = normFromPointer(ev.clientX, ev.clientY)
    cropNorm.value = clampCrop({
      x: start.x + (cur.x - origin.x),
      y: start.y + (cur.y - origin.y),
      width: start.width,
      height: start.height,
    })
  }
  function onUp() {
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
  }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

function startResizeCrop(e) {
  const start = { ...cropNorm.value }
  const origin = normFromPointer(e.clientX, e.clientY)

  function onMove(ev) {
    const cur = normFromPointer(ev.clientX, ev.clientY)
    cropNorm.value = clampCrop({
      x: start.x,
      y: start.y,
      width: start.width + (cur.x - origin.x),
      height: start.height + (cur.y - origin.y),
    })
  }
  function onUp() {
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
  }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

function onStageMouseDown(e) {
  if (e.target !== stageRef.value && !e.target?.classList?.contains('cursor-move')) return
  const p = normFromPointer(e.clientX, e.clientY)
  const size = 0.4
  cropNorm.value = clampCrop({
    x: p.x - size / 2,
    y: p.y - size / 2,
    width: size,
    height: size,
  })
}

function confirm() {
  emit('confirm', clampCrop({ ...cropNorm.value }))
}

watch(
  () => [props.open, props.imageUrl, props.initialCrop],
  () => {
    if (!props.open) return
    cropNorm.value = clampCrop(
      props.initialCrop?.width
        ? { ...props.initialCrop }
        : { x: 0.05, y: 0.05, width: 0.9, height: 0.9 }
    )
    if (imgRef.value?.complete && imgRef.value.naturalWidth) {
      onImageLoad()
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
