<template>
  <div
    v-if="variant === 'bar'"
    class="text-white text-sm font-medium px-3 py-1.5 rounded-sm"
    :style="{ backgroundColor: accent || '#2563eb' }"
  >
    {{ title }}
  </div>
  <div v-else class="text-sm font-semibold pb-1 border-b-2" :style="{ borderColor: accent || '#2563eb', color: accent || '#2563eb' }">
    {{ title }}
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  accent: { type: String, default: '#2563eb' },
  variant: { type: String, default: 'bar' },
})
</script>
