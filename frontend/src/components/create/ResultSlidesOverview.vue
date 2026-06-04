<template>
  <div ref="scrollRootRef" class="flex-1 min-w-0 min-h-0 overflow-y-auto bg-surface-container-low">
    <div class="mx-auto max-w-[960px] px-3 sm:px-4 py-3 space-y-3">
      <section
        v-for="(slide, index) in slides"
        :key="slide.id"
        :id="`result-slide-${slide.id}`"
        :ref="(el) => setSlideRef(slide.id, el)"
        class="rounded-xl border bg-white overflow-hidden transition-all duration-200 ease-out cursor-pointer"
        :class="slideSectionClass(slide.id)"
        :data-slide-id="slide.id"
        @click="onCardClick(slide)"
      >
        <div class="px-3 py-1.5 border-b border-outline-variant/60 bg-surface-container-low/50 flex items-center gap-2">
          <span class="text-xs font-semibold text-on-surface-variant shrink-0">第 {{ index + 1 }} 页</span>
          <span v-if="slide.layout" class="text-[10px] text-on-surface-variant/70 truncate">{{ slide.layout }}</span>
          <span
            v-if="currentId === slide.id"
            class="ml-auto text-[10px] text-primary font-medium shrink-0"
          >
            当前编辑
          </span>
        </div>

        <div
          class="flex justify-center bg-surface-container-low/25"
          :style="{ padding: `${SECTION_PAD}px` }"
          @click.stop="onCardClick(slide)"
        >
          <ResultSlideCardCanvas
            :active="currentId === slide.id"
            :scale="cardScale"
            :viewport="displayViewport"
            :preview-elements="previewElementsForSlide(slide)"
            :elements="currentId === slide.id ? elements : []"
            :selected-ids="currentId === slide.id ? selectedIds : []"
            :canvas-background="slideCanvasBackground(slide)"
            :theme-id="themeId"
            :slide="slide"
            :slide-index="index"
            :slide-total="slides.length"
            @select="$emit('select-element', $event)"
            @deselect="$emit('deselect')"
            @update-element="$emit('update-element', $event)"
            @marquee-select="$emit('marquee-select', $event)"
            @batch-start="$emit('batch-start', $event)"
            @batch-end="$emit('batch-end')"
            @move-delta="$emit('move-delta', $event)"
            @edit-wordcloud="$emit('edit-wordcloud', $event)"
            @edit-chart-stack="$emit('edit-chart-stack', $event)"
          />
        </div>
      </section>

      <EmptyState
        v-if="!slides.length"
        class="py-16"
        icon="slideshow"
        title="暂无幻灯片"
        description="项目已加载，但未包含任何页面内容。"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import ResultSlideCardCanvas from './ResultSlideCardCanvas.vue'
import EmptyState from '../EmptyState.vue'
import { resolveSlideCanvasBackground } from '../../utils/slideBackground.js'
import { compileSlideIfNeeded } from '../../utils/compileStructuredSlide.js'

const TARGET_VISIBLE = 2.5
const SECTION_HEADER = 32
const SECTION_PAD = 12
const GAP = 12
const OUTER_PADDING_X = 32
const MAX_SCALE = 0.48
const MIN_SCALE = 0.24

const props = defineProps({
  slides: { type: Array, default: () => [] },
  currentId: { type: Number, default: null },
  projectId: { type: [Number, String], default: null },
  projectSettings: { type: Object, default: null },
  displayViewport: { type: Object, required: true },
  viewportId: { type: String, default: 'web-1280' },
  themeId: { type: String, default: 'zjy-minimal' },
  elements: { type: Array, default: () => [] },
  selectedIds: { type: Array, default: () => [] },
  canvasBackground: { type: String, default: '' },
})

const emit = defineEmits([
  'select',
  'select-element',
  'deselect',
  'marquee-select',
  'update-element',
  'batch-start',
  'batch-end',
  'move-delta',
  'edit-wordcloud',
  'edit-chart-stack',
])

const scrollRootRef = ref(null)
const slideRefs = ref({})
const containerWidth = ref(880)
const containerHeight = ref(640)
const scrollSyncLock = ref(false)
let resizeObserver = null
let intersectionObserver = null

function setSlideRef(id, el) {
  if (el) slideRefs.value[id] = el
  else delete slideRefs.value[id]
}

const cardScale = computed(() => {
  const maxW = Math.max(240, containerWidth.value - OUTER_PADDING_X)
  const scaleByWidth = maxW / props.displayViewport.width

  const gaps = GAP * (TARGET_VISIBLE - 1)
  const cardContentH =
    (Math.max(320, containerHeight.value) - gaps) / TARGET_VISIBLE - SECTION_HEADER - SECTION_PAD * 2
  const scaleByHeight = cardContentH / props.displayViewport.height

  const scale = Math.min(scaleByWidth, scaleByHeight, MAX_SCALE)
  return Math.max(MIN_SCALE, scale)
})

function previewElementsForSlide(slide) {
  if (slide.id === props.currentId && props.elements?.length) {
    return props.elements
  }
  if (slide.canvas_elements?.length) return slide.canvas_elements
  const compiled = compileSlideIfNeeded(slide, props.viewportId, props.themeId)
  return compiled.length ? compiled : []
}

function slideCanvasBackground(slide) {
  if (slide.id === props.currentId && props.canvasBackground) {
    return props.canvasBackground
  }
  return resolveSlideCanvasBackground(props.projectId, slide, props.projectSettings)
}

function slideSectionClass(slideId) {
  if (props.currentId === slideId) {
    return 'border-primary/50 shadow-md ring-1 ring-primary/20'
  }
  return 'border-outline-variant/60 hover:border-outline-variant hover:shadow-sm'
}

function onCardClick(slide) {
  emit('select', slide)
}

function scrollToSlide(id) {
  const el = slideRefs.value[id]
  if (el?.scrollIntoView) {
    scrollSyncLock.value = true
    el.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    window.setTimeout(() => {
      scrollSyncLock.value = false
    }, 400)
  }
}

function updateContainerSize() {
  if (scrollRootRef.value) {
    containerWidth.value = scrollRootRef.value.clientWidth
    containerHeight.value = scrollRootRef.value.clientHeight
  }
}

function setupIntersectionObserver() {
  intersectionObserver?.disconnect()
  if (!scrollRootRef.value || !props.slides.length) return

  const ratios = new Map()
  intersectionObserver = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        const id = Number(entry.target.dataset.slideId)
        if (id) ratios.set(id, entry.intersectionRatio)
      }
      if (scrollSyncLock.value) return
      let bestId = null
      let bestRatio = 0
      for (const [id, ratio] of ratios) {
        if (ratio > bestRatio) {
          bestRatio = ratio
          bestId = id
        }
      }
      if (bestId != null && bestRatio > 0.35 && bestId !== props.currentId) {
        const slide = props.slides.find((s) => s.id === bestId)
        if (slide) emit('select', slide)
      }
    },
    { root: scrollRootRef.value, threshold: [0, 0.25, 0.5, 0.75, 1] }
  )

  for (const slide of props.slides) {
    const el = slideRefs.value[slide.id]
    if (el) intersectionObserver.observe(el)
  }
}

watch(
  () => props.currentId,
  (id) => {
    if (id) scrollToSlide(id)
  }
)

watch(
  () => props.slides.map((s) => s.id).join(','),
  async () => {
    await nextTick()
    setupIntersectionObserver()
  }
)

onMounted(() => {
  updateContainerSize()
  if (scrollRootRef.value) {
    resizeObserver = new ResizeObserver(() => updateContainerSize())
    resizeObserver.observe(scrollRootRef.value)
  }
  nextTick(() => setupIntersectionObserver())
})

onUnmounted(() => {
  resizeObserver?.disconnect()
  intersectionObserver?.disconnect()
})

defineExpose({ scrollToSlide })
</script>
