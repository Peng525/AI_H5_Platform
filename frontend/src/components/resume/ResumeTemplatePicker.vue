<template>
  <section>
    <h2 v-if="heading" class="text-sm font-semibold text-on-surface-variant mb-3">{{ heading }}</h2>
    <p v-if="!templates.length" class="text-sm text-on-surface-variant py-4 text-center">暂无模板</p>
    <ul v-else class="flex md:grid md:grid-cols-3 gap-2 overflow-x-auto pb-1">
      <li v-for="tpl in templates" :key="tpl.id" class="snap-start shrink-0 w-[min(78vw,14rem)] md:w-auto">
        <PromptTemplateCard
          :title="tpl.title"
          :description="tpl.description"
          :fields="showFields ? (tpl.fields || []) : []"
          :preview-url="isVisual ? resolveResumePreviewUrl(tpl.preview_url) : ''"
          :show-preview="isVisual"
          :selected="selectedId === tpl.id"
          @select="openPreview(tpl)"
        />
      </li>
    </ul>

    <ResumeTemplatePreviewModal
      :open="previewOpen"
      :template="previewTpl"
      :mode="variant"
      @confirm="confirmPreview"
      @cancel="closePreview"
    />
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import PromptTemplateCard from '../create/PromptTemplateCard.vue'
import ResumeTemplatePreviewModal from './ResumeTemplatePreviewModal.vue'
import { resolveResumePreviewUrl } from '../../utils/resumePreviewUrl.js'

const props = defineProps({
  templates: { type: Array, default: () => [] },
  selectedId: { type: String, default: '' },
  heading: { type: String, default: '选择简历模板' },
  showFields: { type: Boolean, default: false },
  variant: { type: String, default: 'visual' },
})

const emit = defineEmits(['select'])

const previewOpen = ref(false)
const previewTpl = ref(null)

const isVisual = computed(() => props.variant === 'visual')

function openPreview(tpl) {
  previewTpl.value = tpl
  previewOpen.value = true
}

function closePreview() {
  previewOpen.value = false
  previewTpl.value = null
}

function confirmPreview() {
  if (previewTpl.value) {
    emit('select', previewTpl.value)
  }
  closePreview()
}
</script>
