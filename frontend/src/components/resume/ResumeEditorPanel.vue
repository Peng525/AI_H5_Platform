<template>
  <div class="h-full overflow-y-auto p-4 bg-surface-container-low relative">
    <div ref="canvasRef" class="relative">
      <ClassicBlueTemplate
        :structured="structured"
        :selected-bind="selectedBind"
        :editing-bind="editingBind"
        :photo-url="photoUrl"
        :cell-value="cellValue"
        :cell-style="cellStyle"
        @select="startEdit"
        @edit="startEdit"
        @blur="stopEdit"
        @update-value="onUpdateValue"
        @photo-click="onPhotoClick"
      />
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
  selectedBind,
  editingBind,
  canvasRef,
  toolbarSelected,
  startEdit,
  stopEdit,
  updateCellValue,
  updateCellStyle,
  cellValue,
  cellStyle,
  resolveCellEl,
  load,
} = useResumeEditor(props.structured, props.visualDocument)

watch(
  () => [props.structured, props.visualDocument],
  () => load({ structured: props.structured, visual_document: props.visualDocument }),
  { deep: true },
)

watch(structured, (v) => emit('update:structured', v), { deep: true })
watch(visualDocument, (v) => emit('update:visualDocument', v), { deep: true })

function onUpdateValue(bind, value) {
  updateCellValue(bind, value)
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
})
</script>
