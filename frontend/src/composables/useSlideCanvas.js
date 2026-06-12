import { computed, ref, watch } from 'vue'
import { api } from '../api/client'
import { DEFAULT_CANVAS_BG } from '../constants/canvasBackgrounds.js'
import { getCanvasContentSize, DEFAULT_WEB_VIEWPORT_ID, isWideWebViewport } from '../constants/editorPresets.js'
import { getThemeMargins } from '../constants/designThemes.js'
import { textColorForSlideBackground } from '../utils/slideBackground.js'
import { compileSlideIfNeeded, resolveSlideStructured } from '../utils/compileStructuredSlide.js'

const STORAGE_PREFIX = 'ai_h5_canvas_'
const SETTINGS_PREFIX = 'ai_h5_project_settings_'

/** 画布层级：0 为全页背景图；正文组件从 CONTENT_BASE 起 */
export const CANVAS_Z = {
  BACKGROUND: 0,
  CONTENT_BASE: 10,
}

function storageKey(projectId, slideId) {
  return `${STORAGE_PREFIX}${String(projectId)}_${slideId}`
}

export function buildElementsFromSlide(slide, viewportId = 'mobile-375') {
  if (!slide) return []
  const textColor = textColorForSlideBackground(slide.canvas_background)
  const isWeb = String(viewportId).startsWith('web')
  const wide = isWideWebViewport(viewportId)
  const margin = wide ? getThemeMargins('zjy-minimal', viewportId) : null
  const marginX = wide ? margin.x : isWeb ? 80 : 20
  const contentW = wide ? margin.contentWidth : isWeb ? 1120 : 320
  const titleSize = wide ? 28 : isWeb ? 40 : 22
  const subtitleSize = wide ? 14 : isWeb ? 20 : 14
  const bodySize = wide ? 14 : isWeb ? 18 : 14
  const titleY = wide ? 48 : isWeb ? 120 : 80
  const subtitleY = wide ? 96 : isWeb ? 190 : 130
  const bulletsStartY = wide ? 140 : isWeb ? 240 : 170
  const bulletLineH = wide ? 24 : isWeb ? 36 : 28

  const items = []
  if (slide.title) {
    items.push(
      defaultElement('text', {
        x: marginX,
        y: titleY,
        width: contentW,
        height: isWeb ? 56 : 48,
        content: slide.title,
        style: { fontSize: titleSize, color: textColor, fontWeight: 'bold', background: 'transparent' },
      })
    )
  }
  if (slide.subtitle) {
    items.push(
      defaultElement('text', {
        x: marginX,
        y: subtitleY,
        width: contentW,
        height: isWeb ? 40 : 32,
        content: slide.subtitle,
        style: { fontSize: subtitleSize, color: textColor, background: 'transparent' },
      })
    )
  }
  ;(slide.bullets || []).forEach((b, i) => {
    items.push(
      defaultElement('text', {
        x: marginX + (isWeb ? 8 : 4),
        y: bulletsStartY + i * bulletLineH,
        width: contentW - (isWeb ? 16 : 8),
        height: bulletLineH - 4,
        content: `• ${b}`,
        style: { fontSize: bodySize, color: textColor, background: 'transparent' },
      })
    )
  })
  if (slide.layout === 'image-text') {
    const label = encodeURIComponent((slide.title || 'AI生图').slice(0, 16))
    const imgW = isWeb ? 960 : 335
    const imgH = isWeb ? 360 : 200
    items.push(
      defaultElement('image', {
        x: marginX,
        y: bulletsStartY + (slide.bullets?.length || 0) * bulletLineH + (isWeb ? 32 : 16),
        width: imgW,
        height: imgH,
        content: `https://placehold.co/${imgW}x${imgH}/005daa/ffffff?text=${label}`,
      })
    )
  }
  return items
}

/** 根据适应方式计算图片在画布内容区上的位置与样式 */
export function computeImageFitLayout(fit, viewport, meta = {}) {
  const content = getCanvasContentSize(viewport)
  const srcW = meta.width || 1024
  const srcH = meta.height || 1024
  const aspect = srcH / srcW

  if (fit === 'fill') {
    return {
      x: 0,
      y: 0,
      width: content.width,
      height: content.height,
      zIndex: CANVAS_Z.BACKGROUND,
      insertAtFront: true,
      fitIntent: 'fill',
      style: {
        background: 'transparent',
        objectFit: 'contain',
      },
    }
  }

  if (fit === 'original') {
    const scale = Math.min(content.width / srcW, content.height / srcH, 1)
    const width = Math.round(srcW * scale)
    const height = Math.round(srcH * scale)
    return {
      x: Math.round((content.width - width) / 2),
      y: Math.round((content.height - height) / 2),
      width,
      height,
      zIndex: CANVAS_Z.CONTENT_BASE,
      insertAtFront: false,
      fitIntent: 'original',
      style: {
        background: 'transparent',
        objectFit: 'fill',
      },
    }
  }

  const width = Math.max(24, content.width - 48)
  const height = Math.round(width * aspect)
  return {
    x: Math.round((content.width - width) / 2),
    y: 120,
    width,
    height,
    zIndex: CANVAS_Z.CONTENT_BASE,
    insertAtFront: false,
    fitIntent: 'width',
    style: {
      background: '#f0f0f0',
      objectFit: 'contain',
    },
  }
}

/** 预览用：localStorage → 服务端 canvas → structured 编译 → 由 slide 字段生成 */
export function resolvePreviewElements(projectId, slide, viewportId = DEFAULT_WEB_VIEWPORT_ID, themeId = 'zjy-minimal') {
  if (!slide?.id) return []
  const stored = loadCanvasElements(projectId, slide.id)
  if (stored.length) return stored
  if (slide.canvas_elements?.length) return slide.canvas_elements
  if (resolveSlideStructured(slide)) {
    const compiled = compileSlideIfNeeded(slide, viewportId, themeId)
    if (compiled.length) return compiled
  }
  return buildElementsFromSlide(slide, viewportId)
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

function chartCardId() {
  return `c_${Math.random().toString(36).slice(2, 10)}`
}

export function defaultChartStackContent() {
  return {
    cards: [
      {
        id: chartCardId(),
        title: '您对未来「吃谷」消费的期望',
        chartType: 'pie',
        labels: ['增加', '维持', '减少'],
        values: [45, 35, 20],
      },
      {
        id: chartCardId(),
        title: '您对「吃谷」规划和安排的建议',
        chartType: 'bar',
        labels: ['规划1', '规划2', '规划3', '规划4'],
        values: [60, 40, 55, 70],
      },
    ],
  }
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
    height: type === 'shape' ? 80 : type === 'image' ? 120 : type === 'table' ? 100 : type === 'chart' ? 120 : type === 'chartStack' ? 260 : type === 'wordcloud' ? 200 : type === 'icon' ? 64 : 48,
    width: type === 'table' ? 220 : type === 'chart' ? 200 : type === 'chartStack' ? 320 : type === 'wordcloud' ? 280 : type === 'icon' ? 64 : type === 'shape' ? 120 : 200,
    zIndex: CANVAS_Z.CONTENT_BASE,
    content: type === 'text' ? '双击编辑文本' : type === 'icon' ? 'star' : type === 'table' ? defaultTableContent() : type === 'chart' ? defaultChartContent() : type === 'chartStack' ? defaultChartStackContent() : type === 'wordcloud' ? defaultWordCloudContent() : type === 'image' ? '' : '',
    style: {
      fontSize: 16,
      color: '#1b1b1c',
      background: type === 'shape' ? '#005daa' : type === 'table' ? '#ffffff' : type === 'chart' || type === 'chartStack' ? '#ffffff' : type === 'icon' ? '#e8f0fe' : 'transparent',
      borderRadius: type === 'shape' || type === 'icon' ? 8 : 0,
      headerBackground: type === 'table' ? '#005daa' : undefined,
      headerColor: type === 'table' ? '#ffffff' : undefined,
      borderColor: type === 'table' ? '#c0c7d6' : undefined,
      chartColor: type === 'chart' || type === 'chartStack' ? '#005daa' : undefined,
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

export function useSlideCanvas(projectIdRef, slideIdRef, viewportIdRef = null) {
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

  function canRedo() {
    return redoStack.length > 0
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
      api.saveSlideCanvas(String(pid), sid, elements.value).catch((e) => {
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
      await api.saveSlideCanvas(String(pid), sid, elements.value)
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
    let nextStyle = prev.style
    if (patch.style) {
      nextStyle = { ...(prev.style || {}), ...patch.style }
      if (Object.prototype.hasOwnProperty.call(patch.style, 'crop') && patch.style.crop == null) {
        delete nextStyle.crop
      }
    }
    elements.value[idx] = {
      ...prev,
      ...patch,
      style: nextStyle,
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
    const viewportId = viewportIdRef?.value ?? 'mobile-375'
    const items = buildElementsFromSlide(slide, viewportId)
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
      fitIntent: layout.fitIntent || fit,
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
      fitIntent: layout.fitIntent || fit,
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
    canRedo,
    beginHistoryBatch,
    endHistoryBatch,
  }
}
