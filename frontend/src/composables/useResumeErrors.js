/** Resume API error helpers — use with errors from client.js (err.status). */

export function isQuotaExceeded(err) {
  if (!err) return false
  if (err.status === 402) return true
  const msg = String(err.message || '')
  return /用完|升级套餐|配额/.test(msg)
}

export function isResumeLimit(err) {
  if (!err) return false
  if (err.status === 409) return true
  const msg = String(err.message || '')
  return /Maximum|最多.*5|5.*resume/i.test(msg)
}

export function isFileTooLarge(err) {
  return err?.status === 413
}

export function isContentPolicy(err) {
  return err?.status === 422
}
