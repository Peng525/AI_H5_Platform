<template>
  <aside class="w-[17rem] sm:w-[20rem] border-l border-outline-variant/60 bg-white flex flex-col shrink-0 min-h-0 h-full overflow-hidden">
    <div class="flex items-center justify-between px-4 py-3 border-b border-outline-variant/60 shrink-0">
      <h3 class="text-sm font-semibold text-on-surface">Media</h3>
      <button type="button" class="p-1 rounded hover:bg-surface-container text-on-surface-variant" title="关闭" @click="$emit('close')">
        <span class="material-symbols-outlined text-[20px]">close</span>
      </button>
    </div>

    <div class="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
      <div class="rounded-lg border border-outline-variant/60 overflow-hidden bg-surface-container-low aspect-video flex items-center justify-center">
        <img
          v-if="imageUrl"
          :src="imageUrl"
          alt=""
          class="max-w-full max-h-full object-contain"
        />
        <span v-else class="text-xs text-on-surface-variant">无图片</span>
      </div>

      <div class="space-y-2">
        <label class="text-xs font-medium text-on-surface-variant">适应方式</label>
        <div class="flex flex-wrap gap-1.5">
          <button
            v-for="m in fitModes"
            :key="m.id"
            type="button"
            class="px-2.5 py-1 text-xs font-medium rounded-lg border transition-colors"
            :class="activeFit === m.id ? 'border-primary bg-primary/8 text-primary' : 'border-outline-variant hover:bg-surface-container-low'"
            @click="$emit('image-fit', m.id)"
          >
            {{ m.label }}
          </button>
        </div>
      </div>

      <div class="flex flex-col gap-2">
        <button
          type="button"
          class="w-full py-2 text-sm font-medium rounded-lg border border-outline-variant hover:bg-surface-container-low inline-flex items-center justify-center gap-1.5"
          @click="$emit('image-crop')"
        >
          <span class="material-symbols-outlined text-[18px]">crop</span>
          裁切图片
        </button>
      </div>

      <div class="space-y-2">
        <label for="regenerate-prompt" class="text-xs font-medium text-on-surface-variant">提示词</label>
        <textarea
          id="regenerate-prompt"
          v-model="regeneratePrompt"
          rows="3"
          class="w-full text-xs text-on-surface bg-surface-container-low rounded-lg p-2 leading-relaxed border border-outline-variant/60 resize-y focus:outline-none focus:border-primary"
          placeholder="描述你想生成的画面…"
          :disabled="imageLoading"
        />
        <label class="flex items-start gap-2 cursor-pointer select-none">
          <input
            v-model="useReferenceImage"
            type="checkbox"
            class="mt-0.5 rounded border-outline-variant text-primary focus:ring-primary"
            :disabled="imageLoading || !hasReferenceImage"
          />
          <span class="text-xs text-on-surface-variant leading-snug">将此图作为参考图</span>
        </label>
        <button
          type="button"
          class="w-full py-2 text-sm font-medium rounded-lg bg-primary text-on-primary inline-flex items-center justify-center gap-1.5 disabled:opacity-50"
          :disabled="imageLoading || !regeneratePrompt.trim()"
          @click="submitRegenerate"
        >
          <span class="material-symbols-outlined text-[18px]">auto_awesome</span>
          {{ imageLoading ? '生成中…' : 'AI 重新生成' }}
        </button>
      </div>

      <p v-if="quotaRemaining != null" class="text-[11px] text-on-surface-variant">
        剩余配额 {{ quotaRemaining }} / {{ quotaTotal }}
      </p>
    </div>
  </aside>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  selectedElement: { type: Object, required: true },
  imageLoading: { type: Boolean, default: false },
  quotaRemaining: { type: Number, default: null },
  quotaTotal: { type: Number, default: null },
})

const emit = defineEmits(['close', 'image-fit', 'image-crop', 'regenerate-image'])

const fitModes = [
  { id: 'width', label: '适应宽' },
  { id: 'fill', label: '填充' },
  { id: 'original', label: '原图' },
]

const regeneratePrompt = ref('')
const useReferenceImage = ref(true)

const imageUrl = computed(() => {
  const c = props.selectedElement?.content
  if (typeof c !== 'string' || !c) return ''
  if (c.startsWith('http') || c.startsWith('data:image')) return c
  return ''
})

const hasReferenceImage = computed(() => Boolean(imageUrl.value))

function defaultPromptForElement(el) {
  if (!el) return ''
  return el.style?.imagePrompt || el.meta?.prompt || ''
}

watch(
  () => props.selectedElement?.id,
  () => {
    regeneratePrompt.value = defaultPromptForElement(props.selectedElement)
    useReferenceImage.value = Boolean(imageUrl.value)
  },
  { immediate: true },
)

const activeFit = computed(() => {
  const el = props.selectedElement
  if (!el) return 'width'
  if (el.fitIntent) return el.fitIntent
  if ((el.zIndex ?? 10) === 0) return 'fill'
  return 'width'
})

function submitRegenerate() {
  const prompt = regeneratePrompt.value.trim()
  if (!prompt) return
  emit('regenerate-image', {
    prompt,
    useReferenceImage: useReferenceImage.value && hasReferenceImage.value,
  })
}
</script>
