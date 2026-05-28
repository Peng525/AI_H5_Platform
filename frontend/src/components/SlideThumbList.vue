<template>
  <div class="p-3 flex flex-col gap-2">
    <div class="flex items-center justify-between mb-1">
      <span class="text-xs font-semibold text-on-surface-variant">页面列表</span>
      <button class="text-primary hover:bg-primary/10 rounded p-1" title="新增页面" @click="$emit('add')">
        <span class="material-symbols-outlined text-[16px]">add</span>
      </button>
    </div>

    <div
      v-for="(s, i) in slides"
      :key="s.id"
      class="group relative rounded-lg border overflow-hidden cursor-pointer transition-shadow"
      :class="currentId === s.id ? 'border-2 border-primary shadow-card' : 'border-outline-variant hover:border-outline'"
      @click="$emit('select', s)"
    >
      <div class="h-20 bg-surface-container-lowest flex items-center justify-center p-2">
        <div class="w-full h-full bg-white border border-outline-variant/50 rounded flex flex-col gap-1 p-1">
          <div class="w-full h-2 bg-primary/20 rounded-sm" />
          <div class="w-2/3 h-2 bg-surface-container rounded-sm" />
          <div class="w-1/2 h-2 bg-secondary/30 rounded-sm self-end" />
        </div>
      </div>
      <div
        class="absolute top-1 left-1 text-[10px] px-1.5 py-0.5 rounded font-bold shadow-sm"
        :class="currentId === s.id ? 'bg-primary text-on-primary' : 'bg-surface-variant text-on-surface-variant'"
      >
        {{ i + 1 }}
      </div>
      <div class="p-1.5 text-center border-t border-outline-variant text-xs truncate" :class="currentId === s.id ? 'text-primary font-medium' : 'text-on-surface-variant'">
        {{ s.title || '未命名' }}
      </div>
      <button
        v-if="slides.length > 1"
        class="absolute top-1 right-1 opacity-0 group-hover:opacity-100 p-0.5 bg-red-50 text-red-600 rounded"
        title="删除页面"
        @click.stop="$emit('remove', s.id)"
      >
        <span class="material-symbols-outlined text-[14px]">close</span>
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  slides: { type: Array, default: () => [] },
  currentId: { type: Number, default: null },
})

defineEmits(['select', 'add', 'remove'])
</script>
