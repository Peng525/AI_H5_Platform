<template>
  <PresentationViewer
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
import { useRoute } from 'vue-router'
import { api } from '../api/client'
import PresentationViewer from '../components/PresentationViewer.vue'

const route = useRoute()
const project = ref(null)
const loading = ref(true)
const error = ref('')
const projectId = computed(() => Number(route.params.id))

onMounted(async () => {
  try {
    project.value = await api.getProject(projectId.value)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>
