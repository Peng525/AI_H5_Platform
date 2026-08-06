<template>
  <VisualTemplatePreviewModal
    :open="open"
    :template="template"
    :mode="mode"
    :resolve-preview-url="resolveResumePreviewUrl"
    @confirm="emit('confirm')"
    @cancel="emit('cancel')"
  />
</template>

<script setup>
import VisualTemplatePreviewModal from '../create/VisualTemplatePreviewModal.vue'
import { resolveResumePreviewUrl } from '../../utils/resumePreviewUrl.js'

defineProps({
  open: { type: Boolean, default: false },
  template: { type: Object, default: null },
  mode: { type: String, default: 'visual' },
})

const emit = defineEmits(['confirm', 'cancel'])
</script>
