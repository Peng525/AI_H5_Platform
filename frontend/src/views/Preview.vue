<template>
  <div class="fixed inset-0 bg-black z-50 flex flex-col" tabindex="0" @keydown="onKey">
    <div v-if="loading" class="text-white m-auto flex flex-col items-center gap-3">
      <div class="w-10 h-10 border-4 border-white/30 border-t-white rounded-full animate-spin" />
      加载演示…
    </div>
    <div v-else-if="error" class="text-red-400 m-auto text-center px-6">
      <p>{{ error }}</p>
      <router-link :to="`/editor/${$route.params.id}`" class="text-white underline mt-4 inline-block">返回编辑器</router-link>
    </div>
    <template v-else>
      <div class="absolute top-4 left-4 z-10 max-w-[240px] pointer-events-none">
        <p class="text-sm text-white font-semibold drop-shadow-md">{{ scrollModeInfo.label }}</p>
        <p class="text-xs text-white/85 mt-1 leading-relaxed drop-shadow">{{ scrollModeInfo.hint }}</p>
      </div>

      <div class="absolute top-4 right-4 z-20 flex items-center gap-2 flex-wrap justify-end">
        <PreviewSelect
          v-model="scrollEffect"
          :options="scrollOptions"
          @change="onScrollModeChange"
        />
        <span class="text-sm text-white font-medium tabular-nums min-w-[44px] text-center drop-shadow">{{ Math.round(userZoom) }}%</span>
        <button
          type="button"
          class="preview-toolbar-btn"
          title="重置缩放"
          @click="resetUserZoom"
        >
          重置
        </button>
        <PreviewSelect
          v-model="viewportId"
          :options="viewportOptions"
        />
        <button
          type="button"
          class="preview-toolbar-btn"
          @click="phoneFrame = !phoneFrame"
        >
          {{ phoneFrame ? '无边框' : '设备边框' }}
        </button>
      </div>

      <p
        v-if="slides.length <= 1 && scrollEffect !== 'page'"
        class="absolute top-16 left-1/2 -translate-x-1/2 z-10 text-xs text-amber-200 bg-amber-900/40 px-3 py-1 rounded-full"
      >
        添加多页后，滚动/滑动效果更明显
      </p>

      <!-- 翻页模式：单页 + 过渡动效 + 点击左右切换 -->
      <div
        v-if="scrollEffect === 'page'"
        class="flex-1 flex items-center justify-center p-4 overflow-hidden relative"
        @wheel.prevent="onWheelZoom"
      >
        <button
          type="button"
          class="absolute left-2 md:left-8 top-1/2 -translate-y-1/2 z-10 w-10 h-10 rounded-full bg-white/10 text-white border border-white/20 hover:bg-white/20 disabled:opacity-20"
          :disabled="index <= 0"
          aria-label="上一页"
          @click="prev"
        >
          ‹
        </button>
        <button
          type="button"
          class="absolute right-2 md:right-8 top-1/2 -translate-y-1/2 z-10 w-10 h-10 rounded-full bg-white/10 text-white border border-white/20 hover:bg-white/20 disabled:opacity-20"
          :disabled="index >= slides.length - 1"
          aria-label="下一页"
          @click="next"
        >
          ›
        </button>
        <div :class="outerFrameClass">
          <Transition :name="transitionName" mode="out-in">
            <div :key="index" :style="scaledWrapStyle">
              <PreviewSlideFrame
                :viewport="viewport"
                :elements="currentElements"
                :canvas-background="currentBackground"
                :slide="current"
                :slide-index="index"
                :slide-total="slides.length"
              />
            </div>
          </Transition>
        </div>
      </div>

      <!-- 纵向滚动 / 滚动吸附：同一滚动容器，整屏无间距，下滑无感切换 -->
      <div
        v-else-if="scrollEffect === 'vertical' || scrollEffect === 'snap'"
        ref="flowScrollRef"
        class="flex-1 min-h-0 overflow-y-auto overflow-x-hidden preview-flow-scroll snap-y snap-mandatory"
        @scroll="trackFlowScroll"
        @wheel="onFlowWheel"
      >
        <div
          v-for="(s, i) in slides"
          :key="s.id"
          class="preview-flow-panel snap-start snap-always flex items-center justify-center"
        >
          <div :style="scaledWrapStyle">
            <PreviewSlideFrame
              :viewport="viewport"
              :elements="elementsForSlide(s)"
              :canvas-background="backgroundForSlide(s.id)"
              :slide="s"
              :slide-index="i"
              :slide-total="slides.length"
            />
          </div>
        </div>
      </div>

      <!-- 横向滑动 -->
      <div
        v-else-if="scrollEffect === 'horizontal'"
        ref="horizontalScrollRef"
        class="flex-1 overflow-x-auto overflow-y-hidden flex flex-row preview-scroll-horizontal"
        @scroll="trackHorizontalScroll"
        @wheel.prevent="onHorizontalWheel"
      >
        <div
          v-for="(s, i) in slides"
          :key="s.id"
          class="min-w-full h-full flex items-center justify-center p-4 shrink-0"
        >
          <div :style="scaledWrapStyle">
            <PreviewSlideFrame
              :viewport="viewport"
              :elements="elementsForSlide(s)"
              :canvas-background="backgroundForSlide(s.id)"
              :slide="s"
              :slide-index="i"
              :slide-total="slides.length"
            />
          </div>
        </div>
      </div>

      <div class="flex justify-between items-center px-6 py-4 bg-black/60 text-white text-sm shrink-0 backdrop-blur-sm">
        <button
          type="button"
          class="disabled:opacity-30 px-3 py-1"
          :disabled="!canGoPrev"
          @click="goPrev"
        >
          {{ scrollEffect === 'horizontal' ? '← 上一页' : '上一页' }}
        </button>
        <span class="text-xs text-center max-w-[50%]">{{ footerStatus }}</span>
        <div class="flex items-center gap-3">
          <button
            type="button"
            class="disabled:opacity-30 px-3 py-1"
            :disabled="!canGoNext"
            @click="goNext"
          >
            {{ scrollEffect === 'horizontal' ? '下一页 →' : '下一页' }}
          </button>
          <router-link :to="`/editor/${$route.params.id}`" class="underline opacity-80">退出</router-link>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/client'
import PreviewSlideFrame from '../components/PreviewSlideFrame.vue'
import PreviewSelect from '../components/PreviewSelect.vue'
import { loadSlideBackground, resolvePreviewElements } from '../composables/useSlideCanvas'
import { VIEWPORT_PRESETS, getViewportPreset, SCROLL_EFFECTS } from '../constants/editorPresets'
import { getSlideAnimation } from '../utils/slideAnimation'

const route = useRoute()
const project = ref(null)
const index = ref(0)
const visibleIndex = ref(0)
const loading = ref(true)
const error = ref('')
const phoneFrame = ref(true)
const viewportId = ref('mobile-375')
const scrollEffect = ref('page')
const userZoom = ref(100)

const flowScrollRef = ref(null)
const horizontalScrollRef = ref(null)
const flowWheelLock = ref(false)

const scrollOptions = computed(() => SCROLL_EFFECTS.map((s) => ({ value: s.id, label: s.label })))
const viewportOptions = computed(() => [
  ...mobileViewports.map((v) => ({ value: v.id, label: v.label })),
  ...webViewports.map((v) => ({ value: v.id, label: v.label })),
])

const MIN_ZOOM = 25
const MAX_ZOOM = 200
const ZOOM_STEP = 5

const mobileViewports = VIEWPORT_PRESETS.filter((v) => v.device === 'mobile')
const webViewports = VIEWPORT_PRESETS.filter((v) => v.device === 'web')

const projectId = computed(() => Number(route.params.id))
const slides = computed(() => project.value?.slides || [])
const current = computed(() => slides.value[index.value] || {})
const viewport = computed(() => getViewportPreset(viewportId.value))

const scrollModeInfo = computed(() => {
  const m = SCROLL_EFFECTS.find((s) => s.id === scrollEffect.value)
  const hints = {
    page: '空格 / 方向键 / 左右按钮切换整页',
    vertical: '滚轮或键盘 ↓ 下滑，整屏无感切换',
    horizontal: '滚轮或拖动左右切换，每页占满宽度',
    snap: '滚轮滑动后自动吸附到整屏',
  }
  return { label: m?.label || '翻页模式', hint: hints[scrollEffect.value] || m?.desc || '' }
})

const currentElements = computed(() => resolvePreviewElements(projectId.value, current.value))

const currentBackground = computed(() => {
  const slide = current.value
  if (!slide?.id) return '#005daa'
  return loadSlideBackground(projectId.value, slide.id)
})

const transitionName = computed(() => {
  const anim = getSlideAnimation(current.value)
  const map = {
    fade: 'slide-fade',
    'slide-left': 'slide-left',
    'slide-right': 'slide-right',
    'slide-up': 'slide-up',
    zoom: 'slide-zoom',
    flip: 'slide-flip',
    none: 'slide-none',
  }
  return map[anim] || 'slide-fade'
})

const previewScale = computed(() => {
  const maxW = phoneFrame.value ? 420 : 900
  const maxH = phoneFrame.value ? 720 : 600
  return Math.min(1, maxW / viewport.value.width, maxH / viewport.value.height)
})

const displayScale = computed(() => {
  const raw = previewScale.value * (userZoom.value / 100)
  return Math.round(raw * 100) / 100
})

const scaledWrapStyle = computed(() => ({
  transform: `scale(${displayScale.value})`,
  transformOrigin: 'center center',
  WebkitFontSmoothing: 'antialiased',
  MozOsxFontSmoothing: 'grayscale',
}))

const outerFrameClass = computed(() => 'overflow-visible')

const footerStatus = computed(() => {
  const total = slides.value.length
  if (scrollEffect.value === 'page') {
    return `翻页模式 · ${index.value + 1}/${total}`
  }
  if (scrollEffect.value === 'vertical' || scrollEffect.value === 'snap') {
    return `${scrollEffect.value === 'vertical' ? '纵向滚动' : '滚动吸附'} · ${visibleIndex.value + 1}/${total}`
  }
  if (scrollEffect.value === 'horizontal') {
    return `横向滑动 · ${visibleIndex.value + 1}/${total}`
  }
  return `${visibleIndex.value + 1}/${total}`
})

const canGoPrev = computed(() => {
  if (scrollEffect.value === 'page') return index.value > 0
  return visibleIndex.value > 0
})

const canGoNext = computed(() => {
  const total = slides.value.length
  if (scrollEffect.value === 'page') return index.value < total - 1
  return visibleIndex.value < total - 1
})

function elementsForSlide(slide) {
  return resolvePreviewElements(projectId.value, slide)
}

function backgroundForSlide(slideId) {
  return loadSlideBackground(projectId.value, slideId)
}

function loadProjectSettings() {
  try {
    const raw = localStorage.getItem(`ai_h5_project_settings_${route.params.id}`)
    if (raw) {
      const s = JSON.parse(raw)
      if (s.viewportId) viewportId.value = s.viewportId
      if (s.scrollEffect) scrollEffect.value = s.scrollEffect
    }
  } catch { /* ignore */ }
}

function persistScrollEffect() {
  try {
    const key = `ai_h5_project_settings_${route.params.id}`
    const s = JSON.parse(localStorage.getItem(key) || '{}')
    s.scrollEffect = scrollEffect.value
    localStorage.setItem(key, JSON.stringify(s))
  } catch { /* ignore */ }
}

function onScrollModeChange() {
  persistScrollEffect()
  index.value = 0
  visibleIndex.value = 0
  nextTick(() => scrollToVisible(0, 'auto'))
}

function scrollToVisible(i, behavior = 'smooth') {
  if (scrollEffect.value === 'horizontal') {
    const el = horizontalScrollRef.value
    if (el) el.scrollTo({ left: i * el.clientWidth, behavior })
  } else if (scrollEffect.value === 'vertical' || scrollEffect.value === 'snap') {
    const el = flowScrollRef.value
    if (!el) return
    const h = el.clientHeight
    el.scrollTo({ top: i * h, behavior })
  }
}

function trackFlowScroll(e) {
  const el = e.target
  if (!el.clientHeight) return
  visibleIndex.value = Math.min(
    slides.value.length - 1,
    Math.max(0, Math.round(el.scrollTop / el.clientHeight))
  )
}

function onFlowWheel(e) {
  if (scrollEffect.value !== 'vertical' && scrollEffect.value !== 'snap') return
  e.preventDefault()
  if (flowWheelLock.value) return
  const dir = e.deltaY > 0 ? 1 : e.deltaY < 0 ? -1 : 0
  if (!dir) return
  const next = visibleIndex.value + dir
  if (next < 0 || next >= slides.value.length) return
  flowWheelLock.value = true
  scrollToVisible(next, 'smooth')
  window.setTimeout(() => {
    flowWheelLock.value = false
  }, 520)
}

function trackHorizontalScroll(e) {
  const el = e.target
  if (!el.clientWidth) return
  visibleIndex.value = Math.min(slides.value.length - 1, Math.max(0, Math.round(el.scrollLeft / el.clientWidth)))
}

function onHorizontalWheel(e) {
  const el = horizontalScrollRef.value
  if (!el) return
  el.scrollLeft += e.deltaY + e.deltaX
}

onMounted(async () => {
  loadProjectSettings()
  try {
    project.value = await api.getProject(projectId.value)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

watch(viewportId, () => {
  resetUserZoom()
  try {
    const key = `ai_h5_project_settings_${route.params.id}`
    const s = JSON.parse(localStorage.getItem(key) || '{}')
    s.viewportId = viewportId.value
    localStorage.setItem(key, JSON.stringify(s))
  } catch { /* ignore */ }
})

function resetUserZoom() {
  userZoom.value = 100
}

function clampUserZoom(v) {
  return Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, Math.round(v)))
}

function onWheelZoom(e) {
  const step = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP
  userZoom.value = clampUserZoom(userZoom.value + step)
}

function prev() {
  if (index.value > 0) index.value--
}

function next() {
  if (index.value < slides.value.length - 1) index.value++
}

function goPrev() {
  if (scrollEffect.value === 'page') {
    prev()
    return
  }
  scrollToVisible(Math.max(0, visibleIndex.value - 1))
}

function goNext() {
  if (scrollEffect.value === 'page') {
    next()
    return
  }
  scrollToVisible(Math.min(slides.value.length - 1, visibleIndex.value + 1))
}

function onKey(e) {
  if (scrollEffect.value === 'page') {
    if (e.key === 'ArrowRight' || e.key === ' ') {
      e.preventDefault()
      next()
    }
    if (e.key === 'ArrowLeft') prev()
    return
  }
  if (scrollEffect.value === 'horizontal') {
    if (e.key === 'ArrowRight') {
      e.preventDefault()
      goNext()
    }
    if (e.key === 'ArrowLeft') goPrev()
    return
  }
  if (scrollEffect.value === 'vertical' || scrollEffect.value === 'snap') {
    if (e.key === 'ArrowDown' || e.key === ' ') {
      e.preventDefault()
      goNext()
    }
    if (e.key === 'ArrowUp') goPrev()
  }
}
</script>

<style scoped>
.preview-toolbar-btn {
  font-size: 13px;
  font-weight: 500;
  color: #fff;
  background: rgba(20, 24, 32, 0.92);
  border: 1px solid rgba(255, 255, 255, 0.28);
  border-radius: 8px;
  padding: 8px 12px;
  backdrop-filter: blur(8px);
}
.preview-toolbar-btn:hover {
  background: rgba(40, 44, 52, 0.95);
}
.preview-flow-scroll {
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior-y: contain;
}
.preview-flow-panel {
  height: 100%;
  min-height: 100%;
  flex-shrink: 0;
  scroll-snap-stop: always;
}
.preview-scroll-horizontal {
  scroll-behavior: smooth;
  scroll-snap-type: x mandatory;
}
.preview-scroll-horizontal > div {
  scroll-snap-align: center;
}
</style>
