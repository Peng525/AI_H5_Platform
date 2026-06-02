const HEADING_RE = /^#{1,3}\s+/m
const CN_NUM_RE = /^[一二三四五六七八九十百]+[、．.]/m
const DIGIT_NUM_RE = /^\d+[.、)）]\s*/m

function splitByPattern(text, pattern) {
  const lines = text.split('\n')
  const chunks = []
  let current = []

  for (const line of lines) {
    if (pattern.test(line) && current.length > 0) {
      chunks.push(current.join('\n').trim())
      current = [line]
    } else {
      current.push(line)
    }
  }
  if (current.length) chunks.push(current.join('\n').trim())
  return chunks.filter(Boolean)
}

function splitIntoSections(text) {
  const trimmed = (text || '').trim()
  if (!trimmed) return []

  for (const re of [HEADING_RE, CN_NUM_RE, DIGIT_NUM_RE]) {
    const parts = splitByPattern(trimmed, re)
    if (parts.length > 1) return parts
  }

  const paragraphs = trimmed.split(/\n\s*\n/).map((p) => p.trim()).filter(Boolean)
  return paragraphs.length > 1 ? paragraphs : [trimmed]
}

function normalizeToCount(chunks, pageCount) {
  let arr = chunks.filter((c) => c.trim())
  if (arr.length === 0) return Array(pageCount).fill('')

  while (arr.length > pageCount) {
    let minIdx = 0
    let minLen = arr[0].length + (arr[1]?.length ?? Infinity)
    for (let i = 0; i < arr.length - 1; i++) {
      const len = arr[i].length + arr[i + 1].length
      if (len < minLen) {
        minLen = len
        minIdx = i
      }
    }
    arr.splice(minIdx, 2, `${arr[minIdx]}\n\n${arr[minIdx + 1]}`.trim())
  }

  while (arr.length < pageCount) {
    let longestIdx = 0
    for (let i = 1; i < arr.length; i++) {
      if (arr[i].length > arr[longestIdx].length) longestIdx = i
    }
    const chunk = arr[longestIdx]
    const mid = Math.floor(chunk.length / 2)
    let splitAt = chunk.indexOf('\n', mid)
    if (splitAt === -1) splitAt = mid
    const left = chunk.slice(0, splitAt).trim()
    const right = chunk.slice(splitAt).trim()
    if (!left || !right) break
    arr.splice(longestIdx, 1, left, right)
  }

  while (arr.length < pageCount) arr.push('')
  if (arr.length > pageCount) arr = arr.slice(0, pageCount)
  return arr
}

/**
 * 按标题/序号/段落规则将长文本拆分为 pageCount 段
 * @param {string} text
 * @param {number} pageCount
 * @returns {string[]}
 */
export function splitContentIntoPages(text, pageCount) {
  const n = Math.max(1, Math.min(30, pageCount))
  const sections = splitIntoSections(text)
  return normalizeToCount(sections, n)
}
