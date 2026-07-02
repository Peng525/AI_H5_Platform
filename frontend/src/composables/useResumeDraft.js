const DRAFT_KEY = 'ai_resume_draft'

const DEFAULT_DRAFT = {
  tab: 'resume-optimize',
  prompt: '',
  fileId: null,
  fileName: '',
  selectedPromptTemplateId: '',
  selectedVisualTemplateId: '',
}

export function loadResumeDraft() {
  try {
    const raw = sessionStorage.getItem(DRAFT_KEY)
    if (!raw) return { ...DEFAULT_DRAFT }
    const parsed = JSON.parse(raw)
    const tab = parsed.tab === 'resume' ? 'resume-optimize' : (parsed.tab || DEFAULT_DRAFT.tab)
    return { ...DEFAULT_DRAFT, ...parsed, tab }
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

export function resolveResumeTab(tab) {
  if (tab === 'resume-edit' || tab === 'resume-optimize') return tab
  if (tab === 'resume') return 'resume-optimize'
  return null
}
