<template>
  <div class="flex flex-col items-center justify-center py-12 text-on-surface-variant" :class="compact ? 'py-6' : ''">
    <span class="material-symbols-outlined text-primary text-3xl animate-spin mb-2">progress_activity</span>
    <p class="text-sm">{{ message }}</p>
  </div>
</template>

<script setup>
defineProps({
  message: { type: String, default: '加载中…' },
  compact: { type: Boolean, default: false },
})
</script>

<style scoped>
@keyframes spin {
  to { transform: rotate(360deg); }
}
.animate-spin {
  animation: spin 1s linear infinite;
  display: inline-block;
}
</style>
