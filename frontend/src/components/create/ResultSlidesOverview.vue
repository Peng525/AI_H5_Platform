<template>
  <div
    ref="scrollRootRef"
    class="flex-1 min-w-0 min-h-0 overflow-y-auto bg-surface-container-low"
    @click="onContainerPointerDown"
  >
    <div
      ref="slidesContainerRef"
      class="mx-auto w-full px-3 sm:px-4 py-3 flex flex-col"
      :class="isWideViewport ? 'max-w-[1400px]' : 'max-w-[1200px]'"
      :style="slidesContainerStyle"
    >
      <template v-for="(slide, index) in slides" :key="slide.id">
        <div v-if="shouldMountSlide(index)" class="relative shrink-0">
          <section
            :id="`result-slide-${slide.id}`"
            :ref="(el) => setSlideRef(slide.id, el)"
            class="mx-auto rounded-xl border-2 overflow-hidden transition-colors duration-300 cursor-pointer"
            :style="{
              background: slideCanvasBackground(slide),
              width: `${cardDisplayWidth}px`,
              minHeight: `${cardDisplayHeight}px`,
            }"
            :class="[
              interactionLocked ? 'pointer-events-none' : '',
              slide.id === currentId
                ? 'border-primary'
                : 'border-outline-variant/60',
            ]"
            :data-slide-id="slide.id"
            @click.stop="onCardClick(slide)"
          >
            <ResultSlideCardCanvas
              :ref="(el) => setCardRef(slide.id, el)"
              fill-card
              :active="!interactionLocked && currentId === slide.id"
              :scale="cardScale"
              :viewport="displayViewport"
              :preview-elements="previewElementsForSlide(slide, index)"
              :elements="elementsForSlide(slide)"
              :selected-ids="currentId === slide.id ? selectedIds : []"
              :canvas-background="slideCanvasBackground(slide)"
              :theme-id="themeId"
              :slide="slide"
              :slide-index="index"
              :slide-total="slides.length"
              :reveal-stagger="revealActive"
              @select="$emit('select-element', $event)"
              @deselect="$emit('deselect')"
              @update-element="(id, patch) => $emit('update-element', id, patch)"
              @marquee-select="$emit('marquee-select', $event)"
              @batch-start="$emit('batch-start', $event)"
              @batch-end="$emit('batch-end')"
              @move-delta="$emit('move-delta', $event)"
              @edit-wordcloud="$emit('edit-wordcloud', $event)"
              @edit-chart-stack="$emit('edit-chart-stack', $event)"
              @text-edit-start="$emit('text-edit-start', $event)"
              @text-edit-end="$emit('text-edit-end', $event)"
            />
          </section>
        </div>

        <div
          v-if="index < slides.length - 1"
          :ref="(el) => setGapRef(slide.id, el)"
          class="w-full shrink-0 relative overflow-visible"
          :class="isGeneratePanelOpen(slide.id) ? 'z-10' : ''"
          :style="gapSpacerStyle(slide.id)"
          @mouseenter="onGapEnter(slide.id)"
          @mouseleave="onGapLeave(slide.id)"
        >
          <template v-if="showInsertUi && isInsertSlotVisible(index, slide)">
            <div
              v-if="!isGeneratePanelOpen(slide.id)"
              class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none overflow-hidden"
            >
              <SlideInsertAffordance
                v-show="shouldShowInsertButtons(slide.id)"
                class="pointer-events-auto"
                @add-blank="$emit('add-slide-after', slide.id)"
                @open-generate="$emit('open-generate-card', slide.id)"
              />
            </div>
            <div
              v-if="generatePanelSlideId === slide.id"
              class="mx-auto rounded-2xl bg-gradient-to-b from-[#0f1a2e] via-[#1e3a6b] to-[#3a8fd4] px-5 sm:px-6 py-5 overflow-visible pointer-events-auto"
              :style="panelShellStyle"
            >
              <GenerateCardPanel
                :loading="generateLoading"
                :quota-remaining="quotaRemaining"
                :quota-total="quotaTotal"
                @close="$emit('close-generate-panel')"
                @generate="$emit('generate-card', $event)"
              />
            </div>
          </template>
        </div>
      </template>

      <EmptyState
        v-if="!slides.length && !revealActive"
        class="py-16"
        icon="slideshow"
        title="暂无幻灯片"
        description="项目已加载，但未包含任何页面内容。"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import ResultSlideCardCanvas from './ResultSlideCardCanvas.vue'
import SlideInsertAffordance from './SlideInsertAffordance.vue'
import GenerateCardPanel from './GenerateCardPanel.vue'
import EmptyState from '../EmptyState.vue'
import { DEFAULT_WEB_VIEWPORT_ID, isWideWebViewport } from '../../constants/editorPresets.js'
import { resolveSlideCanvasBackground } from '../../utils/slideBackground.js'
import { clampElementsToViewport, ensureSlideCompiled } from '../../utils/compileStructuredSlide.js'

const OUTER_PADDING_X = 16
const MAX_SCALE = 1.0
const MIN_SCALE = 0.24
const CARD_HEIGHT_FACTOR = 0.72
const CARD_GAP_RATIO = 0.2

const props = defineProps({
  slides: { type: Array, default: () => [] },
  currentId: { type: Number, default: null },
  projectId: { type: [Number, String], default: null },
  projectSettings: { type: Object, default: null },
  displayViewport: { type: Object, required: true },
  viewportId: { type: String, default: DEFAULT_WEB_VIEWPORT_ID },
  themeId: { type: String, default: 'zjy-minimal' },
  elements: { type: Array, default: () => [] },
  selectedIds: { type: Array, default: () => [] },
  canvasBackground: { type: String, default: '' },
  revealActive: { type: Boolean, default: false },
  interactionLocked: { type: Boolean, default: false },
  visibleSlideCount: { type: Number, default: -1 },
  visibleElementIdsBySlide: { type: Object, default: () => ({}) },
  generatePanelSlideId: { type: Number, default: null },
  generateLoading: { type: Boolean, default: false },
  quotaRemaining: { type: Number, default: null },
  quotaTotal: { type: Number, default: null },
})

const emit = defineEmits([
  'select',
  'deselect-slide',
  'select-element',
  'deselect',
  'marquee-select',
  'update-element',
  'batch-start',
  'batch-end',
  'move-delta',
  'edit-wordcloud',
  'edit-chart-stack',
  'text-edit-start',
  'text-edit-end',
  'add-slide-after',
  'open-generate-card',
  'close-generate-panel',
  'generate-card',
])

const scrollRootRef = ref(null)
const slidesContainerRef = ref(null)
const slideRefs = ref({})
const cardRefs = ref({})
const gapRefs = ref({})
const containerWidth = ref(880)
const activeInsertAfterId = ref(null)
const hoverInsertAfterId = ref(null)
let resizeObserver = null
let resizeRafId = null

const showInsertUi = computed(() => !props.interactionLocked && !props.revealActive)

function setSlideRef(id, el) {
  if (el) slideRefs.value[id] = el
  else delete slideRefs.value[id]
}

function setCardRef(id, el) {
  if (el) cardRefs.value[id] = el
  else delete cardRefs.value[id]
}

function setGapRef(id, el) {
  if (el) gapRefs.value[id] = el
  else delete gapRefs.value[id]
}

const cardScale = computed(() => {
  const maxW = Math.max(240, containerWidth.value - OUTER_PADDING_X)
  const scaleByWidth = maxW / props.displayViewport.width
  if (isWideViewport.value) {
    return Math.max(MIN_SCALE, Math.min(scaleByWidth, MAX_SCALE))
  }
  const base = Math.max(MIN_SCALE, Math.min(scaleByWidth, MAX_SCALE))
  return base * CARD_HEIGHT_FACTOR
})

const isWideViewport = computed(() => isWideWebViewport(props.viewportId))
const cardDisplayHeight = computed(() =>
  Math.round(props.displayViewport.height * cardScale.value)
)
const cardDisplayWidth = computed(() =>
  Math.round(props.displayViewport.width * cardScale.value)
)
const panelDisplayWidth = computed(() => cardDisplayWidth.value)
const panelDisplayHeight = 430

const gapPx = computed(() => Math.max(16, Math.round(cardDisplayHeight.value * CARD_GAP_RATIO)))

const slidesContainerStyle = computed(() => ({
  gap: '0px',
}))

function isGeneratePanelOpen(slideId) {
  return props.generatePanelSlideId === slideId
}

function shouldShowInsertButtons(slideId) {
  if (isGeneratePanelOpen(slideId)) return true
  return hoverInsertAfterId.value === slideId || activeInsertAfterId.value === slideId
}

function gapSpacerStyle(slideId) {
  if (isGeneratePanelOpen(slideId)) {
    return {
      minHeight: `${gapPx.value}px`,
      height: 'auto',
      paddingTop: `${gapPx.value}px`,
      paddingBottom: `${gapPx.value}px`,
    }
  }
  return {
    height: `${gapPx.value}px`,
  }
}

const panelShellStyle = computed(() => ({
  width: `${panelDisplayWidth.value}px`,
  minHeight: `${panelDisplayHeight}px`,
}))

function isInsertSlotVisible(index, slide) {
  if (isGeneratePanelOpen(slide.id)) return true
  if (index < props.slides.length - 1) return true
  return activeInsertAfterId.value === slide.id
}

function isSlideShown(index) {
  if (!props.revealActive) return true
  if (props.visibleSlideCount < 0) return true
  if (props.visibleSlideCount === 0) return index === 0
  return index < props.visibleSlideCount
}

function shouldMountSlide(_index) {
  if (!props.revealActive) return true
  return isSlideShown(_index)
}

function allElementsForSlide(slide) {
  if (slide.id === props.currentId && props.elements?.length) {
    return clampElementsToViewport(props.elements, props.viewportId)
  }
  return ensureSlideCompiled(slide, props.viewportId, props.themeId)
}

function filterVisibleElements(slide, allEls) {
  if (!props.revealActive) return allEls
  const ids = new Set(props.visibleElementIdsBySlide[slide.id] || [])
  if (!ids.size) return []
  return allEls.filter((el) => ids.has(el.id))
}

function previewElementsForSlide(slide, index) {
  if (props.revealActive && !isSlideShown(index)) return []
  return filterVisibleElements(slide, allElementsForSlide(slide))
}

function elementsForSlide(slide) {
  if (slide.id !== props.currentId) return []
  return filterVisibleElements(slide, clampElementsToViewport(props.elements || [], props.viewportId))
}

function slideCanvasBackground(slide) {
  return resolveSlideCanvasBackground(props.projectId, slide, props.projectSettings)
}

function scrollToSlide(id, smooth = true) {
  const el = slideRefs.value[id]
  if (el?.scrollIntoView) {
    el.scrollIntoView({ behavior: smooth ? 'smooth' : 'auto', block: 'nearest' })
  }
}

async function scrollToGapAfter(id, smooth = true) {
  await nextTick()
  const el = gapRefs.value[id]
  if (el?.scrollIntoView) {
    el.scrollIntoView({ behavior: smooth ? 'smooth' : 'auto', block: 'nearest' })
  }
}

function onCardClick(slide) {
  if (props.interactionLocked) return
  activeInsertAfterId.value = slide.id
  if (slide.id !== props.currentId) {
    emit('select', slide)
  }
}

function onGapEnter(slideId) {
  hoverInsertAfterId.value = slideId
}

function onGapLeave(slideId) {
  if (hoverInsertAfterId.value === slideId) {
    hoverInsertAfterId.value = null
  }
}

function isChromeTarget(target) {
  if (!(target instanceof Element)) return false
  return !!target.closest('[data-element-id], [data-editor-chrome], [data-slide-insert], [data-slide-id], [data-generate-card-panel]')
}

function onContainerPointerDown(e) {
  if (props.interactionLocked) return
  if (isChromeTarget(e.target)) return
  if (props.generatePanelSlideId != null) {
    emit('close-generate-panel')
  }
  activeInsertAfterId.value = null
  if (props.currentId != null) {
    emit('deselect')
  }
}

function updateContainerSize() {
  if (resizeRafId != null) cancelAnimationFrame(resizeRafId)
  resizeRafId = requestAnimationFrame(() => {
    resizeRafId = null
    const target = slidesContainerRef.value || scrollRootRef.value
    if (target) {
      containerWidth.value = target.clientWidth
    }
  })
}

function resolveElementEl(slideId, elementId) {
  const card = cardRefs.value[slideId]
  const fromCard = card?.resolveElementEl?.(elementId)
  if (fromCard) return fromCard
  const section = slideRefs.value[slideId]
  if (!section) return null
  return section.querySelector(`[data-editable-canvas] [data-element-id="${elementId}"]`)
}

onMounted(() => {
  updateContainerSize()
  if (scrollRootRef.value) {
    resizeObserver = new ResizeObserver(() => updateContainerSize())
    resizeObserver.observe(scrollRootRef.value)
    if (slidesContainerRef.value) resizeObserver.observe(slidesContainerRef.value)
  }
})

onUnmounted(() => {
  if (resizeRafId != null) cancelAnimationFrame(resizeRafId)
  resizeObserver?.disconnect()
})

defineExpose({ scrollToSlide, scrollToGapAfter, resolveElementEl, scrollRootRef })
</script>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
