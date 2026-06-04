<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50"
      role="dialog"
      aria-modal="true"
      @click.self="$emit('close')"
    >
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg max-h-[min(90vh,720px)] flex flex-col overflow-hidden">
        <div class="flex items-center justify-between px-4 py-3 border-b border-outline-variant shrink-0">
          <h2 class="text-sm font-semibold">{{ title }}</h2>
          <button type="button" class="p-1.5 rounded-lg hover:bg-surface-container-low" aria-label="关闭" @click="$emit('close')">
            <span class="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>
        <div class="flex-1 min-h-0 overflow-y-auto">
          <slot />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '' },
})

defineEmits(['close'])
</script>
