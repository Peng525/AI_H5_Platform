<template>
  <div class="bg-[#2563eb] text-white text-sm font-medium px-3 py-1.5 rounded-sm">
    {{ title }}
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
})
</script>
