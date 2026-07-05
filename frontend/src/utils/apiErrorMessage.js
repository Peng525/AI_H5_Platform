/** Normalize known English API errors to user-facing Chinese. */

const ERROR_REPLACEMENTS = [
  [/Internal Server Error/i, '服务器内部错误，请稍后重试'],
  [/Generation failed:/i, '生成失败：'],
  [/Optimize failed:/i, '优化失败：'],
  [/Maximum \d+ resumes per user/i, '简历数量已达上限，请先删除旧简历'],
  [/Thumbnail not found/i, '缩略图不存在'],
  [/Resume not found/i, '简历不存在或无权访问'],
  [/Resume expired/i, '简历已过期，请重新创建'],
  [/Input violates content policy/i, '内容不符合规范，请修改后重试'],
  [/PaddleOCR is not enabled/i, '当前环境未启用图片 OCR，请上传 PDF 或纯文本文件'],
]

export function normalizeUserErrorMessage(msg, status) {
  if (!msg) {
    if (status === 500) return '服务器内部错误，请稍后重试'
    if (status === 503) return '数据库结构需同步，请重启服务'
    return ''
  }
  let text = String(msg)
  for (const [pattern, replacement] of ERROR_REPLACEMENTS) {
    text = text.replace(pattern, replacement)
  }
  return text
}
