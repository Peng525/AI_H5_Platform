<template>
  <div class="flex flex-col items-center justify-center py-10 px-4 text-center">
    <span v-if="icon" class="material-symbols-outlined text-4xl text-on-surface-variant/50 mb-3">{{ icon }}</span>
    <p class="text-sm font-medium text-on-surface">{{ title }}</p>
    <p v-if="description" class="text-xs text-on-surface-variant mt-1 max-w-sm">{{ description }}</p>
    <button
      v-if="actionLabel"
      type="button"
      class="mt-4 px-4 py-2 text-sm rounded-lg bg-primary text-on-primary font-medium"
      @click="$emit('action')"
    >
      {{ actionLabel }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: 'inbox' },
  title: { type: String, default: '暂无内容' },
  description: { type: String, default: '' },
  actionLabel: { type: String, default: '' },
})
defineEmits(['action'])
</script>
