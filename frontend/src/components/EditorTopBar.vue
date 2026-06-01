<template>
  <AppShell
    :project-id="projectId"
    :hide-publish="hidePublish"
    :nav-mode="navMode"
    :show-quota="navMode !== 'admin'"
  >
    <template #actions>
      <slot name="actions" />
    </template>
  </AppShell>
</template>

<script setup>
import AppShell from './AppShell.vue'

defineProps({
  projectId: { type: [String, Number], default: null },
  hidePublish: { type: Boolean, default: false },
  navMode: { type: String, default: 'user' },
})
</script>
