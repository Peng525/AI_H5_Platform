const PENDING_PREFIX = 'resume_pending_generate:'

function pendingKey(publicId) {
  return `${PENDING_PREFIX}${publicId}`
}

export function savePendingGenerate(publicId, payload) {
  if (!publicId) return
  try {
    sessionStorage.setItem(pendingKey(publicId), JSON.stringify(payload))
  } catch {
    /* ignore */
  }
}

export function loadPendingGenerate(publicId) {
  if (!publicId) return null
  try {
    const raw = sessionStorage.getItem(pendingKey(publicId))
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function clearPendingGenerate(publicId) {
  if (!publicId) return
  try {
    sessionStorage.removeItem(pendingKey(publicId))
  } catch {
    /* ignore */
  }
}
