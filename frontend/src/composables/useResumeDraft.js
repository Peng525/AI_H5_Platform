const DRAFT_KEY = 'ai_resume_draft'

const DEFAULT_DRAFT = {
  prompt: '',
  fileId: null,
  fileName: '',
  selectedTemplateId: '',
}

export function loadResumeDraft() {
  try {
    const raw = sessionStorage.getItem(DRAFT_KEY)
    if (!raw) return { ...DEFAULT_DRAFT }
    return { ...DEFAULT_DRAFT, ...JSON.parse(raw) }
  } catch {
    return { ...DEFAULT_DRAFT }
  }
}

export function saveResumeDraft(partial) {
  const next = { ...loadResumeDraft(), ...partial }
  sessionStorage.setItem(DRAFT_KEY, JSON.stringify(next))
  return next
}

export function clearResumeDraft() {
  sessionStorage.removeItem(DRAFT_KEY)
}
