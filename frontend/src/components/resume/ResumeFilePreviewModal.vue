<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/40"
        @click.self="emit('close')"
      >
        <div
          class="bg-white rounded-xl shadow-elevated border border-outline-variant w-full max-w-3xl max-h-[90vh] flex flex-col overflow-hidden"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="titleId"
        >
          <div class="flex items-center justify-between gap-3 px-4 py-3 border-b border-outline-variant shrink-0">
            <h2 :id="titleId" class="font-semibold text-on-surface truncate min-w-0" :title="fileName">
              {{ fileName || '文件预览' }}
            </h2>
            <button
              type="button"
              class="shrink-0 text-on-surface-variant hover:text-on-surface p-1 rounded-lg hover:bg-surface-container-low"
              title="关闭"
              @click="emit('close')"
            >
              <span class="material-symbols-outlined text-[22px]">close</span>
            </button>
          </div>
          <div class="flex-1 min-h-0 overflow-auto p-4 bg-surface-container-low">
            <iframe
              v-if="previewKind === 'pdf' && objectUrl"
              :src="objectUrl"
              class="w-full h-[70vh] rounded-lg border border-outline-variant bg-white"
              title="PDF 预览"
            />
            <img
              v-else-if="previewKind === 'image' && objectUrl"
              :src="objectUrl"
              :alt="fileName"
              class="max-h-[70vh] mx-auto block rounded-lg border border-outline-variant bg-white"
            />
            <p v-else class="text-sm text-on-surface-variant text-center py-12">
              暂不支持预览此格式
            </p>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, onUnmounted, ref, useId, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  fileName: { type: String, default: '' },
  file: { type: Object, default: null },
})

const emit = defineEmits(['close'])

const titleId = useId()
const objectUrl = ref('')

const previewKind = computed(() => {
  const file = props.file
  if (!file) return 'unsupported'
  const mime = (file.type || '').toLowerCase()
  const name = (props.fileName || file.name || '').toLowerCase()
  if (mime === 'application/pdf' || name.endsWith('.pdf')) return 'pdf'
  if (mime.startsWith('image/') || /\.(png|jpe?g|gif|webp|bmp)$/i.test(name)) return 'image'
  return 'unsupported'
})

function revokeUrl() {
  if (objectUrl.value) {
    URL.revokeObjectURL(objectUrl.value)
    objectUrl.value = ''
  }
}

watch(
  () => [props.open, props.file],
  ([open, file]) => {
    revokeUrl()
    if (open && file instanceof File) {
      objectUrl.value = URL.createObjectURL(file)
    }
  },
  { immediate: true },
)

onUnmounted(revokeUrl)
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
