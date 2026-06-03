<script setup>
import AspectRatioSelect from './AspectRatioSelect.vue'

defineProps({
  modelValue: { type: String, default: '9:16' },
})

defineEmits(['update:modelValue'])
</script>

<template>
  <AspectRatioSelect
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
  />
</template>
