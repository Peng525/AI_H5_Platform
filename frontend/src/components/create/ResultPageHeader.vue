<template>
  <header class="h-14 border-b border-outline-variant bg-white px-4 sm:px-6 shrink-0 flex items-center gap-3">
    <CreateHomeButton />

    <button
      type="button"
      class="inline-flex items-center gap-1 text-sm text-on-surface-variant hover:text-primary shrink-0 whitespace-nowrap ml-2.5"
      @click="$emit('back-to-review')"
    >
      <span class="material-symbols-outlined text-[14px]">arrow_back</span>
      <span class="hidden sm:inline text-[14px]">返回提示词编辑器</span>
      <span class="sm:hidden">编辑器</span>
    </button>

    <div class="inline-grid max-w-[min(48rem,calc(100vw-22rem))] min-w-0">
      <span
        class="invisible whitespace-pre col-start-1 row-start-1 px-2 py-1 text-sm font-semibold min-w-[8rem]"
        aria-hidden="true"
      >{{ title || '无标题' }}</span>
      <input
        :value="title"
        type="text"
        class="col-start-1 row-start-1 w-full min-w-[8rem] border border-transparent hover:border-outline-variant focus:border-primary/40 rounded-lg px-2 py-1 text-sm font-semibold bg-transparent focus:outline-none focus:ring-1 focus:ring-primary/30"
        placeholder="无标题"
        @input="$emit('update:title', $event.target.value)"
        @blur="$emit('save-title')"
        @keydown.enter="$event.target.blur()"
      />
    </div>

    <div class="flex-1 min-w-0" aria-hidden="true" />

    <div class="flex items-center gap-2 shrink-0">
      <button
        type="button"
        class="px-3 py-1.5 rounded-lg border text-sm font-medium inline-flex items-center gap-1.5 transition-colors disabled:opacity-50"
        :class="
          themeDrawerOpen
            ? 'border-primary bg-primary/8 text-primary'
            : 'border-outline-variant bg-white text-on-surface hover:border-primary/40'
        "
        :disabled="!projectId || projectId === '_pending'"
        @click="$emit('open-theme')"
      >
        <span class="material-symbols-outlined text-[18px]">format_paint</span>
        <span class="hidden sm:inline">主题</span>
      </button>
      <button
        type="button"
        class="px-3 py-1.5 rounded-lg bg-primary text-on-primary text-sm font-medium inline-flex items-center gap-1.5 disabled:opacity-50"
        :disabled="!projectId || projectId === '_pending'"
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
import CreateHomeButton from './CreateHomeButton.vue'
import UserMenu from './UserMenu.vue'

defineProps({
  title: { type: String, default: '' },
  projectId: { type: [Number, String], default: null },
  themeDrawerOpen: { type: Boolean, default: false },
})

defineEmits(['update:title', 'save-title', 'present', 'open-theme', 'back-to-review'])
</script>
