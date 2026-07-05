<template>
  <div class="h-full overflow-y-auto p-4 bg-surface-container-low relative">
    <div ref="canvasRef" class="relative space-y-6">
      <section
        v-for="(page, index) in pages"
        :key="page.id"
        class="resume-page-block"
      >
        <p v-if="pages.length > 1" class="text-xs text-on-surface-variant mb-2 text-center">
          第 {{ index + 1 }} 页
        </p>
        <div :ref="(el) => setPageRef(index, el)" class="relative">
          <ClassicBlueTemplate
            :structured="page.structured"
            :selected-bind="selectedBind"
            :editing-bind="editingBind"
            :photo-url="photoUrl"
            :cell-value="(bind) => cellValue(bind, index)"
            :cell-style="(bind) => cellStyle(bind, index)"
            @select="(bind) => startEdit(bind, index)"
            @edit="(bind) => startEdit(bind, index)"
            @blur="stopEdit"
            @update-value="(bind, val) => onUpdateValue(bind, val, index)"
            @photo-click="onPhotoClick"
          />
        </div>
        <div class="flex justify-center items-center gap-3 mt-4">
          <button
            type="button"
            class="inline-flex items-center gap-1.5 px-4 py-2 text-sm rounded-lg border border-outline-variant bg-white hover:bg-surface-container-low transition-colors"
            title="在本页下方新增一页空白内容"
            @click="insertBlankPageAfter(index)"
          >
            <span class="inline-flex w-5 h-5 items-center justify-center rounded-full border border-current text-base leading-none">+</span>
            新页
          </button>
          <button
            type="button"
            class="inline-flex items-center gap-1.5 px-4 py-2 text-sm rounded-lg border border-outline-variant bg-white hover:bg-surface-container-low transition-colors"
            title="复制本页全部内容到新页"
            @click="duplicatePageAfter(index)"
          >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <rect x="9" y="9" width="13" height="13" rx="2" />
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
            </svg>
            复制
          </button>
        </div>
      </section>
    </div>
    <input ref="photoInputRef" type="file" accept="image/*" class="hidden" @change="onPhotoPicked" />
    <ResumeFormatToolbar
      :selected="toolbarSelected"
      :resolve-element-el="resolveCellEl"
      :scroll-root-ref="canvasRef"
      @style-change="updateCellStyle"
    />
  </div>
</template>

<script setup>
import { onBeforeUnmount, ref, watch } from 'vue'
import ClassicBlueTemplate from './ClassicBlueTemplate.vue'
import ResumeFormatToolbar from './ResumeFormatToolbar.vue'
import { useResumeEditor } from '../../composables/useResumeEditor.js'
import { api } from '../../api/client.js'

const props = defineProps({
  structured: { type: Object, default: () => ({}) },
  visualDocument: { type: Object, default: () => ({}) },
  publicId: { type: String, default: '' },
})

const emit = defineEmits(['update:structured', 'update:visualDocument'])

const photoInputRef = ref(null)
const photoUrl = ref('')

const {
  structured,
  visualDocument,
  pages,
  selectedBind,
  editingBind,
  canvasRef,
  setPageRef,
  toolbarSelected,
  startEdit,
  stopEdit,
  updateCellValue,
  updateCellStyle,
  cellValue,
  cellStyle,
  resolveCellEl,
  insertBlankPageAfter,
  duplicatePageAfter,
  load,
} = useResumeEditor(props.structured, props.visualDocument)

watch(
  () => [props.structured, props.visualDocument],
  () => load({ structured: props.structured, visual_document: props.visualDocument }),
  { deep: true },
)

watch(structured, (v) => emit('update:structured', v), { deep: true })
watch(visualDocument, (v) => emit('update:visualDocument', v), { deep: true })

function onUpdateValue(bind, value, pageIndex) {
  updateCellValue(bind, value, pageIndex)
}

function onPhotoClick() {
  photoInputRef.value?.click()
}

async function onPhotoPicked(e) {
  const file = e.target.files?.[0]
  if (!file || !props.publicId) return
  const fd = new FormData()
  fd.append('file', file)
  try {
    const up = await api.uploadResumeFile(fd)
    visualDocument.value = {
      ...visualDocument.value,
      photo_file_id: up.file_id,
    }
    photoUrl.value = URL.createObjectURL(file)
  } catch {
    /* ignore */
  }
  e.target.value = ''
}

onBeforeUnmount(() => {
  if (photoUrl.value) URL.revokeObjectURL(photoUrl.value)
})

defineExpose({
  structured,
  visualDocument,
  pages,
})
</script>
