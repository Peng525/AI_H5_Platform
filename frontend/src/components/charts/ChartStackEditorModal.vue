<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="open" class="fixed inset-0 z-[200] bg-surface-container-low flex flex-col">
        <header class="shrink-0 flex items-center justify-between px-4 py-3 border-b border-outline-variant bg-white">
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">{{ mode === 'chartStack' ? 'stacked_bar_chart' : 'bar_chart' }}</span>
            <h1 class="text-lg font-bold">{{ mode === 'chartStack' ? '图表卡组' : '编辑图表' }}</h1>
          </div>
          <div class="flex items-center gap-2">
            <button
              type="button"
              class="px-3 py-1.5 text-sm bg-primary text-on-primary rounded-lg font-medium"
              @click="onSave"
            >
              保存
            </button>
            <button type="button" class="p-2 rounded-lg hover:bg-surface-container" @click="$emit('close')">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
        </header>

        <div class="flex-1 min-h-0 overflow-y-auto bg-surface-container-low max-w-lg mx-auto w-full">
          <ChartEditorPanel
            ref="panelRef"
            :mode="mode"
            :initial-content="initialContent"
            @save="$emit('save', $event)"
          />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import ChartEditorPanel from './ChartEditorPanel.vue'

defineProps({
  open: { type: Boolean, default: false },
  mode: { type: String, default: 'chartStack' },
  initialContent: { type: Object, default: null },
})

defineEmits(['close', 'save'])

const panelRef = ref(null)

function onSave() {
  panelRef.value?.save()
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
