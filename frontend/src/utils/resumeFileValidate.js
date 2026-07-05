export const RESUME_FILE_ACCEPT = '.pdf,.png,.jpg,.jpeg,image/*,application/pdf'
export const RESUME_FILE_MAX_BYTES = 5 * 1024 * 1024

export function validateResumeFile(file) {
  if (!file) return { ok: false, error: '未选择文件' }
  if (file.size > RESUME_FILE_MAX_BYTES) {
    return { ok: false, error: '文件超过 5MB 限制' }
  }
  return { ok: true, file }
}

export function formatResumeFileLabel(fileName) {
  if (!fileName) return '文件'
  const lower = fileName.toLowerCase()
  if (lower.endsWith('.pdf')) return 'PDF'
  if (lower.endsWith('.png')) return 'PNG'
  if (lower.endsWith('.jpg') || lower.endsWith('.jpeg')) return 'JPG'
  if (lower.endsWith('.doc') || lower.endsWith('.docx')) return 'DOC'
  const dot = fileName.lastIndexOf('.')
  if (dot > 0 && dot < fileName.length - 1) {
    return fileName.slice(dot + 1).toUpperCase()
  }
  return '文件'
}
