<template>
  <div
    class="bg-white shadow-2xl overflow-hidden flex flex-col shrink-0"
    :class="frameClass"
    :style="frameStyle"
  >
    <div
      v-if="device === 'mobile'"
      class="h-7 w-full flex justify-between items-center px-4 pt-1 shrink-0 bg-white"
    >
      <span class="text-[12px] font-medium text-gray-900">9:41</span>
      <div class="flex gap-1 items-center opacity-80 text-gray-900">
        <span class="material-symbols-outlined text-[14px]">signal_cellular_alt</span>
        <span class="material-symbols-outlined text-[14px]">wifi</span>
        <span class="material-symbols-outlined text-[14px]">battery_full</span>
      </div>
    </div>
    <div v-else class="h-8 shrink-0 bg-gray-100 border-b border-gray-200 flex items-center px-3 gap-1.5">
      <span class="w-2.5 h-2.5 rounded-full bg-red-400" />
      <span class="w-2.5 h-2.5 rounded-full bg-amber-400" />
      <span class="w-2.5 h-2.5 rounded-full bg-green-400" />
      <span class="ml-2 text-[10px] text-gray-500 truncate flex-1">{{ label }}</span>
    </div>

    <div class="flex-1 min-h-0 flex flex-col overflow-hidden">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  width: { type: Number, default: 375 },
  height: { type: Number, default: 812 },
  device: { type: String, default: 'mobile' },
  label: { type: String, default: '网页预览' },
  maxHeight: { type: String, default: 'calc(100vh - 120px)' },
})

const frameClass = computed(() =>
  props.device === 'mobile'
    ? 'rounded-[2rem] border-[8px] border-gray-900'
    : 'rounded-lg border border-gray-300'
)

const frameStyle = computed(() => ({
  width: `${props.width}px`,
  height: `min(${props.height}px, ${props.maxHeight})`,
}))
</script>
