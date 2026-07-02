<template>
  <div class="flex flex-wrap items-center gap-2 min-h-[1.75rem]">
    <template v-if="fileName">
      <span
        class="inline-flex items-center gap-1.5 max-w-full px-2.5 py-1 rounded-lg bg-surface-container-low text-xs text-on-surface"
      >
        <span class="material-symbols-outlined text-[16px] text-on-surface-variant shrink-0">{{ fileIcon }}</span>
        <span class="truncate max-w-[14rem]" :title="fileName">{{ fileName }}</span>
      </span>
      <button
        type="button"
        class="text-xs text-primary hover:underline disabled:opacity-50"
        :disabled="uploading"
        @click="openPicker"
      >
        更换
      </button>
      <button
        type="button"
        class="text-xs text-on-surface-variant hover:text-red-600 disabled:opacity-50"
        :disabled="uploading"
        title="移除附件"
        @click="$emit('remove')"
      >
        <span class="material-symbols-outlined text-[16px] align-middle">close</span>
      </button>
    </template>
    <button
      v-else
      type="button"
      class="inline-flex items-center gap-1.5 text-xs text-primary hover:underline disabled:opacity-50"
      :disabled="uploading"
      @click="openPicker"
    >
      <span class="material-symbols-outlined text-[16px]">attach_file</span>
      {{ uploading ? '上传中…' : '上传简历' }}
      <span class="text-on-surface-variant">· PDF / 图片 · 最大 5MB</span>
    </button>
    <input
      ref="inputRef"
      type="file"
      accept=".pdf,.png,.jpg,.jpeg,image/*,application/pdf"
      class="hidden"
      @change="onPick"
    />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  fileName: { type: String, default: '' },
  uploading: { type: Boolean, default: false },
})

const emit = defineEmits(['select', 'remove'])

const inputRef = ref(null)
const MAX = 5 * 1024 * 1024

const fileIcon = computed(() => {
  const n = (props.fileName || '').toLowerCase()
  if (n.endsWith('.pdf')) return 'picture_as_pdf'
  if (/\.(png|jpe?g|webp|gif)$/.test(n)) return 'image'
  return 'attach_file'
})

function validate(file) {
  if (file.size > MAX) {
    emit('select', { error: '文件超过 5MB 限制' })
    return false
  }
  return true
}

function openPicker() {
  inputRef.value?.click()
}

function onPick(e) {
  const file = e.target.files?.[0]
  if (file && validate(file)) emit('select', { file })
  e.target.value = ''
}

defineExpose({ openPicker })
</script>
