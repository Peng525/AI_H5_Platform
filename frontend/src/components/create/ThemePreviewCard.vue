<template>
  <button
    type="button"
    class="relative w-full text-left rounded-xl border-2 overflow-hidden transition-all disabled:opacity-50"
    :class="
      selected
        ? 'border-primary ring-2 ring-primary/30'
        : 'border-outline-variant/50 hover:border-outline-variant'
    "
    :disabled="disabled"
    @click="$emit('select', preview.id)"
  >
    <div
      class="aspect-[4/3] p-3 flex flex-col justify-center gap-1.5"
      :style="{ background: preview.backgroundCss }"
    >
      <p
        class="text-sm font-bold leading-tight truncate"
        :style="{ fontFamily: preview.titleFont, color: preview.titleColor }"
      >
        Title
      </p>
      <p
        class="text-xs leading-snug"
        :style="{ fontFamily: preview.bodyFont, color: preview.bodyColor }"
      >
        Body &amp;
        <span :style="{ color: preview.linkColor }">link</span>
      </p>
    </div>
    <div class="px-2 py-1.5 bg-white border-t border-outline-variant/40 flex items-center justify-between gap-1">
      <span class="text-xs text-on-surface truncate">{{ preview.label }}</span>
      <span
        v-if="selected"
        class="material-symbols-outlined text-primary text-[18px] shrink-0"
        aria-hidden="true"
      >
        check_circle
      </span>
    </div>
  </button>
</template>

<script setup>
defineProps({
  preview: { type: Object, required: true },
  selected: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
})

defineEmits(['select'])
</script>
