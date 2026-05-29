import { computed, ref, watch } from 'vue'
import { api } from '../api/client'
import { DEFAULT_CANVAS_BG } from '../constants/canvasBackgrounds.js'

const STORAGE_PREFIX = 'ai_h5_canvas_'
const SETTINGS_PREFIX = 'ai_h5_project_settings_'

/** 画布层级：0 为全页背景图；正文组件从 CONTENT_BASE 起 */
export const CANVAS_Z = {
  BACKGROUND: 0,
  CONTENT_BASE: 10,
}

function storageKey(projectId, slideId) {
  return `${STORAGE_PREFIX}${Number(projectId)}_${slideId}`
}

export function buildElementsFromSlide(slide) {
  if (!slide) return []
  const items = []
  if (slide.title) {
    items.push(
      defaultElement('text', {
        x: 20,
        y: 80,
        width: 320,
        height: 48,
        content: slide.title,
        style: { fontSize: 22, color: '#ffffff', fontWeight: 'bold', background: 'transparent' },
      })
    )
  }
  if (slide.subtitle) {
    items.push(
      defaultElement('text', {
        x: 20,
        y: 130,
        width: 320,
        height: 32,
        content: slide.subtitle,
        style: { fontSize: 14, color: '#ffffff', background: 'transparent' },
      })
    )
  }
  ;(slide.bullets || []).forEach((b, i) => {
    items.push(
      defaultElement('text', {
        x: 24,
        y: 170 + i * 28,
        width: 300,
        height: 24,
        content: `• ${b}`,
        style: { fontSize: 14, color: '#ffffff', background: 'transparent' },
      })
    )
  })
  if (slide.layout === 'image-text') {
    const label = encodeURIComponent((slide.title || 'AI生图').slice(0, 16))
    items.push(
      defaultElement('image', {
        x: 20,
        y: 280,
        width: 335,
        height: 200,
        content: `https://placehold.co/335x200/005daa/ffffff?text=${label}`,
      })
    )
  }
  return items
}

/** 根据适应方式计算图片在画布上的位置与样式 */
export function computeImageFitLayout(fit, viewport, meta = {}) {
  const vp = viewport
  const aspect =
    meta.height && meta.width
      ? meta.height / meta.width
      : 16 / 9
  let x = 24
  let y = 120
  let width = vp.width - 48
  let height = Math.round(width * aspect)
  let zIndex = CANVAS_Z.CONTENT_BASE
  let insertAtFront = false

  if (fit === 'fill') {
    x = 0
    y = 0
    width = vp.width
    height = vp.height
    zIndex = CANVAS_Z.BACKGROUND
    insertAtFront = true
  } else if (fit === 'original') {
    width = Math.min(meta.width || 280, vp.width - 48)
    height = Math.min(meta.height || Math.round(width * aspect), vp.height - 160)
    x = Math.round((vp.width - width) / 2)
    y = Math.round((vp.height - height) / 2)
  } else if (fit === 'width') {
    height = Math.round(width * aspect)
    x = Math.round((vp.width - width) / 2)
  }

  return {
    x,
    y,
    width,
    height,
    zIndex,
    insertAtFront,
    style: {
      background: fit === 'fill' ? 'transparent' : '#f0f0f0',
      objectFit: fit === 'fill' ? 'cover' : 'contain',
    },
  }
}

/** 预览用：localStorage → 服务端 canvas → 由 slide 字段生成 */
export function resolvePreviewElements(projectId, slide) {
  if (!slide?.id) return []
  const stored = loadCanvasElements(projectId, slide.id)
  if (stored.length) return stored
  if (slide.canvas_elements?.length) return slide.canvas_elements
  return buildElementsFromSlide(slide)
}

export function loadCanvasElements(projectId, slideId) {
  if (!projectId || !slideId) return []
  try {
    const raw = localStorage.getItem(storageKey(projectId, slideId))
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

export function loadSlideBackground(projectId, slideId) {
  if (!projectId || !slideId) return DEFAULT_CANVAS_BG
  try {
    const raw = localStorage.getItem(`${SETTINGS_PREFIX}${projectId}`)
    if (!raw) return DEFAULT_CANVAS_BG
    const s = JSON.parse(raw)
    return s.slideBackgrounds?.[String(slideId)] ?? DEFAULT_CANVAS_BG
  } catch {
    return DEFAULT_CANVAS_BG
  }
}

function genId() {
  return `el_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
}

function defaultTableContent() {
  return {
    rows: [
      ['标题 A', '标题 B', '标题 C'],
      ['', '', ''],
      ['', '', ''],
    ],
  }
}

function defaultChartContent() {
  return { chartType: 'bar', values: [35, 65, 45, 80, 55] }
}

function defaultWordCloudContent() {
  return {
    words: [
      { text: '年轻人', weight: 120 },
      { text: '性价比', weight: 95 },
      { text: '文旅', weight: 80 },
    ],
    shapeId: 'cloud',
    customMaskUrl: '',
    fontFamily: 'system',
    maxFontSize: 80,
    minFontSize: 14,
    density: 'normal',
    rotation: 'random',
    colorMode: 'auto',
    colors: [],
    backgroundColor: '#ffffff',
    backgroundAlpha: 1,
  }
}

export function defaultElement(type, overrides = {}) {
  const base = {
    id: genId(),
    type,
    x: 24,
    y: 120,
    height: type === 'shape' ? 80 : type === 'image' ? 120 : type === 'table' ? 100 : type === 'chart' ? 120 : type === 'wordcloud' ? 200 : type === 'icon' ? 64 : 48,
    width: type === 'table' ? 220 : type === 'chart' ? 200 : type === 'wordcloud' ? 280 : type === 'icon' ? 64 : type === 'shape' ? 120 : 200,
    zIndex: CANVAS_Z.CONTENT_BASE,
    content: type === 'text' ? '双击编辑文本' : type === 'icon' ? 'star' : type === 'table' ? defaultTableContent() : type === 'chart' ? defaultChartContent() : type === 'wordcloud' ? defaultWordCloudContent() : type === 'image' ? '' : '',
    style: {
      fontSize: 16,
      color: '#1b1b1c',
      background: type === 'shape' ? '#005daa' : type === 'table' ? '#ffffff' : type === 'chart' ? '#ffffff' : type === 'icon' ? '#e8f0fe' : 'transparent',
      borderRadius: type === 'shape' || type === 'icon' ? 8 : 0,
      headerBackground: type === 'table' ? '#005daa' : undefined,
      headerColor: type === 'table' ? '#ffffff' : undefined,
      borderColor: type === 'table' ? '#c0c7d6' : undefined,
      chartColor: type === 'chart' ? '#005daa' : undefined,
      fontWeight: 'normal',
      textAlign: 'left',
      fontFamily: '"Microsoft YaHei", "PingFang SC", sans-serif',
      lineHeight: 1.5,
      letterSpacing: 0,
    },
  }
  return { ...base, ...overrides, style: { ...base.style, ...(overrides.style || {}) } }
}

function remapElementsForCanvas(newEls, existingElements) {
  if (!Array.isArray(newEls) || !newEls.length) return []
  const maxZ = existingElements.reduce((m, el) => Math.max(m, el.zIndex || 0), 0)
  const baseZ = Math.max(CANVAS_Z.CONTENT_BASE, maxZ + 1)
  const internalZs = newEls.map((el) => el.zIndex ?? 1)
  const minInternal = Math.min(...internalZs)
  return newEls.map((el) => {
    const copy = JSON.parse(JSON.stringify(el))
    copy.id = genId()
    copy.zIndex = baseZ + ((el.zIndex ?? 1) - minInternal)
    return copy
  })
}

export function useSlideCanvas(projectIdRef, slideIdRef) {
  const elements = ref([])
  const selectedIds = ref([])
  const selectedId = computed(() => selectedIds.value[selectedIds.value.length - 1] || null)
  const clipboard = ref([])
  let saveTimer = null
  const undoStack = []
  const redoStack = []
  const MAX_HISTORY = 50
  let historyBatching = false

  function normalizeSelectedIds(snapshot) {
    if (Array.isArray(snapshot?.selectedIds)) return [...snapshot.selectedIds]
    if (snapshot?.selectedId) return [snapshot.selectedId]
    return []
  }

  function snapshotState() {
    return {
      elements: JSON.parse(JSON.stringify(elements.value)),
      selectedIds: [...selectedIds.value],
    }
  }

  function pushHistory() {
    undoStack.push(snapshotState())
    if (undoStack.length > MAX_HISTORY) undoStack.shift()
    redoStack.length = 0
  }

  function beginHistoryBatch() {
    if (!historyBatching) {
      pushHistory()
      historyBatching = true
    }
  }

  function endHistoryBatch() {
    historyBatching = false
  }

  function undo() {
    if (!undoStack.length) return false
    redoStack.push(snapshotState())
    const prev = undoStack.pop()
    elements.value = prev.elements
    selectedIds.value = normalizeSelectedIds(prev)
    persistLocal()
    scheduleServerSave()
    return true
  }

  function redo() {
    if (!redoStack.length) return false
    undoStack.push(snapshotState())
    const next = redoStack.pop()
    elements.value = next.elements
    selectedIds.value = normalizeSelectedIds(next)
    persistLocal()
    scheduleServerSave()
    return true
  }

  function canUndo() {
    return undoStack.length > 0
  }

  function clearHistory() {
    undoStack.length = 0
    redoStack.length = 0
    historyBatching = false
  }

  function loadElements(serverCanvas) {
    const pid = projectIdRef.value
    const sid = slideIdRef.value
    if (!pid || !sid) {
      elements.value = []
      return
    }
    try {
      const raw = localStorage.getItem(storageKey(pid, sid))
      const stored = raw ? JSON.parse(raw) : []
      if (stored.length) {
        elements.value = stored
      } else if (serverCanvas?.length) {
        elements.value = serverCanvas
        persistLocal()
      } else {
        elements.value = []
      }
    } catch {
      elements.value = serverCanvas?.length ? serverCanvas : []
    }
    selectedIds.value = []
    clearHistory()
  }

  function selectElement(id, { toggle = false, additive = false } = {}) {
    if (toggle) {
      if (selectedIds.value.includes(id)) {
        selectedIds.value = selectedIds.value.filter((x) => x !== id)
      } else {
        selectedIds.value = [...selectedIds.value, id]
      }
      return
    }
    if (additive) {
      if (!selectedIds.value.includes(id)) {
        selectedIds.value = [...selectedIds.value, id]
      }
      return
    }
    selectedIds.value = [id]
  }

  function clearSelection() {
    selectedIds.value = []
  }

  function selectElements(ids, { additive = false } = {}) {
    const unique = [...new Set(ids)]
    if (additive) {
      selectedIds.value = [...new Set([...selectedIds.value, ...unique])]
    } else {
      selectedIds.value = unique
    }
  }

  function persistLocal() {
    const pid = projectIdRef.value
    const sid = slideIdRef.value
    if (!pid || !sid) return
    try {
      localStorage.setItem(
        storageKey(pid, sid),
        JSON.stringify(elements.value.map((el) => ({ ...el, updatedAt: Date.now() })))
      )
    } catch (e) {
      console.warn('画布本地保存失败', e)
    }
  }

  function scheduleServerSave() {
    const pid = projectIdRef.value
    const sid = slideIdRef.value
    if (!pid || !sid) return
    clearTimeout(saveTimer)
    saveTimer = setTimeout(() => {
      api.saveSlideCanvas(Number(pid), sid, elements.value).catch((e) => {
        console.warn('画布同步服务器失败', e)
      })
    }, 400)
  }

  function replaceAllElements(newElements) {
    if (!historyBatching) pushHistory()
    const remapped = remapElementsForCanvas(newElements, [])
    elements.value = remapped
    selectedIds.value = []
    saveElements()
  }

  function appendLayoutElements(newElements) {
    if (!Array.isArray(newElements) || !newElements.length) return []
    if (!historyBatching) pushHistory()
    const remapped = remapElementsForCanvas(newElements, elements.value)
    elements.value.push(...remapped)
    selectedIds.value = remapped.map((el) => el.id)
    saveElements()
    return remapped
  }

  function saveElements() {
    persistLocal()
    scheduleServerSave()
  }

  async function flushCanvasSave() {
    const pid = projectIdRef.value
    const sid = slideIdRef.value
    if (!pid || !sid) return
    persistLocal()
    clearTimeout(saveTimer)
    try {
      await api.saveSlideCanvas(Number(pid), sid, elements.value)
    } catch (e) {
      console.warn('画布同步服务器失败', e)
    }
  }

  function addElement(type, overrides = {}) {
    if (!historyBatching) pushHistory()
    const maxZ = elements.value.reduce((m, el) => Math.max(m, el.zIndex || 0), 0)
    const zIndex = overrides.zIndex ?? Math.max(CANVAS_Z.CONTENT_BASE, maxZ + 1)
    const el = defaultElement(type, { ...overrides, zIndex })
    elements.value.push(el)
    selectedIds.value = [el.id]
    saveElements()
    return el
  }

  function updateElement(id, patch) {
    const idx = elements.value.findIndex((el) => el.id === id)
    if (idx < 0) return
    if (!historyBatching) pushHistory()
    const prev = elements.value[idx]
    elements.value[idx] = {
      ...prev,
      ...patch,
      style: patch.style ? { ...prev.style, ...patch.style } : prev.style,
    }
    saveElements()
  }

  function removeElement(id) {
    if (!historyBatching) pushHistory()
    elements.value = elements.value.filter((el) => el.id !== id)
    selectedIds.value = selectedIds.value.filter((sid) => sid !== id)
    saveElements()
  }

  function removeSelected() {
    if (!selectedIds.value.length) return
    if (!historyBatching) pushHistory()
    const set = new Set(selectedIds.value)
    elements.value = elements.value.filter((el) => !set.has(el.id))
    selectedIds.value = []
    saveElements()
  }

  function duplicateElement(id) {
    const src = elements.value.find((el) => el.id === id)
    if (!src) return
    if (!historyBatching) pushHistory()
    const copy = {
      ...JSON.parse(JSON.stringify(src)),
      id: genId(),
      x: src.x + 12,
      y: src.y + 12,
      zIndex: (src.zIndex || 0) + 1,
    }
    elements.value.push(copy)
    selectedIds.value = [copy.id]
    saveElements()
    return copy
  }

  function duplicateSelected() {
    if (!selectedIds.value.length) return []
    if (!historyBatching) pushHistory()
    const maxZ = elements.value.reduce((m, el) => Math.max(m, el.zIndex || 0), 0)
    const newIds = []
    selectedIds.value.forEach((id, i) => {
      const src = elements.value.find((el) => el.id === id)
      if (!src) return
      const copy = {
        ...JSON.parse(JSON.stringify(src)),
        id: genId(),
        x: src.x + 12,
        y: src.y + 12,
        zIndex: maxZ + 1 + i,
      }
      elements.value.push(copy)
      newIds.push(copy.id)
    })
    selectedIds.value = newIds
    saveElements()
    return newIds
  }

  function copySelected() {
    if (!selectedIds.value.length) return false
    clipboard.value = selectedIds.value
      .map((id) => elements.value.find((el) => el.id === id))
      .filter(Boolean)
      .map((el) => JSON.parse(JSON.stringify(el)))
    return clipboard.value.length > 0
  }

  function pasteClipboard() {
    if (!clipboard.value.length) return false
    if (!historyBatching) pushHistory()
    const maxZ = elements.value.reduce((m, el) => Math.max(m, el.zIndex || 0), 0)
    const newIds = []
    clipboard.value.forEach((src, i) => {
      const copy = {
        ...JSON.parse(JSON.stringify(src)),
        id: genId(),
        x: src.x + 12,
        y: src.y + 12,
        zIndex: maxZ + 1 + i,
      }
      elements.value.push(copy)
      newIds.push(copy.id)
    })
    selectedIds.value = newIds
    saveElements()
    return true
  }

  function bringToFront(id) {
    if (!historyBatching) pushHistory()
    const maxZ = elements.value.reduce((m, el) => Math.max(m, el.zIndex || 0), 0)
    const idx = elements.value.findIndex((el) => el.id === id)
    if (idx < 0) return
    elements.value[idx] = { ...elements.value[idx], zIndex: maxZ + 1 }
    saveElements()
  }

  function bringSelectedToFront() {
    if (!selectedIds.value.length) return
    if (!historyBatching) pushHistory()
    let maxZ = elements.value.reduce((m, el) => Math.max(m, el.zIndex || 0), 0)
    for (const id of selectedIds.value) {
      const idx = elements.value.findIndex((el) => el.id === id)
      if (idx < 0) continue
      maxZ += 1
      elements.value[idx] = { ...elements.value[idx], zIndex: maxZ }
    }
    saveElements()
  }

  function getContentFloorZ() {
    const contentZs = elements.value
      .map((el) => el.zIndex ?? CANVAS_Z.CONTENT_BASE)
      .filter((z) => z > CANVAS_Z.BACKGROUND)
    return contentZs.length ? Math.min(...contentZs) : CANVAS_Z.CONTENT_BASE
  }

  function sendSelectedToBack() {
    if (!selectedIds.value.length) return
    if (!historyBatching) pushHistory()
    const floor = getContentFloorZ()
    for (const id of selectedIds.value) {
      const idx = elements.value.findIndex((el) => el.id === id)
      if (idx < 0) continue
      elements.value[idx] = { ...elements.value[idx], zIndex: floor }
    }
    saveElements()
  }

  function bringSelectedForward() {
    if (!selectedIds.value.length) return
    if (!historyBatching) pushHistory()
    for (const id of selectedIds.value) {
      const idx = elements.value.findIndex((el) => el.id === id)
      if (idx < 0) continue
      const z = elements.value[idx].zIndex || CANVAS_Z.CONTENT_BASE
      elements.value[idx] = { ...elements.value[idx], zIndex: z + 1 }
    }
    saveElements()
  }

  function sendSelectedBackward() {
    if (!selectedIds.value.length) return
    if (!historyBatching) pushHistory()
    for (const id of selectedIds.value) {
      const idx = elements.value.findIndex((el) => el.id === id)
      if (idx < 0) continue
      const z = elements.value[idx].zIndex || CANVAS_Z.CONTENT_BASE
      elements.value[idx] = {
        ...elements.value[idx],
        zIndex: Math.max(CANVAS_Z.CONTENT_BASE, z - 1),
      }
    }
    saveElements()
  }

  function syncFromSlide(slide) {
    if (!slide || elements.value.length > 0) return
    const items = buildElementsFromSlide(slide)
    if (items.length) {
      elements.value = items
      saveElements()
    }
  }

  watch([projectIdRef, slideIdRef], () => loadElements(), { immediate: true })

  function addImageFromAi(src, fit = 'width', viewport = { width: 375, height: 812 }, meta = {}) {
    const layout = computeImageFitLayout(fit, viewport, meta)
    const zIndex =
      fit === 'fill'
        ? layout.zIndex
        : elements.value.reduce((m, el) => Math.max(m, el.zIndex || 0), 0) + 1
    const el = defaultElement('image', {
      x: layout.x,
      y: layout.y,
      width: layout.width,
      height: layout.height,
      content: src,
      zIndex,
      style: layout.style,
      sourceWidth: meta.width,
      sourceHeight: meta.height,
    })
    if (!historyBatching) pushHistory()
    if (layout.insertAtFront) {
      elements.value.unshift(el)
    } else {
      elements.value.push(el)
    }
    selectedIds.value = [el.id]
    saveElements()
    return el
  }

  function applyImageFitToSelected(fit, viewport = { width: 375, height: 812 }) {
    const id = selectedId.value
    if (!id) return
    const idx = elements.value.findIndex((e) => e.id === id)
    if (idx < 0) return
    const el = elements.value[idx]
    if (el.type !== 'image') return

    const meta = {
      width: el.sourceWidth || el.width,
      height: el.sourceHeight || el.height,
    }
    const layout = computeImageFitLayout(fit, viewport, meta)
    const zIndex =
      fit === 'fill'
        ? layout.zIndex
        : Math.max(CANVAS_Z.CONTENT_BASE, el.zIndex || CANVAS_Z.CONTENT_BASE)
    const updated = {
      ...el,
      x: layout.x,
      y: layout.y,
      width: layout.width,
      height: layout.height,
      zIndex,
      style: { ...el.style, ...layout.style },
    }
    if (!historyBatching) pushHistory()
    elements.value.splice(idx, 1)
    if (layout.insertAtFront) {
      elements.value.unshift(updated)
    } else {
      elements.value.push(updated)
    }
    selectedIds.value = [updated.id]
    saveElements()
    return updated
  }

  return {
    elements,
    selectedIds,
    selectedId,
    loadElements,
    saveElements,
    replaceAllElements,
    appendLayoutElements,
    flushCanvasSave,
    addElement,
    addImageFromAi,
    applyImageFitToSelected,
    updateElement,
    removeElement,
    removeSelected,
    duplicateElement,
    duplicateSelected,
    copySelected,
    pasteClipboard,
    selectElement,
    selectElements,
    clearSelection,
    bringToFront,
    bringSelectedToFront,
    sendSelectedToBack,
    bringSelectedForward,
    sendSelectedBackward,
    syncFromSlide,
    undo,
    redo,
    canUndo,
    beginHistoryBatch,
    endHistoryBatch,
  }
}
