<template>
  <div class="min-h-screen bg-gradient-to-b from-sky-100/50 via-white to-sky-50/80 flex flex-col">
    <AiCreateHeader
      :variant="headerVariant"
      :show-back="showBack"
      :back-label="backLabel"
      @back="$emit('back')"
    />
    <main class="flex-1 min-h-0 flex flex-col" :class="fillHeight ? 'overflow-hidden' : 'overflow-y-auto'">
      <div
        class="max-w-5xl mx-auto px-4 sm:px-8 w-full"
        :class="fillHeight ? 'flex-1 flex flex-col min-h-0 py-4 sm:py-5' : 'py-8 sm:py-12'"
      >
        <p v-if="headerVariant === 'entry'" class="sm:hidden text-center text-sm font-semibold text-on-surface mb-4 shrink-0">
          欢迎来到 AI H5 平台
        </p>
        <slot />
      </div>
    </main>
    <footer v-if="$slots.footer" class="shrink-0 border-t border-outline-variant bg-white px-4 sm:px-8 py-4">
      <div class="max-w-5xl mx-auto w-full">
        <slot name="footer" />
      </div>
    </footer>
  </div>
</template>

<script setup>
import AiCreateHeader from './AiCreateHeader.vue'

defineProps({
  headerVariant: { type: String, default: 'step', validator: (v) => ['entry', 'step'].includes(v) },
  showBack: { type: Boolean, default: false },
  backLabel: { type: String, default: '上一步' },
  fillHeight: { type: Boolean, default: false },
})

defineEmits(['back'])
</script>
