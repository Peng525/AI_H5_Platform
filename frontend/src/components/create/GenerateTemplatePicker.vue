<template>
  <div>
    <p class="text-xs font-medium text-white/80 mb-3 text-left">Choose a template</p>
    <div class="flex justify-center gap-3 sm:gap-4 overflow-x-auto pb-1 px-1">
      <button
        v-for="t in templates"
        :key="t.uiId"
        type="button"
        class="shrink-0 w-[72px] sm:w-[80px] rounded-lg p-2 flex flex-col items-center gap-1.5 transition-colors disabled:opacity-50"
        :class="modelValue === t.uiId
          ? 'bg-[#1a3a6b]/90 border border-sky-400/80'
          : 'bg-white/5 border border-white/25 hover:border-white/40'"
        :disabled="disabled"
        :title="t.label"
        @click="select(t)"
      >
        <div
          class="w-full aspect-[4/3] rounded-md flex items-center justify-center overflow-hidden px-1"
          :class="modelValue === t.uiId ? 'bg-white/10' : 'bg-black/20'"
        >
          <span
            v-if="t.wireframe === 'magic'"
            class="material-symbols-outlined text-[22px] text-white/80"
          >auto_awesome</span>
          <div v-else-if="t.wireframe === 'bullets'" class="w-[85%] space-y-1 py-0.5">
            <div class="h-[3px] w-full rounded-full wire-line" />
            <div v-for="i in 4" :key="i" class="flex items-center gap-1">
              <div class="w-1 h-1 rounded-full bg-white/40 shrink-0" />
              <div class="h-[2px] flex-1 rounded-full wire-line" />
            </div>
          </div>
          <div v-else-if="t.wireframe === 'paragraph'" class="w-[85%] space-y-1 py-0.5">
            <div class="h-[3px] w-full rounded-full wire-line" />
            <div class="h-[2px] w-full rounded-full wire-line" />
            <div class="h-[2px] w-[90%] rounded-full wire-line" />
            <div class="h-[2px] w-full rounded-full wire-line" />
            <div class="h-[2px] w-[75%] rounded-full wire-line" />
          </div>
          <div v-else-if="t.wireframe === 'cards'" class="w-[90%] space-y-1 py-0.5">
            <div class="h-[2px] w-[70%] rounded-full wire-line" />
            <div class="flex gap-0.5 justify-center">
              <div v-for="i in 3" :key="i" class="flex-1 h-5 rounded-sm border border-white/25 bg-white/10" />
            </div>
          </div>
          <div v-else-if="t.wireframe === 'image_text'" class="w-[90%] flex gap-1 items-stretch py-0.5">
            <div class="w-[38%] rounded-sm border border-white/25 bg-white/10 flex items-center justify-center">
              <span class="material-symbols-outlined text-[10px] text-white/50">image</span>
            </div>
            <div class="flex-1 space-y-0.5 flex flex-col justify-center">
              <div class="h-[2px] w-full rounded-full wire-line" />
              <div class="h-[2px] w-[85%] rounded-full wire-line" />
              <div class="h-[2px] w-[70%] rounded-full wire-line" />
            </div>
          </div>
        </div>
        <span
          class="text-[10px] sm:text-xs font-medium leading-tight text-center"
          :class="modelValue === t.uiId ? 'text-white' : 'text-white/75'"
        >
          {{ t.label }}
        </span>
      </button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: String, default: 'magic' },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'update:templateHint'])

const templates = [
  { uiId: 'magic', hint: 'magic', label: 'Magic', wireframe: 'magic' },
  { uiId: 'bullets', hint: 'text', label: '要点', wireframe: 'bullets' },
  { uiId: 'paragraph', hint: 'text', label: '段落', wireframe: 'paragraph' },
  { uiId: 'cards', hint: 'grid', label: '卡片', wireframe: 'cards' },
  { uiId: 'image_text', hint: 'image', label: '图片配文字', wireframe: 'image_text' },
]

function select(t) {
  if (props.disabled) return
  emit('update:modelValue', t.uiId)
  emit('update:templateHint', t.hint)
}
</script>

<style scoped>
.wire-line {
  @apply bg-white/35;
}
</style>
