const STORAGE_KEY = 'ai_create_draft'
const LAST_RESULT_KEY = 'ai_last_result_public_id'
const GENERATE_JOB_KEY = 'ai_generate_job'
const SHOULD_REVEAL_KEY = 'ai_should_reveal'
const RETURN_TO_RESULT_KEY = 'ai_return_to_result'

/** 结果页 pending 路由占位 publicId */
export const PENDING_RESULT_PUBLIC_ID = '_pending'

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
  themeId: 'zjy-minimal',
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

/** 最近一次成功生成对应的结果页 public_id */
export function getLastGenerateResultPublicId() {
  try {
    const fallback = sessionStorage.getItem(LAST_RESULT_KEY)
    if (fallback) return String(fallback)
  } catch {
    /* ignore */
  }
  const draft = loadDraft()
  const allowed = draft.lastGeneratedPublicId ?? draft.lastGeneratedProjectId
  if (allowed == null || allowed === '') return null
  return String(allowed)
}

export function getGenerateResultPath() {
  const publicId = getLastGenerateResultPublicId()
  if (!publicId) return null
  return `/create/generate/result/${publicId}`
}

/** 从生成结果页主动离开（点主页或返回编辑器）时写入 */
export function markReturnToResult(publicId) {
  const id = String(publicId || '').trim()
  if (!id || id === PENDING_RESULT_PUBLIC_ID) return
  try {
    sessionStorage.setItem(RETURN_TO_RESULT_KEY, id)
  } catch {
    /* ignore */
  }
}

export function getReturnToResultPublicId() {
  try {
    const id = sessionStorage.getItem(RETURN_TO_RESULT_KEY)
    return id ? String(id) : null
  } catch {
    return null
  }
}

export function getReturnToResultPath() {
  const publicId = getReturnToResultPublicId()
  if (!publicId) return null
  if (!canAccessGenerateResult(publicId)) {
    clearReturnToResult()
    return null
  }
  return `/create/generate/result/${publicId}`
}

export function clearReturnToResult() {
  try {
    sessionStorage.removeItem(RETURN_TO_RESULT_KEY)
  } catch {
    /* ignore */
  }
}

export function saveGenerateJob(body, meta = {}) {
  sessionStorage.setItem(
    GENERATE_JOB_KEY,
    JSON.stringify({ body, createdAt: Date.now(), ...meta })
  )
}

export function loadGenerateJob() {
  try {
    const raw = sessionStorage.getItem(GENERATE_JOB_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function clearGenerateJob() {
  sessionStorage.removeItem(GENERATE_JOB_KEY)
}

export function markShouldRevealDeck() {
  try {
    sessionStorage.setItem(SHOULD_REVEAL_KEY, '1')
  } catch {
    /* ignore */
  }
}

export function consumeShouldRevealDeck() {
  try {
    const v = sessionStorage.getItem(SHOULD_REVEAL_KEY)
    sessionStorage.removeItem(SHOULD_REVEAL_KEY)
    return v === '1'
  } catch {
    return false
  }
}

/** Review 提交生成任务后，或已成功生成并写入 lastGeneratedPublicId 后，允许进入结果页 */
export function canAccessGenerateResult(publicId) {
  const id = String(publicId || '')
  if (id === PENDING_RESULT_PUBLIC_ID) {
    return !!loadGenerateJob()
  }
  const allowed = getLastGenerateResultPublicId()
  if (!allowed) return false
  return String(allowed) === id
}

export function grantGenerateResultAccess(publicId) {
  const id = String(publicId)
  saveDraft({ lastGeneratedPublicId: id })
  try {
    sessionStorage.setItem(LAST_RESULT_KEY, id)
  } catch {
    /* ignore */
  }
}

export function applyProjectSettingsLocal(publicId, settings) {
  const prefix = 'ai_h5_project_settings_'
  localStorage.setItem(
    prefix + String(publicId),
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
