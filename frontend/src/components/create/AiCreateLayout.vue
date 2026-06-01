<template>
  <div class="min-h-screen bg-gradient-to-br from-sky-50 via-blue-50/80 to-indigo-50 flex flex-col">
    <header class="h-14 border-b border-white/60 bg-white/70 backdrop-blur flex items-center justify-between px-4 sm:px-8 shrink-0">
      <div class="flex items-center gap-2 min-w-0">
        <button
          v-if="showBack"
          type="button"
          class="inline-flex items-center gap-1 text-sm text-on-surface-variant hover:text-primary shrink-0"
          @click="$emit('back')"
        >
          <span class="material-symbols-outlined text-[18px]">arrow_back</span>
          {{ backLabel }}
        </button>
        <router-link
          v-else
          to="/dashboard"
          class="inline-flex items-center gap-1 text-sm text-on-surface-variant hover:text-primary shrink-0"
        >
          <span class="material-symbols-outlined text-[18px]">arrow_back</span>
          返回工作台
        </router-link>
      </div>
      <span
        v-if="quotaText"
        class="text-xs text-on-surface-variant bg-white/80 border border-outline-variant/60 px-2.5 py-1 rounded-full"
      >
        配额 {{ quotaText }}
      </span>
    </header>
    <main class="flex-1 overflow-y-auto">
      <div class="max-w-5xl mx-auto px-4 sm:px-8 py-8 sm:py-12 w-full">
        <slot />
      </div>
    </main>
    <footer v-if="$slots.footer" class="shrink-0 border-t border-white/60 bg-white/70 backdrop-blur px-4 sm:px-8 py-4">
      <div class="max-w-5xl mx-auto w-full">
        <slot name="footer" />
      </div>
    </footer>
  </div>
</template>

<script setup>
defineProps({
  showBack: { type: Boolean, default: false },
  backLabel: { type: String, default: '上一步' },
  quotaText: { type: String, default: '' },
})

defineEmits(['back'])
</script>
