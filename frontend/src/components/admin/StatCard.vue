<template>
  <div
    class="rounded-xl border border-outline-variant bg-white p-4 shadow-card"
    :class="borderClass"
  >
    <div class="flex items-start justify-between">
      <div>
        <p class="text-xs text-on-surface-variant mb-1">{{ label }}</p>
        <p class="text-2xl font-bold">
          <span v-if="prefix" class="text-lg">{{ prefix }}</span>{{ value }}<span v-if="suffix" class="text-sm font-normal text-on-surface-variant ml-0.5">{{ suffix }}</span>
        </p>
      </div>
      <span
        class="material-symbols-outlined text-[28px] opacity-80"
        :class="iconClass"
      >{{ icon }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  icon: { type: String, required: true },
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  prefix: { type: String, default: '' },
  suffix: { type: String, default: '' },
  color: { type: String, default: 'primary' },
})

const colorMap = {
  primary: { border: 'border-l-4 border-l-primary', icon: 'text-primary' },
  secondary: { border: 'border-l-4 border-l-secondary', icon: 'text-secondary' },
  amber: { border: 'border-l-4 border-l-amber-500', icon: 'text-amber-600' },
  green: { border: 'border-l-4 border-l-green-600', icon: 'text-green-600' },
}

const borderClass = computed(() => colorMap[props.color]?.border || colorMap.primary.border)
const iconClass = computed(() => colorMap[props.color]?.icon || colorMap.primary.icon)
</script>
