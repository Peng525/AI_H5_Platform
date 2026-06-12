/** 页面背景：兼容 hex 字符串与 { type, value } 对象 */
import { BACKGROUND_PRESET_COLORS, DEFAULT_CANVAS_BG } from '../constants/canvasBackgrounds.js'

export function normalizeSlideBackground(raw) {
  if (!raw) return { type: 'solid', value: DEFAULT_CANVAS_BG }
  if (typeof raw === 'string') {
    const v = raw.trim()
    if (v.startsWith('linear-gradient') || v.startsWith('radial-gradient')) {
      return { type: 'gradient', value: v }
    }
    return { type: 'solid', value: v || DEFAULT_CANVAS_BG }
  }
  if (typeof raw === 'object' && raw.value) {
    return {
      type: raw.type === 'gradient' ? 'gradient' : 'solid',
      value: String(raw.value),
    }
  }
  return { type: 'solid', value: DEFAULT_CANVAS_BG }
}

export function slideBackgroundCSSValue(raw) {
  return normalizeSlideBackground(raw).value
}

export function slideBackgroundToStorage(raw) {
  const n = normalizeSlideBackground(raw)
  if (n.type === 'gradient') return { type: 'gradient', value: n.value }
  return n.value
}

/** 提交 API 时 slideBackgrounds 值必须为 CSS 字符串 */
export function serializeSlideBackgroundForApi(raw) {
  return slideBackgroundCSSValue(raw)
}

export function serializeSlideBackgroundsForApi(map) {
  const out = {}
  for (const [key, val] of Object.entries(map || {})) {
    if (val == null || val === '') continue
    out[String(key)] = serializeSlideBackgroundForApi(val)
  }
  return out
}

function hexRelativeLuminance(hex) {
  const h = hex.replace('#', '').trim()
  if (h.length !== 3 && h.length !== 6) return 0.5
  const expand = h.length === 3 ? h.split('').map((c) => c + c).join('') : h
  const r = parseInt(expand.slice(0, 2), 16) / 255
  const g = parseInt(expand.slice(2, 4), 16) / 255
  const b = parseInt(expand.slice(4, 6), 16) / 255
  const lin = (c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)
  return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
}

/** 浅色背景（含经典白粉 #fafafa）上应使用深色文字 */
export function isLightSlideBackground(raw) {
  const css = slideBackgroundCSSValue(raw).toLowerCase()
  if (!css) return true
  if (css.includes('gradient')) {
    return /#fff(fff)?|#fafafa|#fce8f0|#f0f2f5|#f0f0f0|#dceefb|#f5e6d8|255,\s*255,\s*255|rgba\(255,\s*255,\s*255/i.test(
      css
    )
  }
  if (css.startsWith('#')) return hexRelativeLuminance(css) > 0.65
  return true
}

export function textColorForSlideBackground(raw) {
  return isLightSlideBackground(raw) ? '#0E2841' : '#FFFFFF'
}

function readLocalProjectSettings(projectId) {
  if (!projectId) return null
  try {
    const raw = localStorage.getItem(`ai_h5_project_settings_${projectId}`)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

/**
 * 统一解析页面画布背景 CSS 值。
 * 优先级：slide.canvas_background → settings.slideBackgrounds → generationMeta.background_preset → DEFAULT
 */
export function resolveSlideCanvasBackground(projectId, slide, settings) {
  const slideBg = slide?.canvas_background
  if (slideBg && String(slideBg).trim()) {
    return slideBackgroundCSSValue(slideBg)
  }

  const slideId = slide?.id
  if (slideId) {
    const key = String(slideId)
    const fromSettings = settings?.slideBackgrounds?.[key]
    if (fromSettings) return slideBackgroundCSSValue(fromSettings)

    const local = readLocalProjectSettings(projectId)
    const fromLocal = local?.slideBackgrounds?.[key]
    if (fromLocal) return slideBackgroundCSSValue(fromLocal)
  }

  const preset =
    settings?.generationMeta?.background_preset ??
    settings?.generationMeta?.backgroundPreset ??
    readLocalProjectSettings(projectId)?.generationMeta?.background_preset ??
    readLocalProjectSettings(projectId)?.generationMeta?.backgroundPreset

  if (preset && BACKGROUND_PRESET_COLORS[preset]) {
    return BACKGROUND_PRESET_COLORS[preset]
  }

  return slideBackgroundCSSValue(DEFAULT_CANVAS_BG)
}
