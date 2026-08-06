/** Resolve deck PPT template preview URL (supports URL-encoded paths). */
export function resolveDeckPreviewUrl(url) {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:')) {
    return url
  }
  const raw = url.startsWith('/') ? url : `/${url}`
  const q = raw.indexOf('?')
  const pathPart = q >= 0 ? raw.slice(0, q) : raw
  const queryPart = q >= 0 ? raw.slice(q) : ''
  const encoded = pathPart
    .split('/')
    .map((seg) => {
      if (!seg) return seg
      try {
        return encodeURIComponent(decodeURIComponent(seg))
      } catch {
        return encodeURIComponent(seg)
      }
    })
    .join('/')
  return encoded + queryPart
}
