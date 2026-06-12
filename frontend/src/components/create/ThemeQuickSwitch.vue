<template>
  <ThemePickerPanel
    :active-theme-id="activeThemeId"
    :disabled="disabled"
    @select="$emit('select', $event)"
  />
</template>

<script setup>
import ThemePickerPanel from './ThemePickerPanel.vue'

defineProps({
  activeThemeId: { type: String, default: 'zjy-minimal' },
  disabled: { type: Boolean, default: false },
})

defineEmits(['select'])
</script>
