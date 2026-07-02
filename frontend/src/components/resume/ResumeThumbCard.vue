<template>
  <router-link
    :to="`/create/generate/resume/${item.public_id}`"
    class="bg-white rounded-xl border shadow-card overflow-hidden hover:border-primary/40 transition block"
  >
    <div class="aspect-[3/4] bg-surface-container-low flex items-center justify-center">
      <span class="material-symbols-outlined text-4xl text-on-surface-variant/40">description</span>
    </div>
    <div class="p-3">
      <p class="font-medium text-sm truncate">{{ item.title }}</p>
      <p class="text-xs text-on-surface-variant mt-1">{{ formatDate(item.updated_at) }}</p>
    </div>
  </router-link>
</template>

<script setup>
defineProps({
  item: { type: Object, required: true },
})

function formatDate(iso) {
  if (!iso) return ''
  try {
    return new Date(iso).toLocaleDateString('zh-CN')
  } catch {
    return ''
  }
}
</script>
