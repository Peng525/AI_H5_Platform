<template>
  <Transition name="result-drawer" @after-leave="$emit('after-leave')">
    <div
      v-if="open"
      class="result-drawer-shell h-full shrink-0 overflow-hidden min-h-0"
      role="complementary"
      :aria-label="title"
    >
      <aside class="result-drawer-panel w-[360px] max-w-[100vw] h-full flex flex-col bg-white border-l border-outline-variant shadow-xl overflow-hidden min-h-0">
        <div class="flex items-center justify-between px-4 py-3 border-b border-outline-variant shrink-0">
          <h2 class="text-sm font-semibold text-on-surface truncate pr-2">{{ title }}</h2>
          <button
            type="button"
            class="p-1.5 rounded-lg hover:bg-surface-container-low shrink-0"
            aria-label="关闭"
            @click="$emit('close')"
          >
            <span class="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>
        <div class="flex-1 min-h-0 overflow-y-auto overflow-x-hidden">
          <slot />
        </div>
      </aside>
    </div>
  </Transition>
</template>

<script setup>
defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '' },
})

defineEmits(['close', 'after-leave'])
</script>

<style scoped>
.result-drawer-shell {
  max-width: min(100vw, 360px);
}

.result-drawer-enter-active,
.result-drawer-leave-active {
  transition: max-width 0.24s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.result-drawer-enter-from,
.result-drawer-leave-to {
  max-width: 0;
}

.result-drawer-enter-to,
.result-drawer-leave-from {
  max-width: min(100vw, 360px);
}
</style>
