<template>
  <div class="space-y-2">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
      <ResumeUploadCard
        label="上传简历"
        icon="description"
        :file-name="resumeFileName"
        :uploading="resumeUploading"
        :preview-file="resumeFile"
        @pick="openResumePicker"
        @remove="emit('remove-resume')"
      />
      <ResumeUploadCard
        label="上传工作描述"
        icon="work"
        :file-name="jdFileName"
        :uploading="jdUploading"
        :preview-file="jdFile"
        @pick="openJdPicker"
        @remove="emit('remove-jd')"
      />
    </div>

    <input ref="resumeInputRef" type="file" :accept="RESUME_FILE_ACCEPT" class="hidden" @change="onResumePick" />
    <input ref="jdInputRef" type="file" :accept="RESUME_FILE_ACCEPT" class="hidden" @change="onJdPick" />

    <p v-if="resumeError" class="text-xs text-red-600">{{ resumeError }}</p>
    <p v-if="jdError" class="text-xs text-red-600">{{ jdError }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ResumeUploadCard from './ResumeUploadCard.vue'
import { RESUME_FILE_ACCEPT, validateResumeFile } from '../../utils/resumeFileValidate.js'

defineProps({
  resumeFileName: { type: String, default: '' },
  jdFileName: { type: String, default: '' },
  resumeFile: { type: Object, default: null },
  jdFile: { type: Object, default: null },
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
