<template>
  <div class="rounded-lg border border-outline-variant bg-surface-container-lowest p-4">
    <p class="text-sm font-medium mb-2">安全验证</p>

    <button
      type="button"
      class="w-full py-2.5 rounded-lg border border-outline-variant text-sm hover:bg-surface-container-low"
      :class="verified ? 'text-secondary border-secondary/40' : ''"
      @click="open"
    >
      <span v-if="verified" class="inline-flex items-center gap-1">
        <span class="material-symbols-outlined text-[18px]">verified</span>
        验证已通过
      </span>
      <span v-else class="inline-flex items-center gap-1">
        <span class="material-symbols-outlined text-[18px]">extension</span>
        点击完成滑动拼图验证
      </span>
    </button>

    <p v-if="error" class="text-xs text-red-600 mt-1">{{ error }}</p>

    <!-- 滑动拼图弹窗 -->
    <Vcode
      :show="showPuzzle"
      :type="'modal'"
      :canvas-width="310"
      :canvas-height="160"
      :puzzle-scale="1"
      :slider-size="50"
      :range="10"
      success-text="验证通过！"
      fail-text="验证失败，请重试"
      slider-text="拖动滑块完成拼图"
      @success="onSuccess"
      @fail="onFail"
      @close="showPuzzle = false"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Vcode from 'vue3-puzzle-vcode'

const emit = defineEmits(['verified', 'ticket'])

const showPuzzle = ref(false)
const verified = ref(false)
const error = ref('')

function open() {
  if (verified.value) return
  error.value = ''
  showPuzzle.value = true
}

function onSuccess({ deviation }) {
  showPuzzle.value = false
  verified.value = true
  error.value = ''
  // 生成模拟票据（与腾讯云机制一致：前端验证成功后向后端提交凭证）
  emit('verified', true)
  emit('ticket', {
    ticket: `slide_${Date.now()}`,
    randstr: `@${Math.round(deviation)}px`,
  })
}

function onFail() {
  verified.value = false
  error.value = '验证失败，请重试'
  emit('verified', false)
}

function reset() {
  verified.value = false
  error.value = ''
  emit('verified', false)
  emit('ticket', { ticket: '', randstr: '' })
}

defineExpose({ reset })
</script>
