/** 生成页「生成图片」Tab 下拉选项 */

export const IMAGE_RATIO_OPTIONS = [
  { value: '1:1', label: '1:1', iconW: 12, iconH: 12, viewportMode: 'mobile' },
  { value: '16:9', label: '16:9', iconW: 16, iconH: 9, viewportMode: 'web' },
  { value: '4:3', label: '4:3', iconW: 16, iconH: 12, viewportMode: 'web' },
  { value: '3:4', label: '3:4', iconW: 12, iconH: 16, viewportMode: 'mobile' },
  { value: '4:5', label: '4:5', iconW: 13, iconH: 16, viewportMode: 'mobile' },
  { value: '9:16', label: '9:16', iconW: 9, iconH: 16, viewportMode: 'mobile' },
]

export const IMAGE_COLOR_OPTIONS = [
  { value: '', label: '无' },
  { value: 'classic_white', label: '经典白粉' },
  { value: 'light_gray', label: '浅灰' },
  { value: 'dark', label: '深色' },
  { value: 'colorful', label: '多彩' },
]

/** 演示文稿生成页背景（与后端 BACKGROUND_COLORS 一致） */
export const DECK_BACKGROUND_OPTIONS = [
  { value: '', label: '无' },
  { value: 'classic_white', label: '经典白粉' },
  { value: 'light_gray', label: '浅灰' },
]

export const IMAGE_STYLE_OPTIONS = [
  { value: '', label: '无' },
  { value: '扁平插画', label: '扁平插画' },
  { value: '3D质感', label: '3D质感' },
  { value: '水彩插画', label: '水彩插画' },
  { value: '商务专业', label: '商务专业' },
  { value: '摄影写实', label: '摄影写实' },
]

const styleValues = new Set(
  IMAGE_STYLE_OPTIONS.map((o) => o.value).filter(Boolean)
)

export function getImageRatioOption(value) {
  return IMAGE_RATIO_OPTIONS.find((o) => o.value === value) || IMAGE_RATIO_OPTIONS[5]
}

export function aspectRatioToViewportMode(ratio) {
  return getImageRatioOption(ratio).viewportMode
}

export function aspectRatioToPresetId(ratio) {
  return aspectRatioToViewportMode(ratio) === 'web' ? 'web-1280' : 'mobile-375'
}

/** 从旧 draft viewportMode 推断比例 */
export function viewportModeToAspectRatio(viewportMode) {
  if (viewportMode === 'web') return '16:9'
  return '9:16'
}

export function isValidImageStyle(style) {
  return Boolean(style) && styleValues.has(style)
}

export function getImageColorLabel(value) {
  return IMAGE_COLOR_OPTIONS.find((o) => o.value === value)?.label || value
}

/** 缩放比例图标至 max 边长 */
export function scaleRatioIcon(iconW, iconH, max = 16) {
  const scale = max / Math.max(iconW, iconH)
  return {
    width: Math.round(iconW * scale),
    height: Math.round(iconH * scale),
  }
}

/** 若 prompt 未含风格/色调，追加元数据行 */
export function enrichImagePrompt(prompt, { imageStyle, imageColor }) {
  const text = (prompt || '').trim()
  if (!text) return text
  const parts = []
  if (imageStyle && !text.includes('风格')) {
    parts.push(`风格：${imageStyle}`)
  }
  const colorLabel = getImageColorLabel(imageColor)
  if (imageColor && colorLabel && !text.includes('色调') && !text.includes('颜色')) {
    parts.push(`色调：${colorLabel}`)
  }
  if (!parts.length) return text
  return `${text}\n${parts.join('；')}`
}
