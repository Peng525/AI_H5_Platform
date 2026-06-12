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
            {{ subtitle }}
          </p>
        </div>
        <div class="rounded-xl border border-outline-variant bg-white px-5 py-4 space-y-2 text-sm">
          <div class="flex justify-between tabular-nums">
            <span class="text-on-surface-variant">预估时间</span>
            <span class="font-medium">约 {{ estimatedSeconds }} 秒</span>
          </div>
          <div class="flex justify-between tabular-nums">
            <span class="text-on-surface-variant">已等待</span>
            <span class="font-medium text-primary">{{ elapsedLabel }}</span>
          </div>
        </div>
        <p class="text-xs text-on-surface-variant">{{ footerHint }}</p>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  estimatedSeconds: { type: Number, default: 48 },
  title: { type: String, default: '加载中…' },
  subtitle: {
    type: String,
    default: 'AI 正在根据您的提示词创建演示，请稍候…',
  },
  footerHint: { type: String, default: '生成完成后将开始绘制页面' },
})

const elapsed = ref(0)

let timer = null

const elapsedLabel = computed(() => {
  const s = elapsed.value
  if (s < 60) return `${s} 秒`
  const m = Math.floor(s / 60)
  const r = s % 60
  return r ? `${m} 分 ${r} 秒` : `${m} 分`
})

watch(
  () => props.open,
  (isOpen) => {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
    if (!isOpen) {
      elapsed.value = 0
      return
    }
    elapsed.value = 0
    timer = setInterval(() => {
      elapsed.value += 1
    }, 1000)
  },
  { immediate: true }
)

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>
