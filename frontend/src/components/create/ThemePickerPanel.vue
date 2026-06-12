<template>
  <div class="p-2 space-y-1 max-h-[min(70vh,28rem)] overflow-y-auto">
    <button
      v-for="opt in options"
      :key="opt.id"
      type="button"
      class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg border text-sm text-left transition-all"
      :class="
        opt.id === activeThemeId
          ? 'border-primary bg-primary/8 text-primary font-medium'
          : 'border-transparent hover:bg-surface-container-low text-on-surface'
      "
      :disabled="disabled"
      @click="$emit('select', opt.id)"
    >
      <span
        class="w-1.5 self-stretch min-h-[2rem] rounded-full shrink-0"
        :style="{ background: opt.swatch }"
        aria-hidden="true"
      />
      <span class="flex-1 min-w-0 truncate">{{ opt.label }}</span>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { listThemeOptions } from '../../utils/applyProjectTheme.js'

defineProps({
  activeThemeId: { type: String, default: 'zjy-minimal' },
  disabled: { type: Boolean, default: false },
})

defineEmits(['select'])

const options = computed(() => listThemeOptions())
</script>
