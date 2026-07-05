<template>
  <div
    class="relative w-full max-w-md rounded-xl border border-outline-variant/60 bg-surface-container-low px-3 py-2.5 flex items-center gap-2.5"
    :title="fileName"
  >
    <span
      class="shrink-0 w-9 h-9 rounded-lg flex items-center justify-center text-white text-sm font-bold"
      :class="iconClass"
    >
      {{ formatShort }}
    </span>
    <div class="min-w-0 flex-1 text-left">
      <p class="text-sm font-medium text-on-surface truncate">{{ fileName }}</p>
      <p class="text-xs text-on-surface-variant">
        {{ uploading ? '上传中…' : `${formatLabel} · 最大 5MB` }}
      </p>
    </div>
    <button
      type="button"
      class="shrink-0 w-6 h-6 rounded-full bg-on-surface/80 text-white flex items-center justify-center hover:bg-on-surface disabled:opacity-50"
      :disabled="uploading"
      title="移除"
      @click="emit('remove')"
    >
      <span class="material-symbols-outlined text-[14px]">close</span>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatResumeFileLabel } from '../../utils/resumeFileValidate.js'

const props = defineProps({
  fileName: { type: String, required: true },
  uploading: { type: Boolean, default: false },
})

const emit = defineEmits(['remove'])

const formatLabel = computed(() => formatResumeFileLabel(props.fileName))

const formatShort = computed(() => {
  const label = formatLabel.value
  return label.length <= 3 ? label : label.slice(0, 3)
})

const iconClass = computed(() => {
  const label = formatLabel.value
  if (label === 'PDF') return 'bg-red-500'
  if (label === 'DOC') return 'bg-blue-600'
  return 'bg-emerald-600'
})
</script>
