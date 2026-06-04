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
          <h2 class="text-sm font-semibold">AI 生图</h2>
          <button type="button" class="p-1.5 rounded-lg hover:bg-surface-container-low" @click="$emit('close')">
            <span class="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>
        <div class="flex-1 min-h-0 overflow-hidden">
          <AiPanel
            ref="panelRef"
            :image-loading="imageLoading"
            :quota-remaining="quotaRemaining"
            :quota-total="quotaTotal"
            :canvas-viewport-id="canvasViewportId"
            class="result-ai-panel !w-full !max-w-none !border-0 !h-full"
            @generate-image="$emit('generate-image', $event)"
            @add-image-to-page="$emit('add-image-to-page', $event); $emit('close')"
          />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import AiPanel from '../AiPanel.vue'

defineProps({
  open: { type: Boolean, default: false },
  imageLoading: { type: Boolean, default: false },
  quotaRemaining: { type: Number, default: 0 },
  quotaTotal: { type: Number, default: 0 },
  canvasViewportId: { type: String, default: 'mobile-375' },
})

defineEmits(['close', 'generate-image', 'add-image-to-page'])

const panelRef = ref(null)

function setGeneratedImage(result) {
  panelRef.value?.setGeneratedImage(result)
}

function setImageError(msg) {
  panelRef.value?.setImageError(msg)
}

defineExpose({ setGeneratedImage, setImageError })
</script>

<style scoped>
:deep(.editor-ai-panel) {
  width: 100%;
  max-width: none;
  border: none;
  height: 100%;
}
</style>
