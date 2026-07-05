<template>
  <div class="flex flex-wrap gap-2">
    <button
      v-for="chip in industries"
      :key="chip.id"
      type="button"
      class="px-3 py-1.5 rounded-full text-sm border transition"
      :class="selectedId === chip.id
        ? 'border-primary bg-primary/10 text-primary font-medium'
        : 'border-outline-variant/70 bg-white text-on-surface hover:border-outline-variant'"
      @click="$emit('update:selectedId', chip.id)"
    >
      {{ chip.label }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  industries: { type: Array, default: () => [] },
  selectedId: { type: String, default: 'all' },
})

defineEmits(['update:selectedId'])
</script>
