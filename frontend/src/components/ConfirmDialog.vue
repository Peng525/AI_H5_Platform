<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/40"
        @click.self="$emit('cancel')"
      >
        <div
          class="bg-white rounded-xl shadow-elevated border border-outline-variant w-full max-w-sm overflow-hidden"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="titleId"
        >
          <div class="p-6">
            <div class="flex items-start gap-3">
              <div
                class="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
                :class="danger ? 'bg-red-50 text-red-600' : 'bg-primary/10 text-primary'"
              >
                <span class="material-symbols-outlined">{{ danger ? 'delete_forever' : 'help' }}</span>
              </div>
              <div class="min-w-0">
                <h2 :id="titleId" class="font-semibold text-on-surface">{{ title }}</h2>
                <p class="text-sm text-on-surface-variant mt-2 leading-relaxed">{{ message }}</p>
              </div>
            </div>
          </div>
          <div class="flex gap-3 px-6 py-4 bg-surface-container-low border-t border-outline-variant">
            <button
              type="button"
              class="flex-1 py-2.5 rounded-lg border border-outline-variant text-sm font-medium hover:bg-white transition"
              @click="$emit('cancel')"
            >
              {{ cancelText }}
            </button>
            <button
              type="button"
              class="flex-1 py-2.5 rounded-lg text-sm font-medium text-white transition disabled:opacity-50"
              :class="danger ? 'bg-red-600 hover:bg-red-700' : 'bg-primary hover:bg-primary-container'"
              :disabled="loading"
              @click="$emit('confirm')"
            >
              {{ loading ? '处理中…' : confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { useId } from 'vue'

defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '确认操作' },
  message: { type: String, default: '确定要继续吗？' },
  confirmText: { type: String, default: '确定' },
  cancelText: { type: String, default: '取消' },
  danger: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
})

defineEmits(['confirm', 'cancel'])

const titleId = useId()
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
