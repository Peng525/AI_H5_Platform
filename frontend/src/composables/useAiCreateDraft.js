const STORAGE_KEY = 'ai_create_draft'

export const DEFAULT_DRAFT = {
  type: 'deck',
  pageCount: 10,
  background: '',
  viewportMode: 'auto',
  imageColor: '',
  imageAspectRatio: '9:16',
  imageStyle: '',
  language: '简体中文',
  topic: '',
  audience: '',
  tone: '专业、清晰、具说服力',
  textDensity: '精炼',
  extraContent: '',
  extraInstructions: '',
  contentMode: 'free',
  cardSplitMode: null,
  pageContents: [],
}

/** 将 pageContents 长度对齐到 pageCount（补空或截断） */
export function syncPageContents(pageContents, pageCount) {
  const n = Math.max(1, Math.min(30, pageCount))
  const arr = Array.isArray(pageContents) ? [...pageContents] : []
  while (arr.length < n) arr.push('')
  if (arr.length > n) arr.length = n
  return arr
}

export function loadDraft() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return { ...DEFAULT_DRAFT }
    return { ...DEFAULT_DRAFT, ...JSON.parse(raw) }
  } catch {
    return { ...DEFAULT_DRAFT }
  }
}

export function saveDraft(patch) {
  const next = { ...loadDraft(), ...patch }
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(next))
  return next
}

export function clearDraft() {
  sessionStorage.removeItem(STORAGE_KEY)
}

export function requireDeckDraft(router) {
  const draft = loadDraft()
  if (draft.type !== 'deck') {
    router.replace('/create/generate')
    return null
  }
  return draft
}

export function applyProjectSettingsLocal(projectId, settings) {
  const prefix = 'ai_h5_project_settings_'
  localStorage.setItem(
    prefix + projectId,
    JSON.stringify({
      viewportId: settings.viewportId || 'mobile-375',
      scrollEffect: settings.scrollEffect || 'vertical',
      themeId: settings.themeId || 'zjy-minimal',
      showScrollHint: settings.showScrollHint === true,
      slideBackgrounds: settings.slideBackgrounds || {},
      bgm: settings.bgm || { enabled: false, trackId: '', url: '', loop: true, volume: 0.35 },
      defaultChatTapToContinue: settings.defaultChatTapToContinue !== false,
    })
  )
}
