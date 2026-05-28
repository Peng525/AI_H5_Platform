<template>
  <div class="p-4 space-y-5 text-sm">
    <section>
      <h3 class="text-xs font-semibold text-on-surface-variant mb-2 flex items-center gap-1">
        <span class="material-symbols-outlined text-[16px]">animation</span>
        页面切换动效
      </h3>
      <p class="text-[11px] text-on-surface-variant mb-2">应用于预览与分享时的翻页过渡</p>
      <div class="grid grid-cols-2 gap-2">
        <button
          v-for="a in PAGE_ANIMATIONS"
          :key="a.id"
          class="flex items-center gap-2 px-2 py-2 rounded-lg border text-left text-xs transition"
          :class="animation === a.id ? 'border-primary bg-primary/5 text-primary font-medium' : 'border-outline-variant hover:border-outline'"
          @click="pickAnimation(a.id)"
        >
          <span class="material-symbols-outlined text-[16px]">{{ a.icon }}</span>
          {{ a.label }}
        </button>
      </div>
    </section>

    <section>
      <h3 class="text-xs font-semibold text-on-surface-variant mb-2 flex items-center gap-1">
        <span class="material-symbols-outlined text-[16px]">swap_vert</span>
        浏览滚动效果
      </h3>
      <p class="text-[11px] text-on-surface-variant mb-2">全局演示浏览方式（预览时生效）</p>
      <div class="space-y-2">
        <button
          v-for="s in SCROLL_EFFECTS"
          :key="s.id"
          class="w-full text-left px-3 py-2 rounded-lg border transition"
          :class="scrollEffect === s.id ? 'border-primary bg-primary/5' : 'border-outline-variant hover:bg-white'"
          @click="$emit('scroll-change', s.id)"
        >
          <div class="font-medium text-xs" :class="scrollEffect === s.id ? 'text-primary' : ''">{{ s.label }}</div>
          <div class="text-[10px] text-on-surface-variant mt-0.5">{{ s.desc }}</div>
        </button>
      </div>
    </section>

    <button
      class="w-full py-2 text-xs border border-dashed border-outline-variant rounded-lg hover:bg-white"
      @click="previewTransition"
    >
      预览当前页动效
    </button>
    <p v-if="previewing" class="text-center text-xs text-primary">动效演示中…</p>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { PAGE_ANIMATIONS, SCROLL_EFFECTS } from '../constants/editorPresets'

const props = defineProps({
  slide: { type: Object, default: null },
  scrollEffect: { type: String, default: 'page' },
})

const emit = defineEmits(['save', 'scroll-change', 'preview-animation'])

const animation = ref('fade')
const previewing = ref(false)

watch(
  () => props.slide,
  (s) => {
    animation.value = s?.animation || 'fade'
  },
  { immediate: true }
)

function pickAnimation(id) {
  animation.value = id
  emit('save', { animation: id })
}

function previewTransition() {
  previewing.value = true
  emit('preview-animation', animation.value)
  setTimeout(() => { previewing.value = false }, 800)
}
</script>
