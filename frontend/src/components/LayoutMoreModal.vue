<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/40"
        @click.self="$emit('close')"
      >
        <div
          class="bg-white rounded-xl shadow-elevated border border-outline-variant w-full max-w-sm overflow-hidden"
          role="dialog"
          aria-labelledby="layout-more-title"
        >
          <div class="p-4 border-b border-outline-variant flex items-center justify-between gap-2">
            <div>
              <h2 id="layout-more-title" class="font-semibold text-sm">更多版式</h2>
              <p class="text-xs text-on-surface-variant mt-0.5">商务与叙事版式</p>
            </div>
            <button
              type="button"
              class="p-1 rounded-lg hover:bg-surface-container-low text-on-surface-variant"
              aria-label="关闭"
              @click="$emit('close')"
            >
              <span class="material-symbols-outlined text-[20px]">close</span>
            </button>
          </div>
          <div class="p-3 grid grid-cols-3 gap-2 max-h-[min(60vh,20rem)] overflow-y-auto">
            <button
              v-for="item in blocks"
              :key="item.id"
              type="button"
              class="flex flex-col items-center gap-1 p-2 rounded-lg border border-outline-variant bg-white hover:border-primary hover:bg-[#f8fbff] transition-colors"
              @click="onPick(item.id)"
            >
              <span class="material-symbols-outlined text-xl text-primary">{{ item.icon }}</span>
              <span class="text-[10px] font-medium text-on-surface text-center leading-tight">{{ item.label }}</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { getMoreLayoutBlocks } from '../constants/layoutBlocks.js'

defineProps({
  open: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'pick'])

const blocks = getMoreLayoutBlocks()

function onPick(id) {
  emit('pick', id)
  emit('close')
}
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
