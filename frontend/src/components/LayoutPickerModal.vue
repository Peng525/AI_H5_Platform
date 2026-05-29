<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/40"
        @click.self="$emit('close')"
      >
        <div class="bg-white rounded-xl shadow-elevated border border-outline-variant w-full max-w-md overflow-hidden" role="dialog">
          <div class="p-5 border-b border-outline-variant">
            <h2 class="font-semibold">选择页面版式</h2>
            <p class="text-sm text-on-surface-variant mt-1">套用后将替换当前页画布内容（可 Ctrl+Z 撤销）。</p>
          </div>
          <div class="p-4 grid grid-cols-2 gap-2 max-h-64 overflow-y-auto">
            <button
              v-for="item in blocks"
              :key="item.id"
              type="button"
              class="text-left px-3 py-2 rounded-lg border text-xs transition"
              :class="selected === item.id ? 'border-primary bg-primary/5 text-primary font-medium' : 'border-outline-variant hover:bg-surface-container-low'"
              @click="selected = item.id"
            >
              <span class="material-symbols-outlined text-[16px] align-middle mr-1">{{ item.icon }}</span>
              {{ item.label }}
            </button>
          </div>
          <div class="flex gap-3 px-5 py-4 bg-surface-container-low border-t border-outline-variant">
            <button
              type="button"
              class="flex-1 py-2.5 rounded-lg border border-outline-variant text-sm font-medium hover:bg-white"
              @click="onBlank"
            >
              空白页
            </button>
            <button
              type="button"
              class="flex-1 py-2.5 rounded-lg bg-primary text-on-primary text-sm font-medium"
              @click="onConfirm"
            >
              套用版式
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { BUSINESS_LAYOUT_BLOCKS, STORY_LAYOUT_BLOCKS } from '../constants/layoutBlocks.js'

const props = defineProps({
  open: { type: Boolean, default: false },
  blocks: { type: Array, default: null },
})

const emit = defineEmits(['close', 'pick', 'blank'])

const selected = ref('cover-minimal')
const blocks = computed(() => {
  if (props.blocks?.length) return props.blocks
  return [...BUSINESS_LAYOUT_BLOCKS, ...STORY_LAYOUT_BLOCKS]
})

watch(
  () => props.open,
  (v) => {
    if (v) selected.value = 'cover-minimal'
  }
)

function onConfirm() {
  emit('pick', selected.value)
  emit('close')
}

function onBlank() {
  emit('blank')
  emit('close')
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
