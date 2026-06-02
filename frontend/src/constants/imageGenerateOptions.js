/** 生成页「生成图片」Tab 下拉选项 */

export const IMAGE_RATIO_OPTIONS = [
  { value: 'mobile', label: '9:16 移动端' },
  { value: 'web', label: '16:9 网页' },
]

export const IMAGE_COLOR_OPTIONS = [
  { value: 'classic_white', label: '经典白粉' },
  { value: 'light_gray', label: '浅灰' },
  { value: 'dark', label: '深色' },
  { value: 'colorful', label: '多彩' },
]

export const IMAGE_STYLE_OPTIONS = [
  { value: '扁平插画', label: '扁平插画' },
  { value: '3D质感', label: '3D质感' },
  { value: '水彩插画', label: '水彩插画' },
  { value: '商务专业', label: '商务专业' },
  { value: '摄影写实', label: '摄影写实' },
]

const styleValues = new Set(IMAGE_STYLE_OPTIONS.map((o) => o.value))

export function isValidImageStyle(style) {
  return styleValues.has(style)
}

export function getImageColorLabel(value) {
  return IMAGE_COLOR_OPTIONS.find((o) => o.value === value)?.label || value
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
