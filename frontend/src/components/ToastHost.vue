<template>
  <Teleport to="body">
    <div
      class="fixed bottom-4 left-1/2 -translate-x-1/2 z-[200] flex flex-col gap-2 w-[min(24rem,calc(100vw-2rem))] pointer-events-none"
      aria-live="polite"
      aria-atomic="true"
    >
      <TransitionGroup name="toast">
        <div
          v-for="t in toasts"
          :key="t.id"
          class="pointer-events-auto px-4 py-2.5 rounded-lg shadow-elevated border text-sm font-medium flex items-start gap-2"
          :class="toastClass(t.type)"
          role="status"
        >
          <span class="material-symbols-outlined text-[18px] shrink-0">{{ icon(t.type) }}</span>
          <span class="flex-1 leading-snug">{{ t.message }}</span>
          <button type="button" class="shrink-0 opacity-70 hover:opacity-100" @click="dismiss(t.id)">
            <span class="material-symbols-outlined text-[16px]">close</span>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { useToast } from '../composables/useToast.js'

const { toasts, dismiss } = useToast()

function toastClass(type) {
  if (type === 'success') return 'bg-secondary/95 text-white border-secondary'
  if (type === 'error') return 'bg-red-600 text-white border-red-700'
  return 'bg-white text-on-surface border-outline-variant'
}

function icon(type) {
  if (type === 'success') return 'check_circle'
  if (type === 'error') return 'error'
  return 'info'
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.22s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
