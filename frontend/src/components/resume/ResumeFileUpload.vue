<template>
  <div
    class="rounded-xl border border-dashed border-outline-variant bg-white px-4 py-6 text-center"
    :class="{ 'border-primary bg-primary/5': dragging }"
    @dragover.prevent="dragging = true"
    @dragleave="dragging = false"
    @drop.prevent="onDrop"
  >
    <input ref="inputRef" type="file" accept=".pdf,.png,.jpg,.jpeg,image/*,application/pdf" class="hidden" @change="onPick" />
    <span class="material-symbols-outlined text-3xl text-on-surface-variant">upload_file</span>
    <p class="text-sm text-on-surface-variant mt-2">PDF / 图片 · 最大 5MB</p>
    <button
      type="button"
      class="mt-3 inline-flex items-center gap-2 px-4 py-2 rounded-full border border-outline-variant text-sm hover:bg-surface-container-low"
      :disabled="uploading"
      @click="inputRef?.click()"
    >
      <span class="material-symbols-outlined text-[18px]">attach_file</span>
      {{ uploading ? '上传中…' : (fileName || '上传简历') }}
    </button>
    <p v-if="error" class="text-xs text-red-600 mt-2">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  uploading: { type: Boolean, default: false },
  fileName: { type: String, default: '' },
  error: { type: String, default: '' },
})

const emit = defineEmits(['select'])

const inputRef = ref(null)
const dragging = ref(false)
const MAX = 5 * 1024 * 1024

function validate(file) {
  if (file.size > MAX) {
    emit('select', { error: '文件超过 5MB 限制' })
    return false
  }
  return true
}

function onPick(e) {
  const file = e.target.files?.[0]
  if (file && validate(file)) emit('select', { file })
  e.target.value = ''
}

function onDrop(e) {
  dragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file && validate(file)) emit('select', { file })
}
</script>
