<template>
  <div
    class="rounded-xl border bg-white shadow-sm overflow-hidden transition-colors flex flex-col w-full h-full"
    :class="selected ? 'border-primary ring-1 ring-primary/20' : 'border-outline-variant/50 hover:border-primary/30'"
  >
    <button type="button" class="flex flex-col flex-1 text-left p-2.5 h-full min-h-[11rem]" @click="$emit('select')">
      <div
        class="aspect-[4/3] w-full rounded-lg bg-surface-container-low/80 border border-outline-variant/40 overflow-hidden shrink-0 mb-2 flex items-center justify-center"
      >
        <img
          v-if="previewUrl"
          :src="previewUrl"
          :alt="title"
          class="w-full h-full object-cover"
        />
        <div v-else class="flex flex-col items-center gap-1 text-on-surface-variant/50">
          <span class="material-symbols-outlined text-[28px]">image</span>
          <span class="text-[10px]">预览图</span>
        </div>
      </div>
      <div class="flex items-start justify-between gap-1.5 shrink-0">
        <div class="min-w-0">
          <p class="text-sm font-medium text-on-surface leading-snug">{{ title }}</p>
          <p v-if="description" class="text-[11px] text-on-surface-variant mt-0.5 line-clamp-2">{{ description }}</p>
        </div>
        <span
          v-if="selected"
          class="material-symbols-outlined text-primary text-base shrink-0"
        >check_circle</span>
      </div>
      <div class="mt-2 flex-1 min-h-0 overflow-y-auto">
        <table class="w-full text-[11px] text-on-surface-variant border-collapse">
          <tbody>
            <tr v-for="field in fields" :key="field.label" class="align-top">
              <td class="pr-1.5 py-0.5 whitespace-nowrap text-on-surface/70 w-8">{{ field.label }}</td>
              <td class="py-0.5 leading-snug">{{ field.value }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </button>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
  fields: { type: Array, default: () => [] },
  previewUrl: { type: String, default: '' },
  selected: { type: Boolean, default: false },
})

defineEmits(['select'])
</script>
