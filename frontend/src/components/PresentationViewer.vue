<template>
  <div
    class="inset-0 bg-black flex flex-col"
    :class="embedded ? 'absolute z-0' : 'fixed z-50'"
    tabindex="0"
    @keydown="onKey"
    @click="onRootClick"
  >
    <div v-if="loading" class="text-white m-auto flex flex-col items-center gap-3">
      <div class="w-10 h-10 border-4 border-white/30 border-t-white rounded-full animate-spin" />
      {{ loadingText }}
    </div>
    <div v-else-if="error" class="text-red-400 m-auto text-center px-6">
      <p>{{ error }}</p>
      <router-link v-if="editorPath" :to="editorPath" class="text-white underline mt-4 inline-block">返回编辑器</router-link>
    </div>
    <template v-else-if="project">
      <div
        v-if="bgmHintVisible && !embedded"
        class="absolute top-20 left-1/2 -translate-x-1/2 z-40 text-xs text-white bg-black/70 px-4 py-2 rounded-full pointer-events-none"
      >
        点击屏幕开启背景音乐
      </div>

      <div
        v-if="scrollHintVisible && !embedded"
        class="absolute bottom-24 left-1/2 -translate-x-1/2 z-40 text-xs text-white bg-black/60 px-4 py-2 rounded-full pointer-events-none animate-bounce"
      >
        上滑继续 ↓
      </div>

      <div v-if="!embedded" class="absolute top-4 left-4 z-10 max-w-[240px] pointer-events-none">
        <p class="text-sm text-white font-semibold drop-shadow-md">{{ scrollModeInfo.label }}</p>
        <p class="text-xs text-white/85 mt-1 leading-relaxed drop-shadow">{{ scrollModeInfo.hint }}</p>
      </div>

      <div class="absolute top-4 right-4 z-20 flex items-center gap-2 flex-wrap justify-end">
        <template v-if="mode === 'preview'">
          <PreviewSelect v-model="scrollEffect" :options="scrollOptions" @change="onScrollModeChange" />
          <span class="text-sm text-white font-medium tabular-nums min-w-[44px] text-center drop-shadow">{{ Math.round(userZoom) }}%</span>
          <button type="button" class="preview-toolbar-btn" title="重置缩放" @click="resetUserZoom">重置</button>
          <PreviewSelect v-model="viewportId" :options="viewportOptions" />
          <button type="button" class="preview-toolbar-btn" @click="phoneFrame = !phoneFrame">
            {{ phoneFrame ? '无边框' : '设备边框' }}
          </button>
          <button
            type="button"
            class="preview-toolbar-btn preview-toolbar-btn-exit"
            title="退出预览 (Esc)"
            @click="exitPreview"
          >
            <span class="material-symbols-outlined text-[18px]">close</span>
            退出
          </button>
        </template>
      </div>

      <div v-if="slides.length === 0" class="flex-1 flex items-center justify-center p-8 text-center text-white/80 text-sm">
        <p>该模板暂无试看页面，请点击「使用此模板」创建项目后编辑。</p>
      </div>

      <div
        v-else-if="scrollEffect === 'page'"
        class="flex-1 flex items-center justify-center p-4 overflow-hidden relative"
        @wheel.prevent="onWheelZoom"
      >
        <button
          type="button"
          class="absolute left-2 md:left-8 top-1/2 -translate-y-1/2 z-10 w-10 h-10 rounded-full bg-white/10 text-white border border-white/20 hover:bg-white/20 disabled:opacity-20"
          :disabled="!canGoPrev"
          aria-label="上一页"
          @click="goPrev"
        >
          ‹
        </button>
        <button
          type="button"
          class="absolute right-2 md:right-8 top-1/2 -translate-y-1/2 z-10 w-10 h-10 rounded-full bg-white/10 text-white border border-white/20 hover:bg-white/20 disabled:opacity-20"
          :disabled="!canGoNext"
          aria-label="下一页"
          @click="goNext"
        >
          ›
        </button>
        <div class="overflow-visible">
          <Transition :name="transitionName" mode="out-in">
            <div :key="index" class="relative" :style="scaledWrapStyle">
              <PreviewSlideFrame
                :viewport="viewport"
                :elements="currentElements"
                :canvas-background="currentBackground"
                :slide="current"
                :slide-index="index"
                :slide-total="slides.length"
                :enable-stagger="!embedded"
                :show-bgm-player="bgmPlayerActive"
                :bgm-muted="bgmMuted"
                :bgm-spinning="bgmPlaying && !bgmMuted"
                @toggle-bgm-mute="toggleBgmMute"
              />
              <ChatStoryOverlay
                :script="slideChatScript(current)"
                :active="!!slideChatScript(current)"
                @complete="onChatComplete"
              />
            </div>
          </Transition>
        </div>
      </div>

      <div
        v-else-if="scrollEffect === 'vertical' || scrollEffect === 'snap'"
        ref="flowScrollRef"
        class="flex-1 min-h-0 overflow-y-auto overflow-x-hidden preview-flow-scroll snap-y snap-mandatory"
        :class="{ 'overflow-hidden': chatBlocking }"
        @scroll="trackFlowScroll"
        @wheel="onFlowWheel"
      >
        <div
          v-for="(s, i) in slides"
          :key="s.id"
          class="preview-flow-panel snap-start snap-always flex items-center justify-center"
        >
          <div class="relative" :style="scaledWrapStyle">
            <PreviewSlideFrame
              :viewport="viewport"
              :elements="elementsForSlide(s)"
              :canvas-background="backgroundForSlide(s)"
              :slide="s"
              :slide-index="i"
              :slide-total="slides.length"
              :enable-stagger="!embedded && i === visibleIndex"
              :show-bgm-player="bgmPlayerActive && i === visibleIndex"
              :bgm-muted="bgmMuted"
              :bgm-spinning="bgmPlaying && !bgmMuted"
              @toggle-bgm-mute="toggleBgmMute"
            />
            <ChatStoryOverlay
              v-if="i === visibleIndex"
              :script="slideChatScript(s)"
              :active="!!slideChatScript(s)"
              @complete="onChatComplete"
            />
          </div>
        </div>
      </div>

      <div
        v-else-if="scrollEffect === 'horizontal'"
        ref="horizontalScrollRef"
        class="flex-1 overflow-x-auto overflow-y-hidden flex flex-row preview-scroll-horizontal"
        :class="{ 'overflow-hidden': chatBlocking }"
        @scroll="trackHorizontalScroll"
        @wheel.prevent="onHorizontalWheel"
      >
        <div
          v-for="(s, i) in slides"
          :key="s.id"
          class="min-w-full h-full flex items-center justify-center p-4 shrink-0"
        >
          <div class="relative" :style="scaledWrapStyle">
            <PreviewSlideFrame
              :viewport="viewport"
              :elements="elementsForSlide(s)"
              :canvas-background="backgroundForSlide(s)"
              :slide="s"
              :slide-index="i"
              :slide-total="slides.length"
              :enable-stagger="!embedded && i === visibleIndex"
              :show-bgm-player="bgmPlayerActive && i === visibleIndex"
              :bgm-muted="bgmMuted"
              :bgm-spinning="bgmPlaying && !bgmMuted"
              @toggle-bgm-mute="toggleBgmMute"
            />
            <ChatStoryOverlay
              v-if="i === visibleIndex"
              :script="slideChatScript(s)"
              :active="!!slideChatScript(s)"
              @complete="onChatComplete"
            />
          </div>
        </div>
      </div>

      <div v-if="!embedded" class="flex justify-between items-center px-6 py-4 bg-black/60 text-white text-sm shrink-0 backdrop-blur-sm">
        <button type="button" class="disabled:opacity-30 px-3 py-1" :disabled="!canGoPrev" @click="goPrev">
          {{ scrollEffect === 'horizontal' ? '← 上一页' : '上一页' }}
        </button>
        <span class="text-xs text-center max-w-[50%]">{{ footerStatus }}</span>
        <div class="flex items-center gap-3">
          <button type="button" class="disabled:opacity-30 px-3 py-1" :disabled="!canGoNext" @click="goNext">
            {{ scrollEffect === 'horizontal' ? '下一页 →' : '下一页' }}
          </button>
          <button
            v-if="editorPath"
            type="button"
            class="preview-footer-exit"
            @click="exitPreview"
          >
            退出预览
          </button>
        </div>
      </div>

      <footer v-if="mode === 'share' && !embedded" class="py-2 text-center text-xs text-white/40 border-t border-white/10 shrink-0">
        AI智能H5演示平台 · 分享预览
      </footer>
    </template>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import ChatStoryOverlay from './ChatStoryOverlay.vue'
import PreviewSlideFrame from './PreviewSlideFrame.vue'
import PreviewSelect from './PreviewSelect.vue'
import {
  mergeProjectSettings,
  resolveSlideBackground,
  usePresentationPlayback,
} from '../composables/usePresentationPlayback'
import { resolvePreviewElements } from '../composables/useSlideCanvas'
import { VIEWPORT_PRESETS, getViewportPreset, SCROLL_EFFECTS } from '../constants/editorPresets'
import { getSlideAnimation } from '../utils/slideAnimation'
import { DEFAULT_CANVAS_BG } from '../constants/canvasBackgrounds.js'

const props = defineProps({
  project: { type: Object, default: null },
  projectId: { type: [Number, String], default: null },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  mode: { type: String, default: 'preview' },
  editorPath: { type: String, default: '' },
  loadingText: { type: String, default: '加载演示…' },
  embedded: { type: Boolean, default: false },
})

const router = useRouter()

const index = ref(0)
const visibleIndex = ref(0)
const phoneFrame = ref(true)
const viewportId = ref('mobile-375')
const scrollEffect = ref('page')
const userZoom = ref(100)
const projectSettings = ref(null)

const flowScrollRef = ref(null)
const horizontalScrollRef = ref(null)
const flowWheelLock = ref(false)

const scrollOptions = computed(() => SCROLL_EFFECTS.map((s) => ({ value: s.id, label: s.label })))
const mobileViewports = VIEWPORT_PRESETS.filter((v) => v.device === 'mobile')
const webViewports = VIEWPORT_PRESETS.filter((v) => v.device === 'web')
const viewportOptions = computed(() => [
  ...mobileViewports.map((v) => ({ value: v.id, label: v.label })),
  ...webViewports.map((v) => ({ value: v.id, label: v.label })),
])

const MIN_ZOOM = 25
const MAX_ZOOM = 200
const ZOOM_STEP = 5

const slides = computed(() => props.project?.slides || [])
const current = computed(() => slides.value[index.value] || {})
const viewport = computed(() => getViewportPreset(viewportId.value))
const bgmConfig = computed(() => projectSettings.value?.bgm || { enabled: false })
const bgmPlayerActive = computed(
  () => !props.embedded && bgmConfig.value.enabled && !!bgmConfig.value.url
)

const activeSlide = computed(() => {
  if (scrollEffect.value === 'page') return current.value
  return slides.value[visibleIndex.value] || {}
})

const activeIndex = computed(() => (scrollEffect.value === 'page' ? index.value : visibleIndex.value))

const playback = usePresentationPlayback({
  settingsRef: projectSettings,
  onNeedUserGesture: () => {},
})

const {
  chatBlocking,
  slideChatScript,
  syncChatGate,
  onChatComplete: clearChatBlock,
  unlockBgmFromGesture,
  toggleBgmMute,
  bgmMuted,
  bgmPlaying,
  bgmUnlocked,
  tryPlayBgm,
} = playback

const bgmHintVisible = computed(
  () => bgmConfig.value.enabled && bgmConfig.value.url && !bgmUnlocked.value && !bgmMuted.value
)

const scrollHintVisible = computed(() => {
  if (props.embedded) return false
  if (!projectSettings.value?.showScrollHint) return false
  if (scrollEffect.value !== 'vertical' && scrollEffect.value !== 'snap') return false
  return visibleIndex.value === 0 && slides.value.length > 1
})

const scrollModeInfo = computed(() => {
  const m = SCROLL_EFFECTS.find((s) => s.id === scrollEffect.value)
  const hints = {
    page: '空格 / 方向键切换；对话页支持点击或自动逐句播放',
    vertical: '滚轮下滑整屏切换；对话页需先点完聊天',
    horizontal: '左右滑动切换页面',
    snap: '滚动后吸附整屏',
  }
  const exitHint =
    props.mode === 'preview' && props.editorPath && !props.embedded ? ' · Esc 退出预览' : ''
  return { label: m?.label || '翻页模式', hint: (hints[scrollEffect.value] || m?.desc || '') + exitHint }
})

const currentElements = computed(() => resolvePreviewElements(props.projectId, current.value))

const currentBackground = computed(() => backgroundForSlide(current.value))

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
  const maxW = props.embedded ? 360 : phoneFrame.value ? 420 : 900
  const maxH = props.embedded ? 640 : phoneFrame.value ? 720 : 600
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

const footerStatus = computed(() => {
  const total = slides.value.length
  const chatHint = chatBlocking.value ? ' · 对话进行中' : ''
  if (scrollEffect.value === 'page') return `翻页 · ${index.value + 1}/${total}${chatHint}`
  if (scrollEffect.value === 'vertical' || scrollEffect.value === 'snap') {
    return `${scrollEffect.value === 'vertical' ? '纵向' : '吸附'} · ${visibleIndex.value + 1}/${total}${chatHint}`
  }
  if (scrollEffect.value === 'horizontal') return `横向 · ${visibleIndex.value + 1}/${total}${chatHint}`
  return `${visibleIndex.value + 1}/${total}${chatHint}`
})

const canGoPrev = computed(() => {
  if (chatBlocking.value) return false
  if (scrollEffect.value === 'page') return index.value > 0
  return visibleIndex.value > 0
})

const canGoNext = computed(() => {
  if (chatBlocking.value) return false
  const total = slides.value.length
  if (scrollEffect.value === 'page') return index.value < total - 1
  return visibleIndex.value < total - 1
})

function elementsForSlide(slide) {
  return resolvePreviewElements(props.projectId, slide)
}

function backgroundForSlide(slide) {
  if (!slide?.id) return slide?.canvas_background || DEFAULT_CANVAS_BG
  const fromApi = slide.canvas_background
  if (fromApi) return fromApi
  return resolveSlideBackground(props.projectId, slide.id, projectSettings.value, slide)
}

function applySettingsFromProject(p) {
  if (!p) return
  projectSettings.value = mergeProjectSettings(props.projectId, p.settings)
  if (projectSettings.value.viewportId) viewportId.value = projectSettings.value.viewportId
  if (projectSettings.value.scrollEffect) scrollEffect.value = projectSettings.value.scrollEffect
  syncChatGate(activeSlide.value, activeIndex.value)
  if (bgmConfig.value.enabled) tryPlayBgm()
}

watch(
  () => props.project,
  (p) => {
    if (p) applySettingsFromProject(p)
  },
  { immediate: true }
)

watch([activeSlide, activeIndex], ([slide, idx]) => {
  syncChatGate(slide, idx)
})

function onRootClick() {
  unlockBgmFromGesture()
}

function onChatComplete() {
  clearChatBlock()
  if (scrollEffect.value === 'page') {
    if (index.value < slides.value.length - 1) index.value += 1
  } else {
    goNext()
  }
}

function onScrollModeChange() {
  if (props.projectId) {
    const merged = { ...projectSettings.value, scrollEffect: scrollEffect.value }
    projectSettings.value = merged
    localStorage.setItem(`ai_h5_project_settings_${props.projectId}`, JSON.stringify(merged))
  }
  index.value = 0
  visibleIndex.value = 0
  nextTick(() => scrollToVisible(0, 'auto'))
}

function scrollToVisible(i, behavior = 'smooth') {
  if (chatBlocking.value) return
  if (scrollEffect.value === 'horizontal') {
    const el = horizontalScrollRef.value
    if (el) el.scrollTo({ left: i * el.clientWidth, behavior })
  } else if (scrollEffect.value === 'vertical' || scrollEffect.value === 'snap') {
    const el = flowScrollRef.value
    if (!el) return
    el.scrollTo({ top: i * el.clientHeight, behavior })
  }
}

function trackFlowScroll(e) {
  if (chatBlocking.value) return
  const el = e.target
  if (!el.clientHeight) return
  visibleIndex.value = Math.min(
    slides.value.length - 1,
    Math.max(0, Math.round(el.scrollTop / el.clientHeight))
  )
}

function onFlowWheel(e) {
  if (scrollEffect.value !== 'vertical' && scrollEffect.value !== 'snap') return
  if (chatBlocking.value) {
    e.preventDefault()
    return
  }
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
  if (chatBlocking.value) return
  const el = e.target
  if (!el.clientWidth) return
  visibleIndex.value = Math.min(slides.value.length - 1, Math.max(0, Math.round(el.scrollLeft / el.clientWidth)))
}

function onHorizontalWheel(e) {
  if (chatBlocking.value) return
  const el = horizontalScrollRef.value
  if (!el) return
  el.scrollLeft += e.deltaY + e.deltaX
}

watch(viewportId, () => {
  resetUserZoom()
  if (props.projectId && projectSettings.value) {
    const merged = { ...projectSettings.value, viewportId: viewportId.value }
    projectSettings.value = merged
    localStorage.setItem(`ai_h5_project_settings_${props.projectId}`, JSON.stringify(merged))
  }
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

function goPrev() {
  if (chatBlocking.value) return
  if (scrollEffect.value === 'page') {
    if (index.value > 0) index.value -= 1
    return
  }
  scrollToVisible(Math.max(0, visibleIndex.value - 1))
}

function goNext() {
  if (chatBlocking.value) return
  if (scrollEffect.value === 'page') {
    if (index.value < slides.value.length - 1) index.value += 1
    return
  }
  scrollToVisible(Math.min(slides.value.length - 1, visibleIndex.value + 1))
}

function exitPreview() {
  if (!props.editorPath || props.embedded) return
  router.push(props.editorPath)
}

function onKey(e) {
  if (e.key === 'Escape' && props.editorPath && !props.embedded) {
    e.preventDefault()
    exitPreview()
    return
  }
  if (chatBlocking.value) return
  if (scrollEffect.value === 'page') {
    if (e.key === 'ArrowRight' || e.key === ' ') {
      e.preventDefault()
      goNext()
    }
    if (e.key === 'ArrowLeft') goPrev()
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
.preview-toolbar-btn-exit {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border-color: rgba(255, 120, 120, 0.45);
}
.preview-toolbar-btn-exit:hover {
  background: rgba(80, 30, 30, 0.85);
}
.preview-footer-exit {
  font-size: 13px;
  font-weight: 500;
  color: #fff;
  background: rgba(180, 40, 40, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 8px;
  padding: 6px 14px;
}
.preview-footer-exit:hover {
  background: rgba(200, 50, 50, 0.95);
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
