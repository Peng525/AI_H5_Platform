<template>
  <AppShell :page-title="projectTitle" :project-id="projectId" />
</template>

<script setup>
import AppShell from './AppShell.vue'

defineProps({
  projectTitle: { type: String, default: '未命名调研报告' },
  projectId: { type: [String, Number], default: null },
})
</script>
