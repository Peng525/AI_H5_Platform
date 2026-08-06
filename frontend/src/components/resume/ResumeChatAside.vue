<template>
  <div
    class="relative flex flex-col h-full min-h-0 w-full min-w-0 border-r border-outline-variant bg-white overflow-hidden"
  >
    <button
      type="button"
      class="hidden lg:flex absolute top-1/2 -translate-y-1/2 -right-3 z-30 w-6 h-6 items-center justify-center rounded-full border border-outline-variant bg-white shadow-sm text-on-surface-variant hover:bg-surface-container-low pointer-events-auto transition-transform duration-200"
      :title="collapsed ? '展开 AI 助手' : '收起 AI 助手'"
      @click.stop="toggle"
    >
      <span
        class="material-symbols-outlined text-[16px] transition-transform duration-200"
        :class="collapsed ? 'rotate-0' : 'rotate-0'"
      >
        {{ collapsed ? 'chevron_right' : 'chevron_left' }}
      </span>
    </button>
    <Transition name="chat-panel-fade">
      <ResumeChatPanel
        v-if="!collapsed"
        class="flex-1 min-h-0"
        :messages="messages"
        :generating="generating"
        @submit="$emit('submit', $event)"
      />
    </Transition>
    <Transition name="chat-panel-fade">
      <div
        v-if="collapsed"
        class="hidden lg:flex flex-1 flex-col items-center justify-start py-3"
      >
        <button
          type="button"
          class="w-9 h-9 rounded-lg hover:bg-surface-container-high flex items-center justify-center"
          title="展开 AI 助手"
          @click="toggle"
        >
          <span class="material-symbols-outlined text-[20px]">forum</span>
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import ResumeChatPanel from './ResumeChatPanel.vue'

const props = defineProps({
  messages: { type: Array, default: () => [] },
  generating: { type: Boolean, default: false },
  collapsed: { type: Boolean, default: false },
})

const emit = defineEmits(['submit', 'update:collapsed'])

function toggle() {
  emit('update:collapsed', !props.collapsed)
}
</script>

<style scoped>
.chat-panel-fade-enter-active,
.chat-panel-fade-leave-active {
  transition: opacity 200ms ease;
}

.chat-panel-fade-enter-from,
.chat-panel-fade-leave-to {
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .chat-panel-fade-enter-active,
  .chat-panel-fade-leave-active {
    transition: none;
  }
}
</style>
