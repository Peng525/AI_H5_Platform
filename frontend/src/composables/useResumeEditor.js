import { computed, ref, watch } from 'vue'
import {
  defaultStructured,
  defaultVisualDocument,
  getBindValue,
  mergeCellStyle,
  setBindValue,
  setCellStyle,
} from '../utils/resumeBind.js'
import {
  blankPage,
  duplicatePage,
  normalizePages,
  pagesToVisualDocument,
} from '../utils/resumePages.js'

export function useResumeEditor(initialStructured, initialVisual, { onSave } = {}) {
  const structured = ref(defaultStructured())
  const visualDocument = ref(defaultVisualDocument())
  const pages = ref([])
  const activePageIndex = ref(0)
  const selectedBind = ref('')
  const editingBind = ref('')
  const canvasRef = ref(null)
  const pageRefs = ref([])

  function syncStructuredFromPages() {
    if (pages.value[0]) {
      structured.value = pages.value[0].structured
    }
  }

  function syncVisualFromPages() {
    visualDocument.value = pagesToVisualDocument(visualDocument.value, pages.value)
  }

  function load(data) {
    const vd = { ...defaultVisualDocument(), ...(data?.visual_document || {}) }
    const fallback = { ...defaultStructured(), ...(data?.structured || {}) }
    visualDocument.value = vd
    pages.value = normalizePages(vd, fallback)
    activePageIndex.value = 0
    syncStructuredFromPages()
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

  const selectedStyle = computed(() => {
    const page = pages.value[activePageIndex.value]
    const bind = selectedBind.value
    if (!bind) return {}
    const pageStyle = page?.styles?.[bind] || {}
    const globalStyle = activePageIndex.value === 0 ? mergeCellStyle(visualDocument.value, bind) : {}
    return { ...globalStyle, ...pageStyle }
  })

  const toolbarSelected = computed(() => ({
    id: selectedBind.value,
    style: selectedStyle.value,
  }))

  function setPageRef(index, el) {
    pageRefs.value[index] = el
  }

  function selectCell(bind, pageIndex = activePageIndex.value) {
    activePageIndex.value = pageIndex
    selectedBind.value = bind
    editingBind.value = ''
  }

  function startEdit(bind, pageIndex = activePageIndex.value) {
    activePageIndex.value = pageIndex
    selectedBind.value = bind
    editingBind.value = bind
  }

  function stopEdit() {
    editingBind.value = ''
  }

  function updateCellValue(bind, value, pageIndex = activePageIndex.value) {
    const page = pages.value[pageIndex]
    if (!page) return
    page.structured = setBindValue(page.structured, bind, value)
    if (pageIndex === 0) {
      structured.value = page.structured
    }
    syncVisualFromPages()
  }

  function updateCellStyle(patch) {
    if (!selectedBind.value) return
    const idx = activePageIndex.value
    const page = pages.value[idx]
    if (!page) return
    page.styles = {
      ...(page.styles || {}),
      [selectedBind.value]: {
        ...(page.styles?.[selectedBind.value] || {}),
        ...patch,
      },
    }
    if (idx === 0) {
      visualDocument.value = setCellStyle(visualDocument.value, selectedBind.value, patch)
    }
    syncVisualFromPages()
  }

  function cellValue(bind, pageIndex) {
    const page = pages.value[pageIndex]
    return getBindValue(page?.structured, bind)
  }

  function cellStyle(bind, pageIndex) {
    const page = pages.value[pageIndex]
    const pageStyle = page?.styles?.[bind] || {}
    const globalStyle = pageIndex === 0 ? mergeCellStyle(visualDocument.value, bind) : {}
    return { ...globalStyle, ...pageStyle }
  }

  function resolveCellEl(_slideId, bind) {
    const root = pageRefs.value[activePageIndex.value] || canvasRef.value
    if (!root || !bind) return null
    return root.querySelector(`[data-resume-bind="${bind}"]`)
  }

  function insertBlankPageAfter(index) {
    pages.value.splice(index + 1, 0, blankPage())
    syncVisualFromPages()
  }

  function duplicatePageAfter(index) {
    const source = pages.value[index]
    if (!source) return
    pages.value.splice(index + 1, 0, duplicatePage(source))
    syncVisualFromPages()
  }

  async function save() {
    syncVisualFromPages()
    if (onSave) {
      await onSave({
        structured: structured.value,
        visual_document: visualDocument.value,
      })
    }
  }

  function applyRemoteData(data) {
    load(data)
  }

  return {
    structured,
    visualDocument,
    pages,
    activePageIndex,
    selectedBind,
    editingBind,
    canvasRef,
    pageRefs,
    setPageRef,
    toolbarSelected,
    selectCell,
    startEdit,
    stopEdit,
    updateCellValue,
    updateCellStyle,
    cellValue,
    cellStyle,
    resolveCellEl,
    insertBlankPageAfter,
    duplicatePageAfter,
    save,
    applyRemoteData,
    load,
  }
}
