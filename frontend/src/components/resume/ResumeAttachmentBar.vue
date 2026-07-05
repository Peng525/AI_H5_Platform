<template>
  <div class="space-y-2">
    <div class="flex items-stretch gap-3 min-h-[5.5rem]">
      <button
        type="button"
        class="shrink-0 w-[7.5rem] flex flex-col items-center justify-center gap-1.5 rounded-xl border border-outline-variant bg-white px-3 py-3 text-sm hover:bg-surface-container-low transition-colors disabled:opacity-50"
        :disabled="resumeUploading"
        @click="openResumePicker"
      >
        <span class="material-symbols-outlined text-[22px] text-primary">description</span>
        <span class="text-xs font-medium text-on-surface">{{ resumeUploading ? '上传中…' : '上传简历' }}</span>
      </button>

      <div class="flex-1 min-w-0 flex flex-col items-center justify-center gap-2 px-1">
        <template v-if="resumeFileName || jdFileName">
          <ResumeAttachmentChip
            v-if="resumeFileName"
            :file-name="resumeFileName"
            :uploading="resumeUploading"
            @remove="emit('remove-resume')"
          />
          <ResumeAttachmentChip
            v-if="jdFileName"
            :file-name="jdFileName"
            :uploading="jdUploading"
            @remove="emit('remove-jd')"
          />
        </template>
        <p v-else class="text-xs text-on-surface-variant/70 text-center leading-snug">
          在左侧上传简历，右侧上传工作描述
        </p>
      </div>

      <button
        type="button"
        class="shrink-0 w-[7.5rem] flex flex-col items-center justify-center gap-1.5 rounded-xl border border-outline-variant bg-white px-3 py-3 text-sm hover:bg-surface-container-low transition-colors disabled:opacity-50"
        :disabled="jdUploading"
        @click="openJdPicker"
      >
        <span class="material-symbols-outlined text-[22px] text-primary">work</span>
        <span class="text-xs font-medium text-on-surface">{{ jdUploading ? '上传中…' : '上传工作描述' }}</span>
      </button>
    </div>

    <input ref="resumeInputRef" type="file" :accept="RESUME_FILE_ACCEPT" class="hidden" @change="onResumePick" />
    <input ref="jdInputRef" type="file" :accept="RESUME_FILE_ACCEPT" class="hidden" @change="onJdPick" />

    <p v-if="resumeError" class="text-xs text-red-600">{{ resumeError }}</p>
    <p v-if="jdError" class="text-xs text-red-600">{{ jdError }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ResumeAttachmentChip from './ResumeAttachmentChip.vue'
import { RESUME_FILE_ACCEPT, validateResumeFile } from '../../utils/resumeFileValidate.js'

defineProps({
  resumeFileName: { type: String, default: '' },
  jdFileName: { type: String, default: '' },
  resumeUploading: { type: Boolean, default: false },
  jdUploading: { type: Boolean, default: false },
  resumeError: { type: String, default: '' },
  jdError: { type: String, default: '' },
})

const emit = defineEmits(['select-resume', 'remove-resume', 'select-jd', 'remove-jd'])

const resumeInputRef = ref(null)
const jdInputRef = ref(null)

function openResumePicker() {
  resumeInputRef.value?.click()
}

function openJdPicker() {
  jdInputRef.value?.click()
}

function onResumePick(e) {
  const file = e.target.files?.[0]
  const result = validateResumeFile(file)
  if (!result.ok) {
    emit('select-resume', { error: result.error })
  } else {
    emit('select-resume', { file: result.file })
  }
  e.target.value = ''
}

function onJdPick(e) {
  const file = e.target.files?.[0]
  const result = validateResumeFile(file)
  if (!result.ok) {
    emit('select-jd', { error: result.error })
  } else {
    emit('select-jd', { file: result.file })
  }
  e.target.value = ''
}
</script>
