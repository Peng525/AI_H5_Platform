<template>
  <div ref="rootRef" class="relative">
    <button
      type="button"
      class="preview-select-trigger flex items-center gap-1.5 min-w-[108px] max-w-[160px]"
      @click="open = !open"
    >
      <span class="truncate flex-1 text-left">{{ currentLabel }}</span>
      <span class="material-symbols-outlined text-[16px] shrink-0 opacity-80">expand_more</span>
    </button>
    <div v-if="open" class="preview-select-menu">
      <button
        v-for="opt in options"
        :key="opt.value"
        type="button"
        class="preview-select-option"
        :class="modelValue === opt.value ? 'is-active' : ''"
        @click="pick(opt.value)"
      >
        {{ opt.label }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'

const props = defineProps({
  modelValue: { type: String, required: true },
  options: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue', 'change'])

const open = ref(false)
const rootRef = ref(null)

const currentLabel = computed(() => props.options.find((o) => o.value === props.modelValue)?.label || '')

function pick(value) {
  emit('update:modelValue', value)
  emit('change', value)
  open.value = false
}

function onClickOutside(e) {
  if (rootRef.value && !rootRef.value.contains(e.target)) open.value = false
}

onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>

<style scoped>
.preview-select-trigger {
  font-size: 14px;
  line-height: 1.35;
  font-weight: 600;
  color: #fff;
  background: rgba(20, 24, 32, 0.96);
  border: 1px solid rgba(255, 255, 255, 0.35);
  border-radius: 8px;
  padding: 9px 12px;
  backdrop-filter: blur(8px);
}
.preview-select-menu {
  position: absolute;
  right: 0;
  top: calc(100% + 6px);
  min-width: 100%;
  max-height: 280px;
  overflow-y: auto;
  background: #141820;
  border: 1px solid rgba(255, 255, 255, 0.28);
  border-radius: 10px;
  padding: 6px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.55);
  z-index: 30;
}
.preview-select-option {
  display: block;
  width: 100%;
  text-align: left;
  font-size: 14px;
  line-height: 1.4;
  font-weight: 600;
  color: #f9fafb;
  padding: 10px 12px;
  border-radius: 6px;
  white-space: nowrap;
}
.preview-select-option:hover {
  background: rgba(255, 255, 255, 0.08);
}
.preview-select-option.is-active {
  background: #005daa;
  color: #fff;
}
</style>
