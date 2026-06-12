import { getTheme } from '../constants/designThemes.js'
import { compileStructuredSlide, resolveSlideStructured } from './compileStructuredSlide.js'
import {
  slideBackgroundToStorage,
  slideBackgroundCSSValue,
  textColorForSlideBackground,
} from './slideBackground.js'

export const THEME_IDS = [
  'zjy-minimal',
  'eqxiu-story',
  'tech-blue',
  'dark-pro',
  'fresh-green',
  'coral-vivid',
  'lavender-soft',
  'ocean-calm',
  'sunset-warm',
  'minimal-gray',
  'elegant-gold',
  'berry-bold',
]

export function getThemeDefaultBackground(themeId) {
  const theme = getTheme(themeId)
  const gradient = theme.gradients?.[0]
  if (gradient?.value) {
    return { type: 'gradient', value: gradient.value }
  }
  return theme.colors.bg
}

export function remapElementColorsForTheme(elements, themeId, backgroundRaw) {
  const theme = getTheme(themeId)
  const textColor = textColorForSlideBackground(backgroundRaw)
  const { colors, fonts } = theme

  return (elements || []).map((el) => {
    const copy = { ...el, style: { ...(el.style || {}) } }
    if (el.type === 'text') {
      copy.style.color = textColor
      copy.style.fontFamily = fonts.body
      if (copy.style.fontWeight === 'bold' || (copy.style.fontSize || 0) >= 28) {
        copy.style.fontFamily = fonts.display
      }
    } else if (el.type === 'shape') {
      const isAccentBar = (el.height || 0) <= 8
      copy.style.background = isAccentBar ? colors.accent : copy.style.background || colors.bgMuted
    } else if (el.type === 'icon') {
      copy.style.color = colors.accent
    } else if (el.type === 'chartPlaceholder') {
      copy.style.background = colors.bgMuted
      copy.style.border = `2px dashed ${colors.textMuted}`
    }
    return copy
  })
}

/**
 * 全局切换主题：背景渐变 + 重编译/重映射 canvas 元素颜色
 */
export function applyProjectTheme({ slides, themeId, viewportId }) {
  const bgStorage = slideBackgroundToStorage(getThemeDefaultBackground(themeId))
  const slideBackgrounds = {}
  const updatedSlides = (slides || []).map((slide) => {
    const copy = { ...slide }
    slideBackgrounds[String(slide.id)] = bgStorage
    copy.canvas_background = bgStorage
    const structured = resolveSlideStructured(copy)
    if (structured) {
      copy.canvas_elements = compileStructuredSlide(structured, viewportId, themeId)
      copy._compiledViewportId = viewportId
    } else if (Array.isArray(copy.canvas_elements) && copy.canvas_elements.length) {
      copy.canvas_elements = remapElementColorsForTheme(copy.canvas_elements, themeId, bgStorage)
    }
    return copy
  })
  return {
    themeId,
    slideBackgrounds,
    slides: updatedSlides,
  }
}

export function listThemeOptions() {
  return THEME_IDS.map((id) => getThemePreview(id))
}

export function getThemePreview(themeId) {
  const theme = getTheme(themeId)
  const bgRaw = getThemeDefaultBackground(themeId)
  const accent = theme.colors.accent
  const accent2 = theme.colors.accent2 || theme.colors.bgMuted
  return {
    id: themeId,
    label: theme.label,
    palette: theme.palette.slice(0, 4),
    gradient: `linear-gradient(180deg, ${accent} 0%, ${accent2} 100%)`,
    swatch: theme.gradients?.[0]?.value || theme.colors.bg,
    backgroundCss: slideBackgroundCSSValue(bgRaw),
    titleFont: theme.fonts.display,
    bodyFont: theme.fonts.body,
    titleColor: theme.colors.text,
    bodyColor: theme.colors.textMuted,
    linkColor: theme.colors.accent,
  }
}
