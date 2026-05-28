<template>
  <div class="space-y-2">
    <p class="text-xs text-on-surface-variant">请拖动滑块完成拼图</p>
    <div class="relative h-40 rounded-lg overflow-hidden border border-outline-variant bg-surface-container select-none">
      <div
        class="absolute inset-0 bg-gradient-to-br from-primary/30 to-primary-container/40"
        :style="{ backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(0,93,170,0.08) 10px, rgba(0,93,170,0.08) 20px)' }"
      />
      <div
        class="absolute w-12 h-12 rounded-lg border-2 border-white shadow-lg overflow-hidden"
        :style="{
          left: gapX + 'px',
          top: gapY + 'px',
          background: 'linear-gradient(135deg, #0075d5, #005daa)',
        }"
      />
      <div
        class="absolute w-12 h-12 rounded-lg border-2 border-dashed border-primary/60 bg-white/20"
        :style="{ left: targetX + 'px', top: gapY + 'px' }"
      />
      <div
        v-if="verified"
        class="absolute inset-0 bg-secondary/20 flex items-center justify-center text-secondary font-medium text-sm"
      >
        <span class="material-symbols-outlined mr-1">check_circle</span>
        验证成功
      </div>
    </div>

    <div class="relative h-10 bg-surface-container-low rounded-full border border-outline-variant overflow-hidden">
      <div
        class="absolute inset-y-0 left-0 bg-primary/10 transition-all"
        :style="{ width: sliderX + 40 + 'px' }"
      />
      <div
        class="absolute top-0.5 left-0.5 w-9 h-9 bg-primary text-on-primary rounded-full flex items-center justify-center cursor-grab active:cursor-grabbing shadow-sm z-10"
        :style="{ transform: `translateX(${sliderX}px)` }"
        @mousedown="startDrag"
        @touchstart.prevent="startTouch"
      >
        <span class="material-symbols-outlined text-[18px]">chevron_right</span>
      </div>
      <span v-if="!verified && !dragging" class="absolute inset-0 flex items-center justify-center text-xs text-on-surface-variant pointer-events-none">
        向右拖动滑块
      </span>
    </div>
    <button v-if="failed" type="button" class="text-xs text-primary" @click="reset">验证失败，点击重试</button>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'

const emit = defineEmits(['verified'])

const gapY = 60
const targetX = ref(180)
const gapX = ref(40)
const sliderX = ref(0)
const verified = ref(false)
const failed = ref(false)
const dragging = ref(false)
const maxSlide = 260

function randomize() {
  targetX.value = 120 + Math.floor(Math.random() * 100)
  gapX.value = 20 + Math.floor(Math.random() * 40)
  sliderX.value = 0
  verified.value = false
  failed.value = false
  emit('verified', false)
}

function startDrag(e) {
  if (verified.value) return
  dragging.value = true
  const startX = e.clientX
  const orig = sliderX.value

  function onMove(ev) {
    sliderX.value = Math.max(0, Math.min(maxSlide, orig + ev.clientX - startX))
    gapX.value = 20 + (sliderX.value / maxSlide) * (targetX.value - 20)
  }
  function onUp() {
    dragging.value = false
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
    checkResult()
  }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

function startTouch(e) {
  if (verified.value) return
  dragging.value = true
  const startX = e.touches[0].clientX
  const orig = sliderX.value

  function onMove(ev) {
    sliderX.value = Math.max(0, Math.min(maxSlide, orig + ev.touches[0].clientX - startX))
    gapX.value = 20 + (sliderX.value / maxSlide) * (targetX.value - 20)
  }
  function onEnd() {
    dragging.value = false
    window.removeEventListener('touchmove', onMove)
    window.removeEventListener('touchend', onEnd)
    checkResult()
  }
  window.addEventListener('touchmove', onMove)
  window.addEventListener('touchend', onEnd)
}

function checkResult() {
  const diff = Math.abs(gapX.value - targetX.value)
  if (diff <= 8) {
    verified.value = true
    failed.value = false
    sliderX.value = maxSlide
    gapX.value = targetX.value
    emit('verified', true)
  } else {
    failed.value = true
    setTimeout(() => {
      sliderX.value = 0
      gapX.value = 20 + Math.floor(Math.random() * 40)
    }, 400)
    emit('verified', false)
  }
}

function reset() {
  randomize()
}

onMounted(randomize)

watch(verified, (v) => emit('verified', v))
</script>
