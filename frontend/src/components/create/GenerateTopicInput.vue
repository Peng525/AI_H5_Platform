<template>
  <div
    class="rounded-2xl border border-outline-variant shadow-card overflow-hidden bg-white"
    :class="showSend ? 'flex items-stretch' : ''"
  >
    <textarea
      ref="textareaRef"
      :value="modelValue"
      :rows="rows"
      class="topic-input w-full bg-transparent text-sm leading-relaxed resize-none placeholder:text-on-surface-variant/60 caret-primary box-border text-on-surface"
      :class="showSend ? 'flex-1 min-w-0 px-4 py-3' : 'px-4 sm:px-5 py-3 sm:py-3.5 overflow-y-hidden'"
      :placeholder="placeholder"
      :disabled="disabled"
      @input="onInput"
      @paste="onPaste"
    />
    <div
      v-if="showSend"
      class="shrink-0 flex items-center border-l border-outline-variant/40 px-2 sm:px-3"
    >
      <button
        type="button"
        class="inline-flex items-center gap-1 rounded-full bg-[#1a2332] hover:bg-[#243044] px-2.5 py-1.5 text-white text-xs disabled:opacity-50 transition-colors"
        :disabled="disabled || loading || !modelValue.trim()"
        title="消耗 1 次配额"
        aria-label="消耗 1 次配额并生成"
        @click="$emit('submit')"
      >
        <span v-if="loading" class="material-symbols-outlined text-[18px] animate-spin">progress_activity</span>
        <template v-else>
          <span>1</span>
          <span class="material-symbols-outlined text-[14px]">auto_awesome</span>
          <span class="material-symbols-outlined text-[18px]">send</span>
        </template>
      </button>
    </div>
  </div>
</template>

<script setup>
import { nextTick, ref, watch } from 'vue'

const TOPIC_MIN_PX = 44
const TOPIC_MAX_EMPTY_PX = 192
const TOPIC_MAX_FILLED_PX = 320

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '描述您想生成的…' },
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  showSend: { type: Boolean, default: false },
  rows: { type: Number, default: 1 },
  autoResize: { type: Boolean, default: true },
})

const emit = defineEmits(['update:modelValue', 'submit', 'paste'])

const textareaRef = ref(null)

function topicMaxPx() {
  if (props.modelValue.trim() && typeof window !== 'undefined') {
    return Math.min(TOPIC_MAX_FILLED_PX, Math.round(window.innerHeight * 0.35))
  }
  return TOPIC_MAX_EMPTY_PX
}

function resize() {
  if (!props.autoResize) return
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  const maxPx = topicMaxPx()
  const next = Math.min(Math.max(el.scrollHeight, TOPIC_MIN_PX), maxPx)
  el.style.height = `${next}px`
  el.style.overflowY = el.scrollHeight > maxPx ? 'auto' : 'hidden'
}

function scrollToTop() {
  const el = textareaRef.value
  if (!el) return
  el.scrollTop = 0
  el.setSelectionRange(0, 0)
}

function onInput(e) {
  emit('update:modelValue', e.target.value)
  nextTick(resize)
}

function onPaste(e) {
  emit('paste', e)
  nextTick(() => {
    requestAnimationFrame(() => {
      scrollToTop()
      resize()
    })
  })
}

watch(
  () => props.modelValue,
  () => nextTick(resize),
)

defineExpose({ resize, scrollToTop, textareaRef })
</script>

<style scoped>
.topic-input {
  border: none;
  outline: none;
  box-shadow: none;
  appearance: none;
  -webkit-appearance: none;
  min-height: 2.75rem;
}

.topic-input:focus,
.topic-input:focus-visible {
  border: none;
  outline: none;
  box-shadow: none;
}
</style>
