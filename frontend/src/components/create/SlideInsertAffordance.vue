<template>
  <div
    data-slide-insert
    class="pointer-events-none"
    :class="rootClass"
    @mousedown.stop
    @click.stop
  >
    <div
      class="pointer-events-auto inline-flex items-center rounded-full border border-white/15 bg-[#2a2a2e] shadow-lg overflow-hidden"
      role="toolbar"
      aria-label="插入页面"
    >
      <button
        type="button"
        class="group relative px-3 py-2 text-white/90 hover:bg-white/10 transition-colors"
        title="添加空白页"
        @click="$emit('add-blank')"
      >
        <span class="material-symbols-outlined text-[18px] leading-none">add</span>
        <span
          class="pointer-events-none absolute left-1/2 -translate-x-1/2 top-full mt-1.5 whitespace-nowrap rounded-md bg-[#1a1a1c] px-2 py-1 text-[11px] text-white opacity-0 group-hover:opacity-100 transition-opacity z-30"
        >
          添加空白页
        </span>
      </button>
      <span class="w-px h-5 bg-white/15 shrink-0" aria-hidden="true" />
      <button
        type="button"
        class="group relative px-3 py-2 text-white/90 hover:bg-white/10 transition-colors"
        title="AI 生成卡片"
        @click="$emit('open-generate')"
      >
        <span class="material-symbols-outlined text-[18px] leading-none">auto_awesome</span>
        <span
          class="pointer-events-none absolute left-1/2 -translate-x-1/2 top-full mt-1.5 whitespace-nowrap rounded-md bg-[#1a1a1c] px-2 py-1 text-[11px] text-white opacity-0 group-hover:opacity-100 transition-opacity z-30"
        >
          AI 生成卡片
        </span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  placement: {
    type: String,
    default: 'gap',
    validator: (v) => ['gap', 'below-card'].includes(v),
  },
})

defineEmits(['add-blank', 'open-generate'])

const rootClass = computed(() =>
  props.placement === 'below-card'
    ? 'absolute left-1/2 z-20 -translate-x-1/2 -translate-y-1/2'
    : 'absolute left-1/2 top-1/2 z-20 -translate-x-1/2 -translate-y-1/2',
)
</script>
