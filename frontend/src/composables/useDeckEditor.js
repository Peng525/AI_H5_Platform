import { computed, onMounted, onUnmounted, ref, watch, unref } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import { api } from '../api/client'
import { useAuth } from './useAuth'
import { registerCanvasFlush, unregisterCanvasFlush } from './useEditorCanvasSave'
import { useSlideCanvas, defaultElement } from './useSlideCanvas'
import { useProjectEditorSettings } from './useProjectEditorSettings'
import { useBgmPlayer } from './useBgmPlayer'
import { useToast } from './useToast.js'
import { buildBlock, getDefaultBlockBackground, resetLayoutBlockIds, resolveStoredLayoutElements } from '../constants/layoutBlocks.js'
import { useLayoutCatalog } from './useLayoutCatalog.js'
import { normalizeChatScript, serializeChatScript } from '../utils/chatScript.js'
import { applyProjectTheme } from '../utils/applyProjectTheme.js'
import { compileSlideIfNeeded, shouldCompileSlide, ensureSlideCompiled, compileRemainingSlides, resolveSlideStructured } from '../utils/compileStructuredSlide.js'
import { serializeSlideBackgroundForApi, serializeSlideBackgroundsForApi, resolveSlideCanvasBackground } from '../utils/slideBackground.js'
import { DEFAULT_WEB_VIEWPORT_ID } from '../constants/editorPresets.js'
import { fitTextElementBox } from '../utils/measureTextBlock.js'

const COACH_KEY = 'ai_h5_editor_coach_seen'

/**
 * 演示项目编辑器核心 composable。
 * 分区：项目加载/保存 · 结构化编译 · 画布 CRUD（useSlideCanvas）· 主题/设置 · 模态与 AI 配图。
 * layoutMode: 'studio' 单页画布 + 顶栏工具栏；'result' 纵览多页 + 浮动 EditorContextLayer。
 */
export function useDeckEditor(projectIdSource, options = {}) {
  const layoutMode = options.layoutMode || 'studio'
  const onProjectLoaded = options.onProjectLoaded
  const onProjectLoadError = options.onProjectLoadError
  const initialProjectRef = options.initialProject
  const adminPresetId = computed(() => options.adminPresetId?.value ?? options.adminPresetId ?? '')
  const adminLayoutId = computed(() => options.adminLayoutId?.value ?? options.adminLayoutId ?? '')
  const isAdminEditorMode = computed(() => !!(adminPresetId.value || adminLayoutId.value))
  const projectId = computed(() => {
    const v = typeof projectIdSource === 'function' ? projectIdSource() : unref(projectIdSource)
    return v
  })

  function apiProjectRef() {
    return project.value?.public_id || String(projectId.value || '')
  }

const { error: toastError, success: toastSuccess } = useToast()

const { user } = useAuth()
const isWideLayout = ref(true)
const toolboxDrawerOpen = ref(false)
const aiDrawerOpen = ref(false)
const adminActionsOpen = ref(false)
const adminLayoutActionsOpen = ref(false)
const adminActionsRef = ref(null)
const adminLayoutActionsRef = ref(null)

const toolboxPanelClass = computed(() => {
  if (!isAdminEditorMode.value || isWideLayout.value) return 'shrink-0 flex min-h-0'
  return toolboxDrawerOpen.value
    ? 'fixed left-0 top-14 bottom-0 z-[56] flex min-h-0 shadow-xl'
    : 'hidden shrink-0'
})

const aiPanelClass = computed(() => {
  if (!isAdminEditorMode.value || isWideLayout.value) return 'shrink-0 flex min-h-0'
  return aiDrawerOpen.value
    ? 'fixed right-0 top-14 bottom-0 z-[56] flex min-h-0 shadow-xl'
    : 'hidden shrink-0'
})

function closeAdminDrawers() {
  toolboxDrawerOpen.value = false
  aiDrawerOpen.value = false
}

function onAdminPptxMenuImport(e) {
  adminActionsOpen.value = false
  onAdminPptxImport(e)
}

function onAdminActionsClickOutside(e) {
  if (adminActionsRef.value && !adminActionsRef.value.contains(e.target)) {
    adminActionsOpen.value = false
  }
  if (adminLayoutActionsRef.value && !adminLayoutActionsRef.value.contains(e.target)) {
    adminLayoutActionsOpen.value = false
  }
}

let layoutMq = null
function onLayoutMqChange(e) {
  isWideLayout.value = e.matches
  if (e.matches) closeAdminDrawers()
}
const project = ref(null)
const current = ref(null)
const imageLoading = ref(false)
const aiPanelRef = ref(null)
const resultRailRef = ref(null)
const quota = ref({ remaining: 5, total: 5 })
const previewAnimation = ref('')
const previewAnimationTick = ref(0)
const shortcutsHelpOpen = ref(false)
const dialogueGeneratorOpen = ref(false)
const wordCloudOpen = ref(false)
const wordCloudEditContent = ref(null)
const chartStackOpen = ref(false)
const chartStackEditContent = ref(null)
const chartEditMode = ref('chartStack')
const showDialoguePreview = ref(false)
const cropModalOpen = ref(false)
const cropTargetId = ref(null)
const cropImageUrl = ref('')
const cropInitial = ref(null)
const projectLoading = ref(true)
const loadError = ref('')
const deleteSlideConfirm = ref(null)
const presetSaveOpen = ref(false)
const layoutSaveOpen = ref(false)
const pptImporting = ref(false)
const templateMeta = ref(null)
const layoutMeta = ref(null)
const showEditorCoach = ref(false)
const editingSlideId = ref(null)

const { settings, viewport, setViewport, setScrollEffect, getSlideBackground, setSlideBackground, applyFromServer, setBgm, setThemeId, save: saveSettings } = useProjectEditorSettings(projectId)

const layoutCatalog = useLayoutCatalog()
const primaryLayoutItems = computed(() => layoutCatalog.getPrimaryLayoutItems())
const moreLayoutItems = computed(() => layoutCatalog.getMoreLayoutItems())

const {
  active: bgmActive,
  muted: bgmMuted,
  playing: bgmPlaying,
  toggleMute: toggleBgmMute,
} = useBgmPlayer(settings)

const bgmSpinning = computed(() => bgmPlaying.value && !bgmMuted.value)

const canvasBackground = computed(() => {
  if (!current.value) return resolveSlideCanvasBackground(projectId.value, null, settings.value)
  return resolveSlideCanvasBackground(projectId.value, current.value, settings.value)
})

const slideIdRef = computed(() => current.value?.id ?? null)
const viewportIdRef = computed(() => settings.value.viewportId || 'mobile-375')
const {
  elements,
  selectedIds,
  selectedId,
  saveElements,
  loadElements,
  addElement: addElementRaw,
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
  replaceAllElements,
  appendLayoutElements,
  addImageFromAi,
  applyImageFitToSelected,
  flushCanvasSave,
  undo,
  redo,
  canUndo,
  canRedo,
  beginHistoryBatch,
  endHistoryBatch,
} = useSlideCanvas(projectId, slideIdRef, viewportIdRef)

const dragState = ref(null)
const pendingDragElementId = ref(null)

function getCanvasContentBounds() {
  const vp = viewport.value
  const chrome = vp.device === 'mobile' ? 28 : 32
  return { width: vp.width, height: vp.height - chrome }
}

function addElement(type, overrides = {}) {
  const hasPos =
    Object.prototype.hasOwnProperty.call(overrides, 'x') ||
    Object.prototype.hasOwnProperty.call(overrides, 'y')
  if (!hasPos) {
    const bounds = getCanvasContentBounds()
    const temp = defaultElement(type, overrides)
    overrides = {
      ...overrides,
      x: Math.max(0, Math.round((bounds.width - temp.width) / 2)),
      y: Math.max(0, Math.round((bounds.height - temp.height) / 2)),
    }
  }
  return addElementRaw(type, overrides)
}

function recompileSlidesForViewport(viewportId) {
  if (!project.value?.slides?.length) return
  const themeId = settings.value.themeId || 'zjy-minimal'
  for (const s of project.value.slides) {
    if (shouldCompileSlide(s, viewportId)) {
      s.canvas_elements = compileSlideIfNeeded(s, viewportId, themeId)
    }
  }
  if (current.value) {
    const slide = project.value.slides.find((s) => s.id === current.value.id)
    if (slide?.canvas_elements?.length) {
      loadElements(slide.canvas_elements)
      current.value = { ...current.value, canvas_elements: slide.canvas_elements }
    }
  }
}

function onViewportChange(viewportId) {
  const prev = settings.value.viewportId
  setViewport(viewportId)
  if (prev === viewportId) return
  recompileSlidesForViewport(viewportId)
}

const slideIndex = computed(() => {
  if (!project.value?.slides || !current.value) return 0
  return project.value.slides.findIndex((s) => s.id === current.value.id)
})

async function loadTemplateMeta() {
  if (!adminPresetId.value) {
    templateMeta.value = null
    return
  }
  try {
    templateMeta.value = await api.getAdminTemplate(adminPresetId.value)
  } catch {
    templateMeta.value = null
  }
}

async function loadLayoutMeta() {
  if (!adminLayoutId.value) {
    layoutMeta.value = null
    return
  }
  try {
    layoutMeta.value = await api.getAdminLayout(adminLayoutId.value)
  } catch {
    layoutMeta.value = {
      id: adminLayoutId.value,
      label: adminLayoutId.value,
      icon: 'dashboard',
      group: 'custom',
      placement: 'more',
      sort_order: 100,
      enabled: true,
    }
  }
}

async function openLayoutSave() {
  await flushCanvasSave()
  await loadLayoutMeta()
  layoutSaveOpen.value = true
}

async function onLayoutSaved() {
  toastSuccess('版式已保存')
  await layoutCatalog.reload()
  await loadLayoutMeta()
}

async function openPresetSave() {
  await flushCanvasSave()
  presetSaveOpen.value = true
}

async function onPresetSaved() {
  toastSuccess('模板预设已保存')
  await loadTemplateMeta()
}

async function onAdminPptxImport(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file || !adminPresetId.value) return
  pptImporting.value = true
  try {
    await flushCanvasSave()
    const fd = new FormData()
    fd.append('file', file)
    fd.append('project_public_id', apiProjectRef())
    fd.append('device', templateMeta.value?.device || 'mobile')
    if (templateMeta.value?.title) fd.append('title', templateMeta.value.title)
    await api.importPptxToTemplateDraft(adminPresetId.value, fd)
    toastSuccess('PPT 已导入到当前草稿')
    await load()
  } catch (err) {
    toastError(err.message)
  } finally {
    pptImporting.value = false
  }
}

async function applyProjectPayload(p) {
  project.value = p
  applyFromServer(p.settings)
  if (p.generation_meta) {
    settings.value = {
      ...settings.value,
      generationMeta: {
        ...(settings.value.generationMeta || {}),
        ...p.generation_meta,
      },
    }
  }
  current.value = p.slides?.[0] || null
  showDialoguePreview.value = !!current.value?.chat_script?.enabled
  if (layoutMode === 'result') {
    normalizeResultViewport()
  }
  const vp = settings.value.viewportId || DEFAULT_WEB_VIEWPORT_ID
  const themeId = settings.value.themeId || 'zjy-minimal'
  const slideList = p.slides || []
  for (const s of slideList) {
    ensureSlideCompiled(s, vp, themeId)
  }
  loadElements(current.value?.canvas_elements)
  if (layoutMode !== 'result' && current.value && !elements.value.length) {
    syncFromSlide(current.value)
  }
  const q = await api.getQuota()
  quota.value = { remaining: q.quota_remaining, total: q.quota_total }
  if (layoutMode === 'result') {
    normalizeResultViewport()
  }
  onProjectLoaded?.(p)
}

async function load() {
  projectLoading.value = true
  loadError.value = ''
  const pid = String(projectId.value || '')
  try {
    let payload = null
    const cached = initialProjectRef?.value
    if (cached && String(cached.public_id) === pid) {
      payload = cached
      initialProjectRef.value = null
    } else {
      payload = await api.getProject(pid)
    }
    await applyProjectPayload(payload)
  } catch (e) {
    console.error('[useDeckEditor] load failed', pid, e)
    loadError.value = e.message || '加载失败'
    onProjectLoadError?.(loadError.value)
  } finally {
    projectLoading.value = false
  }
}

function dismissEditorCoach() {
  showEditorCoach.value = false
  localStorage.setItem(COACH_KEY, '1')
}

function onBgmChange(patch) {
  setBgm(patch)
}

onMounted(() => {
  registerCanvasFlush(flushCanvasSave)
  window.addEventListener('keydown', onKeyDown)
  document.addEventListener('click', onAdminActionsClickOutside)
  layoutMq = window.matchMedia('(min-width: 1024px)')
  isWideLayout.value = layoutMq.matches
  layoutMq.addEventListener('change', onLayoutMqChange)
  layoutCatalog.load()
  if (!isAdminEditorMode.value && layoutMode === 'studio') {
    showEditorCoach.value = !localStorage.getItem(COACH_KEY)
  }
  loadTemplateMeta()
  loadLayoutMeta()
  load()
})
watch(adminPresetId, loadTemplateMeta)
watch(adminLayoutId, loadLayoutMeta)
watch(projectId, (id) => {
  if (id) load()
})
onBeforeRouteLeave(async () => {
  await flushCanvasSave()
})

function normalizeResultViewport() {
  if (layoutMode !== 'result' || !project.value) return
  const vid = settings.value.viewportId || 'mobile-375'
  const targetVid = String(vid).startsWith('web') ? vid : DEFAULT_WEB_VIEWPORT_ID
  if (targetVid !== vid) {
    setViewport(targetVid)
  }
  recompileSlidesForViewport(targetVid)
}

function compileAllSlidesLazy(skipFirst = false) {
  if (!project.value?.slides?.length) return
  const vp = settings.value.viewportId || DEFAULT_WEB_VIEWPORT_ID
  const themeId = settings.value.themeId || 'zjy-minimal'
  compileRemainingSlides(project.value.slides, vp, themeId, skipFirst)
}

function selectSlideInternal(slide) {
  const sameSlide = current.value?.id === slide.id
  if (!sameSlide) {
    saveElements()
    current.value = slide
    loadElements(slide.canvas_elements)
    if (!elements.value.length) syncFromSlide(slide)
  }
  showDialoguePreview.value = !!slide?.chat_script?.enabled
}

function deselectCurrentSlide() {
  if (!current.value) return
  saveElements()
  current.value = null
  loadElements([])
  clearSelection()
  showDialoguePreview.value = false
}

async function exitSlideEdit() {
  if (!editingSlideId.value) return
  await flushCanvasSave()
  editingSlideId.value = null
}

async function enterSlideEdit(id) {
  if (editingSlideId.value && editingSlideId.value !== id) {
    await exitSlideEdit()
  }
  const slide = project.value?.slides?.find((s) => s.id === id)
  if (!slide) return
  if (current.value?.id !== id) selectSlideInternal(slide)
  editingSlideId.value = id
}

async function selectSlide(slide) {
  if (layoutMode === 'result') {
    await flushCanvasSave()
  } else if (editingSlideId.value && editingSlideId.value !== slide.id) {
    await exitSlideEdit()
  }
  selectSlideInternal(slide)
}

async function addSlide(insertAfterSlideId = null) {
  if (adminLayoutId.value) {
    toastError('版式编辑仅支持单页画布')
    return
  }
  saveElements()
  try {
    const body = {
      title: '新页面',
      subtitle: '',
      bullets: [],
      layout: 'bullets',
      animation: 'fade',
    }
    if (insertAfterSlideId != null) {
      body.insert_after_slide_id = insertAfterSlideId
    }
    const slide = await api.addSlide(apiProjectRef(), body)
    insertSlideInList(slide, insertAfterSlideId)
    finishNewSlide(slide)
    return slide
  } catch (e) {
    toastError(e.message)
    return null
  }
}

function insertSlideInList(slide, afterSlideId) {
  if (!project.value?.slides) return
  const slides = project.value.slides
  if (afterSlideId == null) {
    slides.push(slide)
    return
  }
  const idx = slides.findIndex((s) => s.id === afterSlideId)
  if (idx >= 0) slides.splice(idx + 1, 0, slide)
  else slides.push(slide)
}

async function addSlideAfter(afterSlideId) {
  const slide = await addSlide(afterSlideId)
  return slide
}

const slideGenerating = ref(false)
const generateCardContext = ref({ afterSlideId: null })

async function generateSlideAfter(afterSlideId, { prompt, templateHint, language }) {
  if (adminLayoutId.value) {
    toastError('版式编辑不支持 AI 生成')
    return null
  }
  await flushCanvasSave()
  slideGenerating.value = true
  try {
    const slide = await api.generateAiSlide(apiProjectRef(), {
      prompt,
      insert_after_slide_id: afterSlideId ?? undefined,
      replace_slide_id: afterSlideId ?? undefined,
      template_hint: templateHint || 'magic',
      language: language || settings.value.aiLanguage || '简体中文',
    })
    const refreshed = await api.getProject(apiProjectRef())
    await applyProjectPayload(refreshed)
    const nextSlide = refreshed.slides?.find((s) => s.id === slide.id) || slide
    finishNewSlide(nextSlide)
    await refreshQuota()
    toastSuccess('卡片已生成')
    return nextSlide
  } catch (e) {
    toastError(e.message)
    return null
  } finally {
    slideGenerating.value = false
  }
}

function finishNewSlide(slide) {
  current.value = slide
  loadElements(slide.canvas_elements)
  if (!elements.value.length) syncFromSlide(slide)
}

function applyLayoutBlock(blockId, slideId = null, { mode = 'append' } = {}) {
  const sid = slideId ?? current.value?.id
  if (!sid) return
  if (slideId && slideId !== current.value?.id) {
    current.value = project.value.slides.find((s) => s.id === slideId) || current.value
    loadElements([])
  }
  resetLayoutBlockIds()
  const catalogItem = layoutCatalog.getCatalogBlock(blockId)
  const stored = resolveStoredLayoutElements(catalogItem, settings.value.viewportId)
  const els = stored ?? buildBlock(blockId, settings.value.viewportId, settings.value.themeId || 'zjy-minimal')
  if (mode === 'replace') {
    replaceAllElements(els)
    const bg =
      catalogItem?.canvas_background ||
      getDefaultBlockBackground(settings.value.themeId || 'zjy-minimal')
    setSlideBackground(sid, bg)
  } else {
    appendLayoutElements(els)
  }
}

async function removeSlide(slideId) {
  if (adminLayoutId.value) {
    toastError('版式编辑仅支持单页画布')
    return
  }
  if ((project.value.slides?.length || 0) <= 1) {
    toastError('至少保留一页')
    return
  }
  deleteSlideConfirm.value = slideId
}

async function onDeleteSlideConfirm() {
  const slideId = deleteSlideConfirm.value
  if (!slideId) return
  deleteSlideConfirm.value = null
  saveElements()
  try {
    await api.deleteSlide(apiProjectRef(), slideId)
    localStorage.removeItem(`ai_h5_canvas_${apiProjectRef()}_${slideId}`)
    project.value.slides = project.value.slides.filter((s) => s.id !== slideId)
    if (current.value?.id === slideId) {
      current.value = project.value.slides[0]
      loadElements()
    }
    toastSuccess('页面已删除')
  } catch (e) {
    toastError(e.message)
  }
}

async function saveSlideFields(fields) {
  if (!current.value) return
  try {
    const updated = await api.updateSlide(apiProjectRef(), current.value.id, fields)
    const idx = project.value.slides.findIndex((s) => s.id === updated.id)
    if (idx >= 0) project.value.slides[idx] = updated
    current.value = {
      ...updated,
      chat_script: updated.chat_script ?? fields.chat_script ?? current.value.chat_script,
    }
  } catch (e) {
    toastError(e.message || '保存页面失败')
    console.error(e)
  }
}

function syncCanvasFromSlide() {
  if (!current.value) return
  elements.value = []
  syncFromSlide(current.value)
}

function addMaterial(item) {
  if (item.type === 'text') {
    addElement('text', {
      content: '在此输入文字',
      height: 56,
      style: {
        background: '#ffffff',
        border: '1px solid #c0c7d6',
        borderRadius: 2,
      },
    })
  } else if (item.type === 'shape') {
    addElement('shape', {
      style: { background: '#005daa', borderRadius: 0 },
      width: 120,
      height: 80,
    })
  } else if (item.type === 'table') {
    addElement('table', {
      style: {
        background: '#ffffff',
        headerBackground: '#005daa',
        headerColor: '#ffffff',
        borderColor: '#c0c7d6',
      },
    })
  } else if (item.type === 'icon') {
    addElement('icon', {
      content: item.icon || 'emoji_objects',
      style: {
        background: '#e8f0fe',
        color: '#005daa',
        borderRadius: 8,
      },
    })
  } else if (item.type === 'image') {
    addElement('image', {
      content: 'https://placehold.co/200x120/005daa/white?text=Image',
      width: 200,
      height: 120,
      style: { background: '#f0f0f0' },
    })
  } else if (item.type === 'chart') {
    addElement('chart', {
      style: { background: '#ffffff', chartColor: '#005daa' },
    })
  } else if (item.type === 'chartStack') {
    const vp = viewport.value
    addElement('chartStack', {
      x: Math.round((vp.width - 320) / 2),
      y: 80,
    })
  } else if (item.type === 'wordcloud') {
    wordCloudOpen.value = true
  }
}

function openDialogueGenerator() {
  dialogueGeneratorOpen.value = true
}

async function onInsertDialogue(script) {
  if (!current.value) return
  const serialized = serializeChatScript({ ...normalizeChatScript(script), enabled: true })
  const bg = serialized.style?.background || '#ededed'

  setSlideBackground(current.value.id, bg)
  replaceAllElements([])
  await flushCanvasSave()
  dialogueGeneratorOpen.value = false

  try {
    const updated = await api.updateSlide(apiProjectRef(), current.value.id, {
      chat_script: serialized,
      layout: 'chat',
      title: current.value.title || '对话页',
      subtitle: '',
      bullets: [],
    })
    const idx = project.value.slides.findIndex((s) => s.id === updated.id)
    if (idx >= 0) project.value.slides[idx] = updated
    current.value = { ...updated, chat_script: serialized }
    showDialoguePreview.value = true
  } catch (e) {
    toastError(e.message || '插入对话失败，请重试')
    console.error(e)
  }
}

function onInsertWordCloud(content) {
  wordCloudOpen.value = false
  wordCloudEditContent.value = null
  if (selectedId.value) {
    const el = elements.value.find((e) => e.id === selectedId.value)
    if (el?.type === 'wordcloud') {
      updateElement(selectedId.value, { content })
      return
    }
  }
  const vp = viewport.value
  addElement('wordcloud', {
    x: Math.round((vp.width - 280) / 2),
    y: 80,
    width: 280,
    height: 200,
    content,
  })
}

function onEditWordCloud(el) {
  wordCloudEditContent.value = el.content
  wordCloudOpen.value = true
}

function onEditChartStack(el) {
  const target = el?.type ? el : selectedId.value ? elements.value.find((e) => e.id === selectedId.value) : null
  if (target?.type === 'chart') {
    chartEditMode.value = 'chart'
    chartStackEditContent.value = target.content || null
  } else if (target?.type === 'chartStack' || el?.content) {
    chartEditMode.value = 'chartStack'
    chartStackEditContent.value = el?.content || target?.content || null
  } else if (selectedId.value) {
    const selected = elements.value.find((e) => e.id === selectedId.value)
    if (selected?.type === 'chart') {
      chartEditMode.value = 'chart'
      chartStackEditContent.value = selected.content
    } else if (selected?.type === 'chartStack') {
      chartEditMode.value = 'chartStack'
      chartStackEditContent.value = selected.content
    } else {
      chartEditMode.value = 'chartStack'
      chartStackEditContent.value = null
    }
  } else {
    chartEditMode.value = 'chartStack'
    chartStackEditContent.value = null
  }
  chartStackOpen.value = true
}

function onSaveChartStack(content) {
  chartStackOpen.value = false
  const targetId = selectedId.value
  if (chartEditMode.value === 'chart') {
    if (targetId) {
      const el = elements.value.find((e) => e.id === targetId)
      if (el?.type === 'chart') {
        updateElement(targetId, { content })
        chartStackEditContent.value = null
        return
      }
    }
    const vp = viewport.value
    addElement('chart', {
      x: Math.round((vp.width - 200) / 2),
      y: 80,
      width: 200,
      height: 120,
      content,
      style: { background: '#ffffff', chartColor: '#005daa' },
    })
    chartStackEditContent.value = null
    return
  }
  if (targetId) {
    const el = elements.value.find((e) => e.id === targetId)
    if (el?.type === 'chartStack') {
      updateElement(targetId, { content })
      chartStackEditContent.value = null
      return
    }
  }
  const vp = viewport.value
  addElement('chartStack', {
    x: Math.round((vp.width - 320) / 2),
    y: 80,
    content,
  })
  chartStackEditContent.value = null
}

function onInsertWordCloudImage(dataUrl) {
  wordCloudOpen.value = false
  const vp = viewport.value
  addElement('image', {
    x: Math.round((vp.width - 280) / 2),
    y: 80,
    width: 280,
    height: 200,
    content: dataUrl,
    style: { background: 'transparent', objectFit: 'contain' },
  })
}

function onCanvasBgChange(color) {
  if (current.value?.id) setSlideBackground(current.value.id, color)
}

function addImagePlaceholder() {
  addElement('image', {
    content: 'https://placehold.co/200x120/005daa/white?text=Image',
    width: 200,
    height: 120,
  })
}

function onStyleChange(patch) {
  if (!selectedId.value) return
  const el = elements.value.find((e) => e.id === selectedId.value)
  if (!el) return
  const mergedStyle = { ...(el.style || {}), ...patch }
  const update = { style: mergedStyle }
  if (el.type === 'text') {
    const vp = viewport.value
    const bounds = vp ? { width: vp.width, height: vp.height } : { width: 9999, height: 9999 }
    const fit = fitTextElementBox({ ...el, style: mergedStyle }, el.content, bounds)
    if (fit) Object.assign(update, fit)
  }
  updateElement(selectedId.value, update)
}

function onDuplicate() {
  if (selectedIds.value.length > 1) duplicateSelected()
  else if (selectedId.value) duplicateElement(selectedId.value)
}

function onDeleteSelected() {
  if (selectedIds.value.length > 1) removeSelected()
  else if (selectedId.value) removeElement(selectedId.value)
}

function onBringFront() {
  if (selectedIds.value.length > 1) bringSelectedToFront()
  else if (selectedId.value) bringToFront(selectedId.value)
}

function onSendBack() {
  sendSelectedToBack()
}

function onBringForward() {
  bringSelectedForward()
}

function onSendBackward() {
  sendSelectedBackward()
}

function onCenterElement(axis) {
  if (!selectedId.value) return
  const el = elements.value.find((e) => e.id === selectedId.value)
  if (!el) return
  const bounds = getCanvasContentBounds()
  const patch = {}
  if (axis === 'h' || axis === 'both') {
    patch.x = Math.max(0, Math.min(Math.round((bounds.width - el.width) / 2), bounds.width - el.width))
  }
  if (axis === 'v' || axis === 'both') {
    patch.y = Math.max(0, Math.min(Math.round((bounds.height - el.height) / 2), bounds.height - el.height))
  }
  updateElement(selectedId.value, patch)
}

function onSelectElement({ id, ctrlKey, shiftKey }) {
  if (ctrlKey) {
    selectElement(id, { toggle: true })
    return
  }
  if (shiftKey) {
    selectElement(id, { additive: true })
    return
  }
  if (!selectedIds.value.includes(id)) {
    selectElement(id)
  }
}

function onMarqueeSelect({ ids, additive }) {
  if (!ids.length && !additive) {
    clearSelection()
    return
  }
  selectElements(ids, { additive })
}

function onBatchStart(dragElementId) {
  beginHistoryBatch()
  pendingDragElementId.value = dragElementId || null
}

function onMoveDelta({ dx, dy }) {
  if (!pendingDragElementId.value) return
  if (!dragState.value) {
    const dragElementId = pendingDragElementId.value
    const ids = selectedIds.value.includes(dragElementId) ? [...selectedIds.value] : [dragElementId]
    dragState.value = {
      ids,
      origins: Object.fromEntries(
        ids.map((sid) => {
          const el = elements.value.find((e) => e.id === sid)
          return [sid, { x: el?.x ?? 0, y: el?.y ?? 0 }]
        })
      ),
    }
  }
  const { ids, origins } = dragState.value
  const bounds = getCanvasContentBounds()
  for (const sid of ids) {
    const origin = origins[sid]
    if (!origin) continue
    const el = elements.value.find((e) => e.id === sid)
    const w = el?.width ?? 0
    const h = el?.height ?? 0
    updateElement(sid, {
      x: Math.max(0, Math.min(origin.x + dx, bounds.width - w)),
      y: Math.max(0, Math.min(origin.y + dy, bounds.height - h)),
    })
  }
}

function onBatchEnd() {
  pendingDragElementId.value = null
  dragState.value = null
  endHistoryBatch()
}

function onKeyDown(e) {
  const editing = ['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)
  if (e.key === 'F1') {
    e.preventDefault()
    shortcutsHelpOpen.value = !shortcutsHelpOpen.value
    return
  }
  if ((e.ctrlKey || e.metaKey) && e.key === '/' && !editing) {
    e.preventDefault()
    shortcutsHelpOpen.value = true
    return
  }
  if (shortcutsHelpOpen.value) return
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z' && !e.shiftKey) {
    if (editing) return
    e.preventDefault()
    undo()
    return
  }
  if ((e.ctrlKey || e.metaKey) && (e.key.toLowerCase() === 'y' || (e.key.toLowerCase() === 'z' && e.shiftKey))) {
    if (editing) return
    e.preventDefault()
    redo()
    return
  }
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'c' && !editing) {
    if (!selectedIds.value.length) return
    e.preventDefault()
    copySelected()
    return
  }
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'v' && !editing) {
    e.preventDefault()
    pasteClipboard()
    return
  }
  if (e.key === 'Delete' && selectedIds.value.length && !editing) {
    e.preventDefault()
    if (selectedIds.value.length > 1) removeSelected()
    else removeElement(selectedId.value)
  }
}

onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown)
  document.removeEventListener('click', onAdminActionsClickOutside)
  layoutMq?.removeEventListener('change', onLayoutMqChange)
  unregisterCanvasFlush()
})

async function refreshQuota() {
  const q = await api.getQuota()
  quota.value = { remaining: q.quota_remaining, total: q.quota_total }
}

async function onGenerateImage({
  prompt,
  channelTier,
  channel,
  style,
  viewportPresetId,
  viewportWidth,
  viewportHeight,
  fitMode: genFitMode,
}) {
  if (!prompt?.trim() || !project.value) return
  imageLoading.value = true
  aiPanelRef.value?.setImageError('')
  resultRailRef.value?.setImageError('')
  try {
    const result = await api.generateImage(apiProjectRef(), {
      prompt,
      tier: channelTier,
      channel: channel || undefined,
      style,
      fit_mode: genFitMode || undefined,
      viewport_preset_id: viewportPresetId || undefined,
      viewport_width: viewportWidth || undefined,
      viewport_height: viewportHeight || undefined,
    })
    aiPanelRef.value?.setGeneratedImage(result)
    resultRailRef.value?.setGeneratedImage(result)
    await refreshQuota()
  } catch (e) {
    aiPanelRef.value?.setImageError(e.message)
    resultRailRef.value?.setImageError(e.message)
  } finally {
    imageLoading.value = false
  }
}

function onAddImageToPage({ url, width, height, fitMode }) {
  if (!url) return
  addImageFromAi(url, fitMode || 'width', viewport.value, { width, height })
}

function onImageFit(fit) {
  applyImageFitToSelected(fit, viewport.value)
}

function onImageLayout(mode) {
  const id = selectedId.value
  if (!id) return
  const el = elements.value.find((e) => e.id === id)
  if (!el || el.type !== 'image') return
  const vp = viewport.value
  const margin = 24
  const presets = {
    left: {
      x: margin,
      y: margin,
      width: Math.round(vp.width * 0.45 - margin),
      height: vp.height - margin * 2,
    },
    right: {
      x: Math.round(vp.width * 0.55),
      y: margin,
      width: Math.round(vp.width * 0.45 - margin),
      height: vp.height - margin * 2,
    },
    top: {
      x: margin,
      y: margin,
      width: vp.width - margin * 2,
      height: Math.round(vp.height * 0.42 - margin),
    },
  }
  const patch = presets[mode]
  if (patch) updateElement(id, patch)
}

async function onRegenerateSelectedImage({ prompt, useReferenceImage } = {}) {
  const id = selectedId.value
  if (!id) return
  const el = elements.value.find((e) => e.id === id)
  if (!el || el.type !== 'image') return
  const trimmed =
    (prompt || '').trim() ||
    el.style?.imagePrompt ||
    el.meta?.prompt ||
    ''
  if (!trimmed) {
    toastError('请输入画面描述')
    return
  }
  const refUrl =
    useReferenceImage && typeof el.content === 'string' && el.content.trim()
      ? el.content.trim()
      : undefined
  imageLoading.value = true
  try {
    const vp = viewport.value
    const result = await api.generateImage(apiProjectRef(), {
      prompt: trimmed,
      use_reference_image: Boolean(refUrl),
      reference_image_url: refUrl,
      fit_mode: el.fitIntent || 'width',
      viewport_preset_id: settings.value.viewportId,
      viewport_width: vp?.width,
      viewport_height: vp?.height,
    })
    updateElement(id, {
      content: result.image_url,
      style: { ...(el.style || {}), imagePrompt: trimmed },
    })
    await refreshQuota()
    toastSuccess('图片已更新')
  } catch (e) {
    toastError(e.message)
  } finally {
    imageLoading.value = false
  }
}

const textEditingId = ref(null)

function onTextEditStart(elementId) {
  textEditingId.value = elementId
}

function onTextEditEnd() {
  textEditingId.value = null
}

function onImageCrop() {
  const id = selectedId.value
  if (!id) return
  const el = elements.value.find((e) => e.id === id)
  if (!el || el.type !== 'image' || !el.content) return
  cropTargetId.value = id
  cropImageUrl.value = el.content
  cropInitial.value = el.style?.crop || null
  cropModalOpen.value = true
}

function onCropConfirm(crop) {
  if (!cropTargetId.value) return
  updateElement(cropTargetId.value, {
    style: { crop },
  })
  cropModalOpen.value = false
}

function onCropReset() {
  if (!cropTargetId.value) return
  updateElement(cropTargetId.value, { style: { crop: null } })
  cropInitial.value = null
}

function onPreviewAnimation(anim) {
  previewAnimation.value = anim
  previewAnimationTick.value += 1
}

async function applyGlobalTheme(themeId) {
  if (!project.value?.slides?.length) return
  const vp = settings.value.viewportId || DEFAULT_WEB_VIEWPORT_ID
  const result = applyProjectTheme({
    slides: project.value.slides,
    themeId,
    viewportId: vp,
  })
  setThemeId(themeId)
  settings.value = {
    ...settings.value,
    themeId,
    slideBackgrounds: { ...settings.value.slideBackgrounds, ...result.slideBackgrounds },
  }
  saveSettings()
  project.value.slides = result.slides
  for (const s of result.slides) {
    const idx = project.value.slides.findIndex((x) => x.id === s.id)
    if (idx >= 0) project.value.slides[idx] = s
  }
  if (current.value) {
    const updated = result.slides.find((s) => s.id === current.value.id)
    if (updated) {
      current.value = updated
      loadElements(updated.canvas_elements || [])
      saveElements()
    }
  }
  try {
    await api.updateProjectSettings(apiProjectRef(), {
      viewportId: settings.value.viewportId,
      scrollEffect: settings.value.scrollEffect,
      themeId: settings.value.themeId,
      showScrollHint: settings.value.showScrollHint,
      slideBackgrounds: serializeSlideBackgroundsForApi(settings.value.slideBackgrounds),
      bgm: settings.value.bgm,
      defaultChatTapToContinue: settings.value.defaultChatTapToContinue,
    })
    for (const s of result.slides) {
      const patch = {}
      if (s.canvas_background) {
        patch.canvas_background = serializeSlideBackgroundForApi(s.canvas_background)
      }
      if (Object.keys(patch).length) {
        await api.updateSlide(apiProjectRef(), s.id, patch)
      }
      if (s.canvas_elements?.length) {
        await api.saveSlideCanvas(apiProjectRef(), s.id, s.canvas_elements)
      }
    }
  } catch (e) {
    toastError(e.message || '主题保存失败')
    return
  }
  toastSuccess('已应用主题')
}
  return {
    layoutMode,
    projectId,
    adminPresetId,
    adminLayoutId,
    isAdminEditorMode,
    isWideLayout,
    toolboxDrawerOpen,
    aiDrawerOpen,
    adminActionsOpen,
    adminLayoutActionsOpen,
    adminActionsRef,
    adminLayoutActionsRef,
    toolboxPanelClass,
    aiPanelClass,
    closeAdminDrawers,
    onAdminPptxMenuImport,
    onAdminActionsClickOutside,
    project,
    current,
    imageLoading,
    aiPanelRef,
    resultRailRef,
    quota,
    previewAnimation,
    previewAnimationTick,
    shortcutsHelpOpen,
    dialogueGeneratorOpen,
    wordCloudOpen,
    wordCloudEditContent,
    chartStackOpen,
    chartStackEditContent,
    chartEditMode,
    showDialoguePreview,
    cropModalOpen,
    cropImageUrl,
    cropInitial,
    projectLoading,
    loadError,
    deleteSlideConfirm,
    presetSaveOpen,
    layoutSaveOpen,
    pptImporting,
    templateMeta,
    layoutMeta,
    showEditorCoach,
    editingSlideId,
    enterSlideEdit,
    exitSlideEdit,
    settings,
    viewport,
    setViewport,
    onViewportChange,
    setScrollEffect,
    getSlideBackground,
    setSlideBackground,
    applyFromServer,
    setBgm,
    primaryLayoutItems,
    moreLayoutItems,
    bgmActive,
    bgmMuted,
    bgmPlaying,
    toggleBgmMute,
    bgmSpinning,
    canvasBackground,
    slideIdRef,
    elements,
    selectedIds,
    selectedId,
    saveElements,
    loadElements,
    addElement,
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
    replaceAllElements,
    appendLayoutElements,
    addImageFromAi,
    applyImageFitToSelected,
    flushCanvasSave,
    undo,
    redo,
    canUndo,
    canRedo,
    beginHistoryBatch,
    endHistoryBatch,
    slideIndex,
    load,
    dismissEditorCoach,
    onBgmChange,
    selectSlide,
    deselectCurrentSlide,
    addSlide,
    addSlideAfter,
    generateSlideAfter,
    slideGenerating,
    generateCardContext,
    finishNewSlide,
    applyLayoutBlock,
    removeSlide,
    onDeleteSlideConfirm,
    saveSlideFields,
    syncCanvasFromSlide,
    addMaterial,
    openDialogueGenerator,
    onInsertDialogue,
    onInsertWordCloud,
    onEditWordCloud,
    onEditChartStack,
    onSaveChartStack,
    onInsertWordCloudImage,
    onCanvasBgChange,
    addImagePlaceholder,
    onStyleChange,
    onDuplicate,
    onDeleteSelected,
    onBringFront,
    onSendBack,
    onBringForward,
    onSendBackward,
    onCenterElement,
    onSelectElement,
    onMarqueeSelect,
    onBatchStart,
    onMoveDelta,
    onBatchEnd,
    onKeyDown,
    refreshQuota,
    onGenerateImage,
    onAddImageToPage,
    onImageFit,
    onImageLayout,
    onRegenerateSelectedImage,
    onImageCrop,
    onTextEditStart,
    onTextEditEnd,
    textEditingId,
    onCropConfirm,
    onCropReset,
    onPreviewAnimation,
    openLayoutSave,
    onLayoutSaved,
    openPresetSave,
    onPresetSaved,
    onAdminPptxImport,
    loadTemplateMeta,
    loadLayoutMeta,
    applyGlobalTheme,
    compileAllSlidesLazy,
  }
}
