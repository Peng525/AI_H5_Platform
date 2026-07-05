<template>
  <div
    v-if="visible"
    class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-10 w-max max-w-[16rem]"
  >
    <div class="relative bg-slate-900 text-white text-xs rounded-lg px-3 py-2 shadow-lg">
      生成前请先选择简历模板
      <button
        type="button"
        class="ml-2 text-white/80 hover:text-white underline"
        @click="dismiss"
      >
        知道了
      </button>
      <span class="absolute left-1/2 -translate-x-1/2 -bottom-1.5 w-3 h-3 bg-slate-900 rotate-45" />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const STORAGE_KEY = 'resume_generate_template_hint_seen'

const visible = ref(false)

onMounted(() => {
  try {
    visible.value = !localStorage.getItem(STORAGE_KEY)
  } catch {
    visible.value = true
  }
})

function dismiss() {
  visible.value = false
  try {
    localStorage.setItem(STORAGE_KEY, '1')
  } catch {
    /* ignore */
  }
}

defineExpose({
  dismissAfterGenerate: dismiss,
})
</script>
