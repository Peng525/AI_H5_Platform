/**
 * 按归一化裁切框导出图片 blob URL
 * @param {string} imageUrl
 * @param {{ x: number, y: number, width: number, height: number }} crop
 * @returns {Promise<string>}
 */
export function cropImageToBlobUrl(imageUrl, crop) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      const sx = Math.round(crop.x * img.naturalWidth)
      const sy = Math.round(crop.y * img.naturalHeight)
      const sw = Math.max(1, Math.round(crop.width * img.naturalWidth))
      const sh = Math.max(1, Math.round(crop.height * img.naturalHeight))
      const canvas = document.createElement('canvas')
      canvas.width = sw
      canvas.height = sh
      const ctx = canvas.getContext('2d')
      if (!ctx) {
        reject(new Error('无法创建画布'))
        return
      }
      ctx.drawImage(img, sx, sy, sw, sh, 0, 0, sw, sh)
      canvas.toBlob(
        (blob) => {
          if (!blob) {
            reject(new Error('裁切失败'))
            return
          }
          resolve(URL.createObjectURL(blob))
        },
        'image/png',
        0.92
      )
    }
    img.onerror = () => reject(new Error('图片加载失败'))
    img.src = imageUrl
  })
}

/**
 * @param {string} url blob 或 http url
 * @returns {Promise<Blob>}
 */
export async function urlToBlob(url) {
  const res = await fetch(url)
  return res.blob()
}
