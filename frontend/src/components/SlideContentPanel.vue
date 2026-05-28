<template>
  <div v-if="slide" class="p-4 space-y-4 text-sm">
    <label class="block">
      <span class="text-xs font-medium text-on-surface-variant">标题</span>
      <input
        v-model="form.title"
        class="w-full mt-1 border border-outline-variant rounded-lg px-3 py-2"
        @blur="emitSave"
      />
    </label>
    <label class="block">
      <span class="text-xs font-medium text-on-surface-variant">副标题</span>
      <input
        v-model="form.subtitle"
        class="w-full mt-1 border border-outline-variant rounded-lg px-3 py-2"
        @blur="emitSave"
      />
    </label>
    <label class="block">
      <span class="text-xs font-medium text-on-surface-variant">要点（每行一条）</span>
      <textarea
        v-model="bulletsText"
        rows="5"
        class="w-full mt-1 border border-outline-variant rounded-lg px-3 py-2 resize-none"
        @blur="emitBullets"
      />
    </label>
    <button
      class="w-full py-2 border border-outline-variant rounded-lg text-xs hover:bg-surface-container-low"
      @click="$emit('sync-canvas')"
    >
      同步到画布
    </button>
  </div>
  <p v-else class="p-4 text-on-surface-variant text-sm">请选择页面</p>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'

const props = defineProps({
  slide: { type: Object, default: null },
})

const emit = defineEmits(['save', 'sync-canvas'])

const form = reactive({ title: '', subtitle: '' })
const bulletsText = ref('')

watch(
  () => props.slide,
  (s) => {
    if (!s) return
    form.title = s.title || ''
    form.subtitle = s.subtitle || ''
    bulletsText.value = (s.bullets || []).join('\n')
  },
  { immediate: true }
)

function emitSave() {
  if (!props.slide) return
  emit('save', { title: form.title, subtitle: form.subtitle })
}

function emitBullets() {
  if (!props.slide) return
  const bullets = bulletsText.value.split('\n').map((l) => l.trim()).filter(Boolean)
  emit('save', { title: form.title, subtitle: form.subtitle, bullets })
}
</script>
