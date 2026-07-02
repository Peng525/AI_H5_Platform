import { computed, ref, watch } from 'vue'
import { defaultStructured, defaultVisualDocument, getBindValue, mergeCellStyle, setBindValue, setCellStyle } from '../utils/resumeBind.js'

export function useResumeEditor(initialStructured, initialVisual, { onSave } = {}) {
  const structured = ref(defaultStructured())
  const visualDocument = ref(defaultVisualDocument())
  const selectedBind = ref('')
  const editingBind = ref('')
  const canvasRef = ref(null)

  function load(data) {
    structured.value = { ...defaultStructured(), ...(data?.structured || {}) }
    visualDocument.value = { ...defaultVisualDocument(), ...(data?.visual_document || {}) }
  }

  if (initialStructured) load({ structured: initialStructured, visual_document: initialVisual })

  watch(
    () => [initialStructured, initialVisual],
    () => {
      if (initialStructured) {
        load({ structured: initialStructured, visual_document: initialVisual })
      }
    },
  )

  const selectedStyle = computed(() => mergeCellStyle(visualDocument.value, selectedBind.value))

  const toolbarSelected = computed(() => ({
    id: selectedBind.value,
    style: selectedStyle.value,
  }))

  function selectCell(bind) {
    selectedBind.value = bind
    editingBind.value = ''
  }

  function startEdit(bind) {
    selectedBind.value = bind
    editingBind.value = bind
  }

  function stopEdit() {
    editingBind.value = ''
  }

  function updateCellValue(bind, value) {
    structured.value = setBindValue(structured.value, bind, value)
  }

  function updateCellStyle(patch) {
    if (!selectedBind.value) return
    visualDocument.value = setCellStyle(visualDocument.value, selectedBind.value, patch)
  }

  function cellValue(bind) {
    return getBindValue(structured.value, bind)
  }

  function cellStyle(bind) {
    return mergeCellStyle(visualDocument.value, bind)
  }

  function resolveCellEl(_slideId, bind) {
    if (!canvasRef.value || !bind) return null
    return canvasRef.value.querySelector(`[data-resume-bind="${bind}"]`)
  }

  async function save() {
    if (onSave) {
      await onSave({
        structured: structured.value,
        visual_document: visualDocument.value,
      })
    }
  }

  function applyRemoteData(data) {
    if (data?.structured) structured.value = { ...defaultStructured(), ...data.structured }
    if (data?.visual_document) visualDocument.value = { ...defaultVisualDocument(), ...data.visual_document }
  }

  return {
    structured,
    visualDocument,
    selectedBind,
    editingBind,
    canvasRef,
    toolbarSelected,
    selectCell,
    startEdit,
    stopEdit,
    updateCellValue,
    updateCellStyle,
    cellValue,
    cellStyle,
    resolveCellEl,
    save,
    applyRemoteData,
    load,
  }
}
