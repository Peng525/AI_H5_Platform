<template>
  <header class="h-14 border-b border-outline-variant bg-white flex items-center justify-between px-4 sm:px-6 shrink-0 gap-3">
    <div class="flex items-center gap-3 min-w-0 flex-1">
      <nav class="hidden sm:flex items-center gap-1 text-xs sm:text-sm text-on-surface-variant shrink-0">
        <router-link to="/create/generate" class="hover:text-primary whitespace-nowrap">生成</router-link>
        <span class="opacity-40">/</span>
        <router-link to="/create/generate/review" class="hover:text-primary whitespace-nowrap">提示编辑器</router-link>
        <span class="opacity-40">/</span>
        <span class="text-on-surface font-medium whitespace-nowrap">生成结果</span>
      </nav>
      <input
        :value="title"
        type="text"
        class="min-w-0 flex-1 max-w-md border border-transparent hover:border-outline-variant focus:border-primary/40 rounded-lg px-2 py-1 text-sm font-semibold bg-transparent focus:outline-none focus:ring-1 focus:ring-primary/30"
        placeholder="无标题"
        @input="$emit('update:title', $event.target.value)"
        @blur="$emit('save-title')"
        @keydown.enter="$event.target.blur()"
      />
    </div>
    <div class="flex items-center gap-2 shrink-0">
      <slot name="meta" />
      <button
        type="button"
        class="px-3 py-1.5 rounded-lg bg-primary text-on-primary text-sm font-medium inline-flex items-center gap-1.5 disabled:opacity-50"
        :disabled="!projectId"
        @click="$emit('present')"
      >
        <span class="material-symbols-outlined text-[18px]">play_arrow</span>
        <span class="hidden sm:inline">演示</span>
      </button>
      <UserMenu />
    </div>
  </header>
</template>

<script setup>
import UserMenu from './UserMenu.vue'

defineProps({
  title: { type: String, default: '' },
  projectId: { type: [Number, String], default: null },
})

defineEmits(['update:title', 'save-title', 'present'])
</script>
