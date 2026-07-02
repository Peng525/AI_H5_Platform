<template>
  <div
    class="relative flex flex-col h-full min-h-0 border-r border-outline-variant bg-white transition-[width]"
    :class="collapsed ? 'lg:w-12' : 'lg:w-[320px]'"
  >
    <button
      type="button"
      class="hidden lg:flex absolute -right-3 top-3 z-10 w-6 h-6 items-center justify-center rounded-full border border-outline-variant bg-white shadow-sm text-on-surface-variant hover:bg-surface-container-low"
      :title="collapsed ? '展开 AI 助手' : '收起 AI 助手'"
      @click="toggle"
    >
      <span class="material-symbols-outlined text-[16px]">
        {{ collapsed ? 'chevron_right' : 'chevron_left' }}
      </span>
    </button>
    <ResumeChatPanel
      v-show="!collapsed"
      class="flex-1 min-h-0"
      :messages="messages"
      :generating="generating"
      @submit="$emit('submit', $event)"
    />
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
