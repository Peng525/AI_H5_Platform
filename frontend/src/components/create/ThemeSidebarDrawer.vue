<template>
  <Teleport to="body">
    <Transition name="theme-drawer">
      <aside
        v-if="open"
        class="fixed right-0 top-14 bottom-0 z-[90] w-[min(100vw,360px)] bg-[#1e1e24] text-white shadow-2xl flex flex-col border-l border-white/10"
        role="dialog"
        aria-modal="true"
        aria-labelledby="theme-sidebar-title"
      >
        <div class="flex items-center justify-between px-4 py-3 border-b border-white/10 shrink-0">
          <h2 id="theme-sidebar-title" class="text-base font-semibold">演示主题</h2>
          <button
            type="button"
            class="p-1.5 rounded-lg hover:bg-white/10"
            aria-label="关闭"
            @click="$emit('close')"
          >
            <span class="material-symbols-outlined text-[22px]">close</span>
          </button>
        </div>
        <div class="flex-1 min-h-0 overflow-y-auto p-3">
          <div class="grid grid-cols-2 gap-3">
            <ThemePreviewCard
              v-for="preview in previews"
              :key="preview.id"
              :preview="preview"
              :selected="preview.id === activeThemeId"
              :disabled="disabled"
              @select="onSelect"
            />
          </div>
        </div>
      </aside>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import ThemePreviewCard from './ThemePreviewCard.vue'
import { listThemeOptions } from '../../utils/applyProjectTheme.js'

defineProps({
  open: { type: Boolean, default: false },
  activeThemeId: { type: String, default: 'zjy-minimal' },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'select'])

const previews = computed(() => listThemeOptions())

function onSelect(themeId) {
  emit('select', themeId)
}
</script>

<style scoped>
.theme-drawer-enter-active,
.theme-drawer-leave-active {
  transition: transform 0.22s ease, opacity 0.22s ease;
}
.theme-drawer-enter-from,
.theme-drawer-leave-to {
  transform: translateX(100%);
  opacity: 0.6;
}
</style>
