/** Resolve resume template preview URL for dev (Vite) and prod (FastAPI static). */
export function resolveResumePreviewUrl(url) {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:')) {
    return url
  }
  const path = url.startsWith('/') ? url : `/${url}`
  return path
}
