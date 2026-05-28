/** 页面背景：兼容 hex 字符串与 { type, value } 对象 */
export function normalizeSlideBackground(raw) {
  if (!raw) return { type: 'solid', value: '#005daa' }
  if (typeof raw === 'string') {
    const v = raw.trim()
    if (v.startsWith('linear-gradient') || v.startsWith('radial-gradient')) {
      return { type: 'gradient', value: v }
    }
    return { type: 'solid', value: v || '#005daa' }
  }
  if (typeof raw === 'object' && raw.value) {
    return {
      type: raw.type === 'gradient' ? 'gradient' : 'solid',
      value: String(raw.value),
    }
  }
  return { type: 'solid', value: '#005daa' }
}

export function slideBackgroundCSSValue(raw) {
  return normalizeSlideBackground(raw).value
}

export function slideBackgroundToStorage(raw) {
  const n = normalizeSlideBackground(raw)
  if (n.type === 'gradient') return { type: 'gradient', value: n.value }
  return n.value
}
