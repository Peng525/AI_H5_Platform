<template>
  <div class="flex items-center min-w-0 shrink-0">
    <div class="flex items-center gap-2 min-w-0">
      <CreateHomeButton />
      <slot />
    </div>
    <BackToResultButton class="ml-4 sm:ml-6 shrink-0" />
  </div>
</template>

<script setup>
import CreateHomeButton from './CreateHomeButton.vue'
import BackToResultButton from './BackToResultButton.vue'
</script>
