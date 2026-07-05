import { defaultStructured } from './resumeBind.js'

export function createPageId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return `page-${crypto.randomUUID()}`
  }
  return `page-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

export function cloneJson(value) {
  return JSON.parse(JSON.stringify(value ?? {}))
}

/** Normalize legacy single-page visual_document into pages[]. */
export function normalizePages(visualDocument, fallbackStructured) {
  const raw = visualDocument?.pages
  if (Array.isArray(raw) && raw.length > 0) {
    return raw.map((p) => ({
      id: p.id || createPageId(),
      structured: { ...defaultStructured(), ...(p.structured || {}) },
      styles: { ...(p.styles || {}) },
    }))
  }
  return [
    {
      id: createPageId(),
      structured: { ...defaultStructured(), ...(fallbackStructured || {}) },
      styles: { ...(visualDocument?.styles || {}) },
    },
  ]
}

export function blankPage() {
  return {
    id: createPageId(),
    structured: defaultStructured(),
    styles: {},
  }
}

export function duplicatePage(page) {
  return {
    id: createPageId(),
    structured: cloneJson(page.structured),
    styles: cloneJson(page.styles || {}),
  }
}

export function pagesToVisualDocument(visualDocument, pages) {
  const vd = { ...(visualDocument || {}) }
  vd.pages = pages.map((p) => ({
    id: p.id,
    structured: p.structured,
    styles: p.styles || {},
  }))
  if (pages[0]?.styles) {
    vd.styles = { ...pages[0].styles }
  }
  return vd
}
