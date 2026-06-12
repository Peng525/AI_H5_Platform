<template>
  <RevealDeckViewer v-if="useReveal && project" :project="project" @exit="exitReveal" />
  <PresentationViewer
    v-else
    :project="project"
    :project-id="projectId"
    :loading="loading"
    :error="error"
    mode="preview"
    :editor-path="`/editor/${projectId}`"
  />
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api/client'
import PresentationViewer from '../components/PresentationViewer.vue'
import RevealDeckViewer from '../components/RevealDeckViewer.vue'
import { DEFAULT_WEB_VIEWPORT_ID } from '../constants/editorPresets.js'
import { compileSlideIfNeeded, shouldCompileSlide } from '../utils/compileStructuredSlide.js'
import { shouldUseRevealPreview } from '../utils/revealAdapter.js'

const route = useRoute()
const router = useRouter()
const project = ref(null)
const loading = ref(true)
const error = ref('')
const projectId = computed(() => String(route.params.publicId || ''))
const useReveal = computed(() => shouldUseRevealPreview(route.query, project.value?.settings))

function exitReveal() {
  router.replace({ path: `/preview/${projectId.value}` })
}

onMounted(async () => {
  try {
    project.value = await api.getProject(projectId.value)
    const vp = project.value.settings?.viewportId || DEFAULT_WEB_VIEWPORT_ID
    const themeId = project.value.settings?.themeId || 'zjy-minimal'
    for (const s of project.value.slides || []) {
      if (shouldCompileSlide(s, vp)) {
        s.canvas_elements = compileSlideIfNeeded(s, vp, themeId)
      }
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>
