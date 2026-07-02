<template>
  <div
    class="grid gap-3"
    :class="gridClass"
  >
    <slot />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  cols: { type: Number, default: 1 },
})

const gridClass = computed(() => {
  if (props.cols === 3) return 'grid-cols-3'
  if (props.cols === 2) return 'grid-cols-2'
  return 'grid-cols-1'
})
</script>
