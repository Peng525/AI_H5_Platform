<template>
  <div
    data-slide-insert
    class="flex w-full justify-center items-center"
    @mousedown.stop
    @click.stop
  >
    <div class="inline-flex items-center gap-2">
      <button
        type="button"
        title="添加空白页"
        class="group w-9 h-9 rounded-lg border border-dashed border-outline-variant/70 bg-white hover:border-primary/50 hover:bg-surface-container-lowest transition-colors flex items-center justify-center shrink-0 shadow-sm"
        @click="$emit('add-blank')"
      >
        <span class="material-symbols-outlined text-[20px] text-on-surface-variant group-hover:text-primary transition-colors">add</span>
      </button>
      <button
        type="button"
        title="AI 生成卡片"
        class="group w-9 h-9 rounded-lg border border-dashed border-outline-variant/70 bg-white hover:border-primary/50 hover:bg-surface-container-lowest transition-colors flex items-center justify-center shrink-0 shadow-sm"
        @click="$emit('open-generate')"
      >
        <span class="material-symbols-outlined text-[20px] text-on-surface-variant group-hover:text-primary transition-colors">auto_awesome</span>
      </button>
    </div>
  </div>
</template>

<script setup>
defineEmits(['add-blank', 'open-generate'])
</script>
