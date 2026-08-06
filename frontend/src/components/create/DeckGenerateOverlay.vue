<template>

  <Teleport to="body">

    <div

      v-if="open"

      class="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-surface-container-low/95 backdrop-blur-sm px-6"

      role="dialog"

      aria-modal="true"

      aria-labelledby="deck-generate-overlay-title"

    >

      <div class="w-full max-w-md text-center space-y-6">

        <div class="mx-auto w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">

          <span class="material-symbols-outlined text-primary text-[36px] animate-pulse">auto_awesome</span>

        </div>

        <div>

          <h2 id="deck-generate-overlay-title" class="text-lg font-semibold text-on-surface">

            {{ title }}

          </h2>

          <p class="text-sm text-on-surface-variant mt-2">

            {{ effectiveSubtitle }}

          </p>

        </div>

        <div v-if="showProgress" class="space-y-2">

          <div class="h-2 rounded-full bg-outline-variant/30 overflow-hidden">

            <div

              class="h-full bg-primary transition-all duration-500 ease-out"

              :style="{ width: `${clampedProgress}%` }"

            />

          </div>

          <p class="text-xs text-on-surface-variant tabular-nums">{{ clampedProgress }}%</p>

        </div>

        <div class="rounded-xl border border-outline-variant bg-white px-5 py-4 space-y-2 text-sm">

          <div class="flex justify-between tabular-nums">

            <span class="text-on-surface-variant">{{ etaLabel }}</span>

            <span class="font-medium">{{ etaValue }}</span>

          </div>

          <div class="flex justify-between tabular-nums">

            <span class="text-on-surface-variant">已等待</span>

            <span class="font-medium text-primary">{{ elapsedLabel }}</span>

          </div>

        </div>

        <p v-if="etaHint" class="text-xs text-on-surface-variant/90">{{ etaHint }}</p>

        <p class="text-xs text-on-surface-variant">{{ footerHint }}</p>

      </div>

    </div>

  </Teleport>

</template>



<script setup>

import { computed, onUnmounted, ref, watch } from 'vue'

import {

  computeStageAwareRemainingSeconds,

  estimatePremiumDeckRange,

  formatDurationLabel,

  formatPremiumDeckRangeLabel,

  shouldShowPremiumRemaining,

  smoothEtaSeconds,

} from '../../utils/deckGenerateEstimate.js'



const props = defineProps({

  open: { type: Boolean, default: false },

  estimatedSeconds: { type: Number, default: 48 },

  title: { type: String, default: '加载中…' },

  subtitle: {

    type: String,

    default: 'AI 正在根据您的提示词创建演示，请稍候…',

  },

  stageLabel: { type: String, default: '' },

  progress: { type: Number, default: null },

  footerHint: { type: String, default: '生成完成后将开始绘制页面' },

  isPremium: { type: Boolean, default: false },

  stage: { type: String, default: '' },

  currentPage: { type: Number, default: 0 },

  totalPages: { type: Number, default: 0 },

})



const elapsed = ref(0)

const smoothedRemaining = ref(null)

let timer = null



const effectiveSubtitle = computed(() => props.stageLabel || props.subtitle)



const showProgress = computed(() => props.progress != null && props.progress >= 0)



const clampedProgress = computed(() => {

  if (props.progress == null) return 0

  return Math.min(100, Math.max(0, Math.round(props.progress)))

})



const premiumTypicalSeconds = computed(() => {

  const pages = props.totalPages || Math.round((props.estimatedSeconds - 60) / 90) || 8

  return estimatePremiumDeckRange(pages).typicalSeconds

})



const rawStageRemaining = computed(() => {

  if (!props.isPremium || !shouldShowPremiumRemaining(props.stage, props.currentPage)) {

    return null

  }

  return computeStageAwareRemainingSeconds({

    elapsedSeconds: elapsed.value,

    stage: props.stage,

    currentPage: props.currentPage,

    totalPages: props.totalPages,

    typicalSeconds: premiumTypicalSeconds.value,

  })

})



watch(

  [rawStageRemaining, () => props.open],

  ([next, isOpen]) => {

    if (!isOpen) {

      smoothedRemaining.value = null

      return

    }

    if (next == null) {

      smoothedRemaining.value = null

      return

    }

    smoothedRemaining.value = smoothEtaSeconds(smoothedRemaining.value, next)

  },

)



const etaLabel = computed(() => {

  if (props.isPremium && smoothedRemaining.value != null) return '剩余约'

  if (props.isPremium) return '预计总时长'

  return '预估总时长'

})



const etaValue = computed(() => {

  if (props.isPremium && smoothedRemaining.value != null) {

    const st = String(props.stage || '').toLowerCase()

    if ((st === 'postprocessing' || st === 'importing') && smoothedRemaining.value <= 30) {

      return '即将完成'

    }

    return formatDurationLabel(smoothedRemaining.value)

  }

  if (props.isPremium) {

    const pages = props.totalPages || 8

    return formatPremiumDeckRangeLabel(pages)

  }

  return formatDurationLabel(props.estimatedSeconds)

})



const etaHint = computed(() => {

  if (!props.isPremium) return ''

  if (smoothedRemaining.value != null) {

    return '剩余时间随当前生成阶段更新，属正常现象'

  }

  return '高质量模式需逐页生成，请耐心等待'

})



const elapsedLabel = computed(() => formatDurationLabel(elapsed.value))



watch(

  () => props.open,

  (isOpen) => {

    if (timer) {

      clearInterval(timer)

      timer = null

    }

    if (!isOpen) {

      elapsed.value = 0

      smoothedRemaining.value = null

      return

    }

    elapsed.value = 0

    smoothedRemaining.value = null

    timer = setInterval(() => {

      elapsed.value += 1

    }, 1000)

  },

  { immediate: true },

)



onUnmounted(() => {

  if (timer) clearInterval(timer)

})

</script>


