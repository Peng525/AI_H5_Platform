<template>
  <div class="flex flex-col h-full min-h-0 border-r border-outline-variant bg-white">
    <div ref="scrollRef" class="flex-1 overflow-y-auto p-3 space-y-3">
      <div
        v-if="!messages.length && !generating"
        class="rounded-lg bg-surface-container-low/80 px-3 py-4 text-sm space-y-3"
      >
        <p class="text-on-surface-variant leading-relaxed">
          AI 助手会在这里回复；生成完成后可继续输入优化指令，例如润色经历、匹配 JD、精简篇幅等。
        </p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="(hint, i) in suggestions"
            :key="i"
            type="button"
            class="text-left text-xs px-2.5 py-1.5 rounded-full border border-outline-variant bg-white hover:border-primary/40 hover:bg-primary/5 transition-colors"
            @click="applySuggestion(hint)"
          >
            {{ hint }}
          </button>
        </div>
      </div>
      <div
        v-for="msg in messages"
        :key="msg.id || msg.content.slice(0, 24)"
        class="rounded-lg px-3 py-2 text-sm"
        :class="msg.role === 'user' ? 'bg-primary/10 ml-4' : 'bg-surface-container-low mr-4'"
      >
        <p class="text-xs font-medium text-on-surface-variant mb-1">{{ msg.role === 'user' ? '你' : '助手' }}</p>
        <p class="whitespace-pre-wrap leading-relaxed">{{ msg.content }}</p>
      </div>
      <PageLoading v-if="generating" message="生成中…" />
    </div>
    <div class="p-3 border-t border-outline-variant shrink-0 space-y-2">
      <textarea
        ref="inputRef"
        v-model="input"
        rows="3"
        class="w-full border border-outline-variant rounded-lg px-3 py-2 text-sm resize-none"
        placeholder="输入优化指令…"
        :disabled="generating"
      />
      <button
        type="button"
        class="w-full py-2.5 rounded-lg bg-primary text-on-primary text-sm font-medium disabled:opacity-50"
        :disabled="generating || !input.trim()"
        @click="submit"
      >
        {{ generating ? '生成中…' : '生成' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { nextTick, ref, watch } from 'vue'
import PageLoading from '../PageLoading.vue'
import { RESUME_CHAT_SUGGESTIONS } from '../../constants/resumeChatSuggestions.js'

const props = defineProps({
  messages: { type: Array, default: () => [] },
  generating: { type: Boolean, default: false },
})

const emit = defineEmits(['submit'])

const input = ref('')
const inputRef = ref(null)
const scrollRef = ref(null)
const suggestions = RESUME_CHAT_SUGGESTIONS

watch(() => props.messages.length, () => {
  nextTick(() => {
    if (scrollRef.value) scrollRef.value.scrollTop = scrollRef.value.scrollHeight
  })
})

function applySuggestion(text) {
  input.value = text
  nextTick(() => inputRef.value?.focus())
}

function submit() {
  if (!input.value.trim() || props.generating) return
  emit('submit', input.value.trim())
  input.value = ''
}
</script>
