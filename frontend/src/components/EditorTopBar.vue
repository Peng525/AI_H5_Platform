<template>
  <AppShell :project-id="projectId" />
</template>

<script setup>
import AppShell from './AppShell.vue'

defineProps({
  projectId: { type: [String, Number], default: null },
})
</script>
