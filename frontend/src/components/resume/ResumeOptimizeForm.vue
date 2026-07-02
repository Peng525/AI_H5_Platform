<template>
  <div class="space-y-3">
    <div
      class="rounded-xl border border-outline-variant bg-white overflow-hidden shadow-sm"
      :class="{ 'ring-2 ring-primary/30 border-primary/40': dragging }"
      @dragover.prevent="dragging = true"
      @dragleave="dragging = false"
      @drop.prevent="onDrop"
    >
      <div class="px-4 pt-3 pb-1 border-b border-outline-variant/40 bg-surface-container-low/30">
        <ResumeAttachmentChip
          :file-name="fileName"
          :uploading="uploading"
          @select="onSelectFile"
          @remove="emit('remove-file')"
        />
      </div>
      <GenerateTopicInput
        ref="topicRef"
        :model-value="prompt"
        placeholder="目标岗位、JD、优化方向…"
        @update:model-value="emit('update:prompt', $event)"
        @paste="emit('paste')"
      />
    </div>
    <p v-if="error" class="text-xs text-red-600 px-1">{{ error }}</p>
    <div v-if="canGenerate" class="flex justify-center pt-1">
      <button
        type="button"
        class="inline-flex items-center gap-2 px-8 py-2.5 rounded-full bg-primary text-on-primary font-medium shadow-card hover:bg-primary/90 transition disabled:opacity-50"
        :disabled="generating || uploading"
        @click="emit('generate')"
      >
        <span class="material-symbols-outlined text-[18px]">auto_awesome</span>
        {{ generating ? '生成中…' : '生成' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import GenerateTopicInput from '../create/GenerateTopicInput.vue'
import ResumeAttachmentChip from './ResumeAttachmentChip.vue'

defineProps({
  prompt: { type: String, default: '' },
  fileName: { type: String, default: '' },
  uploading: { type: Boolean, default: false },
  generating: { type: Boolean, default: false },
  canGenerate: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const emit = defineEmits(['update:prompt', 'select-file', 'remove-file', 'generate', 'paste'])

const topicRef = ref(null)
const dragging = ref(false)
const MAX = 5 * 1024 * 1024

function onSelectFile(payload) {
  emit('select-file', payload)
}

function onDrop(e) {
  dragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (!file) return
  if (file.size > MAX) {
    emit('select-file', { error: '文件超过 5MB 限制' })
    return
  }
  emit('select-file', { file })
}

defineExpose({
  resize: () => topicRef.value?.resize(),
})
</script>
