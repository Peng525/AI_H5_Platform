<template>
  <div class="flex flex-col h-full min-h-0 border-r border-outline-variant bg-white">
    <div ref="scrollRef" class="flex-1 overflow-y-auto p-3 space-y-3">
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

const props = defineProps({
  messages: { type: Array, default: () => [] },
  generating: { type: Boolean, default: false },
})

const emit = defineEmits(['submit'])

const input = ref('')
const scrollRef = ref(null)

watch(() => props.messages.length, () => {
  nextTick(() => {
    if (scrollRef.value) scrollRef.value.scrollTop = scrollRef.value.scrollHeight
  })
})

function submit() {
  if (!input.value.trim() || props.generating) return
  emit('submit', input.value.trim())
  input.value = ''
}
</script>
