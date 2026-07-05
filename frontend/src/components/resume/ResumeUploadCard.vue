<template>
  <div
    class="relative rounded-xl border border-outline-variant bg-white px-4 py-6 min-h-[10.5rem] flex flex-col items-center justify-center text-center"
  >
    <template v-if="!fileName">
      <button
        type="button"
        class="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-outline-variant text-sm hover:bg-surface-container-low transition-colors disabled:opacity-50 shrink-0"
        :disabled="uploading"
        @click="emit('pick')"
      >
        <span class="material-symbols-outlined text-[18px] text-primary">{{ icon }}</span>
        {{ uploading ? '上传中…' : label }}
      </button>
      <p class="text-xs text-on-surface-variant mt-2">PDF / 图片 · 最大 5MB</p>
    </template>

    <template v-else>
      <button
        v-if="canPreview"
        type="button"
        class="text-sm font-medium text-primary truncate max-w-full px-2 hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 rounded"
        :title="fileName"
        :disabled="uploading"
        @click="previewOpen = true"
      >
        {{ fileName }}
      </button>
      <p
        v-else
        class="text-sm font-medium text-on-surface truncate max-w-full px-2"
        :title="fileName"
      >
        {{ fileName }}
      </p>
      <button
        type="button"
        class="absolute top-3 right-3 text-on-surface-variant hover:text-red-600 disabled:opacity-50"
        :disabled="uploading"
        title="移除"
        @click.stop="emit('remove')"
      >
        <span class="material-symbols-outlined text-[18px]">close</span>
      </button>
    </template>

    <ResumeFilePreviewModal
      :open="previewOpen"
      :file-name="fileName"
      :file="previewFile"
      @close="previewOpen = false"
    />
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import ResumeFilePreviewModal from './ResumeFilePreviewModal.vue'

const props = defineProps({
  label: { type: String, required: true },
  icon: { type: String, default: 'upload_file' },
  fileName: { type: String, default: '' },
  uploading: { type: Boolean, default: false },
  previewFile: { type: Object, default: null },
})

const emit = defineEmits(['pick', 'remove'])

const previewOpen = ref(false)

const canPreview = computed(() => props.previewFile instanceof File)

watch(
  () => props.fileName,
  (name) => {
    if (!name) previewOpen.value = false
  },
)
</script>
