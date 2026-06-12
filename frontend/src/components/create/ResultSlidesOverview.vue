<template>

  <div

    ref="scrollRootRef"

    class="flex-1 min-w-0 min-h-0 overflow-y-auto bg-surface-container-low"

    @click="onContainerPointerDown"

  >

    <div

      class="mx-auto w-full px-3 sm:px-4 py-3 flex flex-col"

      :class="isWideViewport ? 'max-w-[1100px]' : 'max-w-[960px]'"

      :style="slidesContainerStyle"

    >

      <template v-for="(slide, index) in slides" :key="slide.id">

        <div

          v-if="shouldMountSlide(index)"

          v-show="isSlideShown(index)"

          class="relative"

          :class="[

            revealActive && !isSlideShown(index) ? 'opacity-0 max-h-0 overflow-hidden' : '',

            revealActive && isSlideShown(index) ? 'animate-[fadeIn_0.3s_ease]' : '',

          ]"

        >

          <section

            :id="`result-slide-${slide.id}`"

            :ref="(el) => setSlideRef(slide.id, el)"

            class="rounded-xl border-2 overflow-hidden transition-all duration-300 cursor-pointer"

            :style="{ background: slideCanvasBackground(slide) }"

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

              :preview-elements="previewElementsForSlide(slide)"

              :elements="elementsForSlide(slide)"

              :selected-ids="currentId === slide.id ? selectedIds : []"

              :canvas-background="slideCanvasBackground(slide)"

              :theme-id="themeId"

              :slide="slide"

              :slide-index="index"

              :slide-total="slides.length"

              :reveal-stagger="false"

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



          <SlideInsertAffordance

            v-if="showInsertUi"

            v-show="activeInsertAfterId === slide.id"

            placement="below-card"

            :style="insertBelowStyle"

            @add-blank="$emit('add-slide-after', slide.id)"

            @open-generate="$emit('open-generate-card', slide.id)"

          />



          <div

            v-if="index < slides.length - 1 && showInsertUi"

            class="absolute left-0 right-0 z-20"

            :style="gapHitAreaStyle"

            @mouseenter="onGapEnter(slide.id)"

            @mouseleave="onGapLeave(slide.id)"

          >

            <SlideInsertAffordance

              v-show="hoverInsertAfterId === slide.id && activeInsertAfterId !== slide.id"

              placement="gap"

              @add-blank="$emit('add-slide-after', slide.id)"

              @open-generate="$emit('open-generate-card', slide.id)"

            />

          </div>

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

import { computed, onMounted, onUnmounted, ref } from 'vue'

import ResultSlideCardCanvas from './ResultSlideCardCanvas.vue'

import SlideInsertAffordance from './SlideInsertAffordance.vue'

import EmptyState from '../EmptyState.vue'

import { DEFAULT_WEB_VIEWPORT_ID, isWideWebViewport } from '../../constants/editorPresets.js'

import { resolveSlideCanvasBackground } from '../../utils/slideBackground.js'

import { ensureSlideCompiled } from '../../utils/compileStructuredSlide.js'



const OUTER_PADDING_X = 32

const MAX_SCALE = 0.72

const MIN_SCALE = 0.24

const CARD_HEIGHT_FACTOR = 2 / 3

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

])



const scrollRootRef = ref(null)

const slideRefs = ref({})

const cardRefs = ref({})

const containerWidth = ref(880)

const activeInsertAfterId = ref(null)

const hoverInsertAfterId = ref(null)

let resizeObserver = null



const showInsertUi = computed(() => !props.interactionLocked && !props.revealActive)



function setSlideRef(id, el) {

  if (el) slideRefs.value[id] = el

  else delete slideRefs.value[id]

}



function setCardRef(id, el) {

  if (el) cardRefs.value[id] = el

  else delete cardRefs.value[id]

}



const cardScale = computed(() => {

  const maxW = Math.max(240, containerWidth.value - OUTER_PADDING_X)

  const scaleByWidth = maxW / props.displayViewport.width

  if (isWideViewport.value) {

    return Math.max(MIN_SCALE, scaleByWidth)

  }

  const base = Math.max(MIN_SCALE, Math.min(scaleByWidth, MAX_SCALE))

  return base * CARD_HEIGHT_FACTOR

})



const isWideViewport = computed(() => isWideWebViewport(props.viewportId))

const cardDisplayHeight = computed(() =>

  Math.round(props.displayViewport.height * cardScale.value)

)



const gapPx = computed(() => Math.max(16, Math.round(cardDisplayHeight.value * CARD_GAP_RATIO)))



const slidesContainerStyle = computed(() => ({

  gap: `${gapPx.value}px`,

}))



const insertBelowStyle = computed(() => ({

  top: `calc(100% + ${gapPx.value / 2}px)`,

}))



const gapHitAreaStyle = computed(() => ({

  top: '100%',

  height: `${gapPx.value}px`,

  marginTop: `-${Math.floor(gapPx.value / 2)}px`,

}))



function isSlideShown(index) {

  if (!props.revealActive) return true

  if (props.visibleSlideCount < 0) return true

  if (props.visibleSlideCount === 0) return index === 0

  return index < props.visibleSlideCount

}



function shouldMountSlide(index) {

  if (!props.revealActive) return true

  if (props.visibleSlideCount < 0) return true

  if (props.visibleSlideCount === 0) return index === 0

  return index < props.visibleSlideCount + 1

}



function allElementsForSlide(slide) {

  if (slide.id === props.currentId && props.elements?.length) {

    return props.elements

  }

  return ensureSlideCompiled(slide, props.viewportId, props.themeId)

}



function filterVisibleElements(slide, allEls) {

  if (!props.revealActive) return allEls

  const ids = new Set(props.visibleElementIdsBySlide[slide.id] || [])

  if (!ids.size) return []

  return allEls.filter((el) => ids.has(el.id))

}



function previewElementsForSlide(slide) {

  return filterVisibleElements(slide, allElementsForSlide(slide))

}



function elementsForSlide(slide) {

  if (slide.id !== props.currentId) return []

  return filterVisibleElements(slide, props.elements || [])

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

  return !!target.closest('[data-element-id], [data-editor-chrome], [data-slide-insert], [data-slide-id]')

}



function onContainerPointerDown(e) {

  if (props.interactionLocked) return

  if (isChromeTarget(e.target)) return

  activeInsertAfterId.value = null

  if (props.currentId != null) {

    emit('deselect')

  }

}



function updateContainerSize() {

  if (scrollRootRef.value) {

    containerWidth.value = scrollRootRef.value.clientWidth

  }

}



function resolveElementEl(slideId, elementId) {

  const section = slideRefs.value[slideId]

  if (!section) return null

  return section.querySelector(`[data-element-id="${elementId}"]`)

}



onMounted(() => {

  updateContainerSize()

  if (scrollRootRef.value) {

    resizeObserver = new ResizeObserver(() => updateContainerSize())

    resizeObserver.observe(scrollRootRef.value)

  }

})



onUnmounted(() => {

  resizeObserver?.disconnect()

})



defineExpose({ scrollToSlide, resolveElementEl, scrollRootRef })

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


