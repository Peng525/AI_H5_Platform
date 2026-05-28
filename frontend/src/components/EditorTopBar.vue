<template>
  <header
    class="h-16 border-b border-outline-variant bg-surface flex items-center justify-between px-6 shrink-0 z-50"
  >
    <div class="flex items-center gap-4 min-w-0">
      <router-link to="/templates" class="text-lg font-bold text-primary shrink-0">AI智能H5演示平台</router-link>
      <span class="hidden md:block h-5 w-px bg-outline-variant" />
      <span class="truncate text-sm font-medium text-on-surface">{{ projectTitle }}</span>
    </div>
    <div class="flex items-center gap-2 shrink-0">
      <router-link
        v-if="projectId"
        :to="`/preview/${projectId}`"
        class="px-4 py-2 rounded-lg border border-outline-variant text-sm hover:bg-surface-container-high"
      >
        预览
      </router-link>
      <router-link
        v-if="projectId"
        :to="`/publish/${projectId}`"
        class="px-4 py-2 rounded-lg bg-primary text-on-primary text-sm font-medium shadow-card flex items-center gap-1"
      >
        <span class="material-symbols-outlined text-[18px]">ios_share</span>
        导出/分享
      </router-link>
    </div>
  </header>
</template>

<script setup>
defineProps({
  projectTitle: { type: String, default: '未命名调研报告' },
  projectId: { type: [String, Number], default: null },
})
</script>
