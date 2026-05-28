<template>
  <PresentationViewer
    :project="project"
    :project-id="project?.id"
    :loading="loading"
    :error="error"
    mode="share"
    loading-text="加载分享演示…"
  />
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/client'
import PresentationViewer from '../components/PresentationViewer.vue'

const route = useRoute()
const project = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    project.value = await api.sharePreview(route.params.slug)
  } catch (e) {
    error.value = e.message || '无法加载分享内容'
  } finally {
    loading.value = false
  }
})
</script>
