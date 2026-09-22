<template>
  <footer class="shrink-0 border-t border-outline-variant bg-white py-3 px-4 sm:px-6">
    <div class="flex flex-wrap items-center justify-center gap-3">
      <button
        type="button"
        class="px-5 py-2.5 rounded-lg bg-primary text-on-primary text-sm font-medium inline-flex items-center gap-2 disabled:opacity-60 disabled:cursor-wait"
        :disabled="saving"
        :aria-busy="saving"
        @click="$emit('save')"
      >
        <span class="material-symbols-outlined text-[18px]">save</span>
        {{ saving ? '保存中…' : '保存为草稿' }}
      </button>
      <button
        type="button"
        class="px-5 py-2.5 rounded-lg border border-outline-variant text-sm font-medium hover:bg-surface-container-low"
        @click="$emit('regenerate')"
      >
        再生成一次
      </button>
    </div>
    <p
      v-if="message"
      class="text-xs text-center mt-2"
      :class="error ? 'text-red-600' : 'text-on-surface-variant'"
    >
      {{ message }}
    </p>
  </footer>
</template>

<script setup>
defineProps({
  saving: { type: Boolean, default: false },
  message: { type: String, default: '' },
  error: { type: Boolean, default: false },
})

defineEmits(['save', 'regenerate'])
</script>
