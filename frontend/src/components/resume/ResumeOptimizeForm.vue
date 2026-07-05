<template>
  <div class="space-y-3">
    <div class="relative pb-5">
      <ResumeAttachmentBar
        :resume-file-name="resumeFileName"
        :jd-file-name="jdFileName"
        :resume-file="resumeFile"
        :jd-file="jdFile"
        :resume-uploading="resumeUploading"
        :jd-uploading="jdUploading"
        :resume-error="resumeError"
        :jd-error="jdError"
        @select-resume="emit('select-resume', $event)"
        @remove-resume="emit('remove-resume')"
        @select-jd="emit('select-jd', $event)"
        @remove-jd="emit('remove-jd')"
      />
      <p class="absolute bottom-0 right-0 text-xs text-on-surface-variant/80 text-right max-w-[14rem] leading-snug">
        仅支持上传一份简历以及一个工作描述
      </p>
    </div>
    <GenerateTopicInput
      ref="topicRef"
      :model-value="prompt"
      placeholder="目标岗位、JD、优化方向…"
      @update:model-value="emit('update:prompt', $event)"
      @paste="emit('paste')"
    />
    <p v-if="error" class="text-xs text-red-600 px-1">{{ error }}</p>
    <div v-if="canGenerate" class="flex justify-center pt-1 relative">
      <slot name="generate-hint" />
      <button
        type="button"
        class="inline-flex items-center gap-2 px-8 py-2.5 rounded-full bg-primary text-on-primary font-medium shadow-card hover:bg-primary/90 transition disabled:opacity-50"
        :disabled="generating || resumeUploading || jdUploading"
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
import ResumeAttachmentBar from './ResumeAttachmentBar.vue'

defineProps({
  prompt: { type: String, default: '' },
  resumeFileName: { type: String, default: '' },
  jdFileName: { type: String, default: '' },
  resumeFile: { type: Object, default: null },
  jdFile: { type: Object, default: null },
  resumeUploading: { type: Boolean, default: false },
  jdUploading: { type: Boolean, default: false },
  generating: { type: Boolean, default: false },
  canGenerate: { type: Boolean, default: false },
  error: { type: String, default: '' },
  resumeError: { type: String, default: '' },
  jdError: { type: String, default: '' },
})

const emit = defineEmits([
  'update:prompt',
  'select-resume',
  'remove-resume',
  'select-jd',
  'remove-jd',
  'generate',
  'paste',
])

const topicRef = ref(null)

defineExpose({
  resize: () => topicRef.value?.resize(),
})
</script>
