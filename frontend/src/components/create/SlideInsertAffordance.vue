<template>
  <div
    v-if="visible"
    data-slide-insert
    class="flex justify-center py-2 -mt-1"
    @mousedown.stop
    @click.stop
  >
    <div ref="menuRef" class="relative">
      <button
        type="button"
        class="w-9 h-9 rounded-full border-2 border-dashed border-outline-variant/80 bg-white shadow-sm flex items-center justify-center text-on-surface-variant hover:border-primary hover:text-primary hover:bg-primary/5 transition-colors"
        title="添加页面"
        @click.stop="menuOpen = !menuOpen"
      >
        <span class="material-symbols-outlined text-[20px]">add</span>
      </button>
      <div
        v-show="menuOpen"
        class="absolute left-1/2 -translate-x-1/2 top-full mt-2 w-44 bg-white border border-outline-variant rounded-xl shadow-lg py-1 z-[60]"
        @click.stop
      >
        <button
          type="button"
          class="w-full text-left px-3 py-2.5 text-sm hover:bg-surface-container-low flex items-center gap-2"
          @click="pick('blank')"
        >
          <span class="material-symbols-outlined text-[18px] text-primary">note_add</span>
          添加空白页
        </button>
        <button
          type="button"
          class="w-full text-left px-3 py-2.5 text-sm hover:bg-surface-container-low flex items-center gap-2"
          @click="pick('ai')"
        >
          <span class="material-symbols-outlined text-[18px] text-primary">auto_awesome</span>
          AI 生成卡片
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

defineProps({
  visible: { type: Boolean, default: false },
})

const emit = defineEmits(['add-blank', 'open-generate'])

const menuOpen = ref(false)
const menuRef = ref(null)

function pick(action) {
  menuOpen.value = false
  if (action === 'blank') emit('add-blank')
  else emit('open-generate')
}

function onDocPointerDown(e) {
  if (!menuOpen.value) return
  if (menuRef.value?.contains(e.target)) return
  menuOpen.value = false
}

onMounted(() => document.addEventListener('mousedown', onDocPointerDown))
onUnmounted(() => document.removeEventListener('mousedown', onDocPointerDown))
</script>
