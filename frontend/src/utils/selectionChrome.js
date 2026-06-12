import { isLightSlideBackground } from './slideBackground.js'
import { getTheme } from '../constants/designThemes.js'

const PRIMARY = '#005daa'
const DARK_ACCENT_FALLBACK = '#38BDF8'

/** 根据画布背景与主题返回选中框 / resize handle 的高对比配色 */
export function selectionChromeForBackground(bg, themeId = 'zjy-minimal') {
  const light = isLightSlideBackground(bg)
  const accent = getTheme(themeId)?.palette?.accent || DARK_ACCENT_FALLBACK

  if (light) {
    return {
      ringColor: PRIMARY,
      handleBg: PRIMARY,
      handleBorder: '#ffffff',
      shadow: '0 0 0 1px rgba(255,255,255,0.95), 0 0 0 4px rgba(0,93,170,0.28)',
      outlineWidth: 3,
    }
  }
  return {
    ringColor: accent,
    handleBg: accent,
    handleBorder: '#0f172a',
    shadow: '0 0 0 1px rgba(0,0,0,0.65), 0 0 0 4px rgba(56,189,248,0.35)',
    outlineWidth: 3,
  }
}
