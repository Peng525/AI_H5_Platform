/** 将 DOM 元素导出为 PNG 并下载或返回 data URL */

export async function captureElement(el, options = {}) {
  if (!el) throw new Error('无有效元素')
  const html2canvas = (await import('html2canvas')).default
  const canvas = await html2canvas(el, {
    backgroundColor: options.backgroundColor ?? null,
    scale: options.scale ?? 2,
    useCORS: true,
    logging: false,
    ...options,
  })
  return canvas
}

export function canvasToDataUrl(canvas, type = 'image/png', quality = 0.92) {
  return canvas.toDataURL(type, quality)
}

export function downloadDataUrl(dataUrl, filename = 'export.png') {
  const a = document.createElement('a')
  a.href = dataUrl
  a.download = filename
  a.click()
}

export async function downloadElementAsPng(el, filename = 'export.png', options = {}) {
  const canvas = await captureElement(el, options)
  downloadDataUrl(canvasToDataUrl(canvas), filename)
}

export async function elementToDataUrl(el, options = {}) {
  const canvas = await captureElement(el, options)
  return canvasToDataUrl(canvas)
}
