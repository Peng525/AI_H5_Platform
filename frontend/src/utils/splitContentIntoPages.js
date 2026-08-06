/**
 * 内容切分工具 — 语义感知版本
 *
 * 核心原则：绝不从一个标题的正文中间切开。
 * 宁可 pageCount 不完全匹配，也不破坏内容完整性。
 */

/** H1/H2/H3 标题检测 */
const H1_RE = /^#\s+/m
const H2_RE = /^##\s+/m
const H3_RE = /^###\s+/m
/** 中文数字标题：一、 二、 三、 */
const CN_NUM_RE = /^[一二三四五六七八九十百]+[、．.]\s*/m
/** 阿拉伯数字标题：1. 2) 3、 4.1 4.2 等 */
const DIGIT_NUM_RE = /^\d+(?:\.\d+)*[.、)）]\s*/m

/** 所有标题模式的优先级（越靠前越高级） */
const HEADING_PATTERNS = [
  { re: H1_RE, level: 1, name: 'h1' },
  { re: H2_RE, level: 2, name: 'h2' },
  { re: CN_NUM_RE, level: 2, name: 'cn_num' },
  { re: DIGIT_NUM_RE, level: 3, name: 'digit_num' },
  { re: H3_RE, level: 3, name: 'h3' },
]

/**
 * 判断一行是否匹配某个标题模式
 * @returns {{ level: number, name: string } | null}
 */
function detectHeading(line) {
  const trimmed = line.trim()
  if (!trimmed) return null
  for (const pat of HEADING_PATTERNS) {
    if (pat.re.test(trimmed)) return { level: pat.level, name: pat.name }
  }
  return null
}

/**
 * 将文本按标题拆分为带层级信息的节
 * @returns {Array<{ heading: string, body: string, level: number }>}
 */
function splitToSections(text) {
  const lines = text.split('\n')
  const sections = []
  let currentHeading = ''
  let currentBody = []
  let currentLevel = 4 // 无标题 = 最低优先级

  for (const line of lines) {
    const h = detectHeading(line)
    if (h) {
      // 遇到新标题 → 保存前一节
      if (currentBody.length > 0 || currentHeading) {
        sections.push({
          heading: currentHeading,
          body: currentBody.join('\n').trim(),
          level: currentLevel,
        })
      }
      currentHeading = line.trim()
      currentBody = []
      currentLevel = h.level
    } else {
      currentBody.push(line)
    }
  }
  // 最后一节
  if (currentBody.length > 0 || currentHeading) {
    sections.push({
      heading: currentHeading,
      body: currentBody.join('\n').trim(),
      level: currentLevel,
    })
  }

  return sections
}

/**
 * 把 level=3 的小节合并到前面最近的 level=1 或 level=2 的大节中
 * 返回合并后的节列表（层级最高为2）
 */
function mergeSubsections(sections) {
  if (sections.length <= 1) return sections

  const merged = []
  let buffer = null

  for (const sec of sections) {
    if (sec.level <= 2) {
      // 遇到大标题 → 先保存前一个 buffer
      if (buffer) {
        merged.push(buffer)
        buffer = null
      }
      // 开始新的 buffer
      buffer = {
        heading: sec.heading,
        body: sec.body,
        level: sec.level,
      }
    } else {
      // level >= 3 的小节 → 合并到 buffer
      if (buffer) {
        buffer.body = [buffer.body, sec.heading, sec.body]
          .filter(Boolean).join('\n\n').trim()
      } else {
        // 孤立的小节，独立成段
        merged.push({ ...sec })
      }
    }
  }
  if (buffer) merged.push(buffer)

  return merged
}

/**
 * 将节列表适配为目标页数（语义感知版）
 *
 * 策略：
 * - 节过多 → 合并最短的相邻两节（优先合并不含标题的节）
 * - 节过少 → 不对半切分！返回实际节数，多余页留空
 */
function normalizeToCount(sections, pageCount) {
  const arr = sections.filter((s) => s.heading || s.body)

  if (arr.length === 0) {
    return Array(pageCount).fill('')
  }

  // ── 节过多：合并（语义感知）──
  while (arr.length > pageCount) {
    // 优先找"无标题的节"来合并（它们是前一个节的延续）
    let mergeIdx = -1
    for (let i = 1; i < arr.length; i++) {
      if (!arr[i].heading || arr[i].level >= 3) {
        mergeIdx = i - 1
        break
      }
    }
    // 没有无标题的节 → 合并最短的相邻两节
    if (mergeIdx === -1) {
      let minLen = Infinity
      for (let i = 0; i < arr.length - 1; i++) {
        const combinedLen = (arr[i].body || '').length + (arr[i + 1].body || '').length
        if (combinedLen < minLen) {
          minLen = combinedLen
          mergeIdx = i
        }
      }
    }

    const a = arr[mergeIdx]
    const b = arr[mergeIdx + 1]
    const mergedHeading = a.heading || b.heading
    const mergedBody = [a.body, b.body].filter(Boolean).join('\n\n')
    arr.splice(mergeIdx, 2, { heading: mergedHeading, body: mergedBody, level: Math.min(a.level, b.level) })
  }

  // ── 节过少：不对半切分！──
  // 只做轻量拆分：如果某一节特别长（超过平均长度2倍），且包含换行，尝试在段落边界处分开
  if (arr.length < pageCount) {
    const targetLen = arr.reduce((sum, s) => sum + (s.body || '').length, 0) / arr.length
    const expanded = []
    for (const s of arr) {
      const bodyLen = (s.body || '').length
      if (bodyLen > targetLen * 2 && bodyLen > 200 && expanded.length < pageCount) {
        // 尝试在段落边界分开（双换行）
        const paras = s.body.split(/\n\s*\n/)
        if (paras.length >= 2) {
          const mid = Math.floor(paras.length / 2)
          const first = paras.slice(0, mid).join('\n\n').trim()
          const second = paras.slice(mid).join('\n\n').trim()
          if (first && second) {
            expanded.push({ heading: s.heading, body: first, level: s.level })
            expanded.push({ heading: '', body: second, level: s.level + 1 })
            continue
          }
        }
      }
      expanded.push(s)
    }

    // 如果还是不够 → 剩余的页留空（让AI自由发挥）
    while (expanded.length < pageCount) {
      expanded.push({ heading: '', body: '', level: 4 })
    }
    return expanded.map((s) => {
      if (s.heading && s.body) return `${s.heading}\n${s.body}`
      if (s.heading) return s.heading
      return s.body || ''
    })
  }

  return arr.map((s) => {
    if (s.heading && s.body) return `${s.heading}\n${s.body}`
    if (s.heading) return s.heading
    return s.body || ''
  })
}

/**
 * 将长文本按语义拆分为 pageCount 段
 * - 优先按标题层级切分
 * - 子节（H3/digit_num）合并到父节，不会独立占页
 * - 绝不对半切开一个标题的内容
 * - 如果内容不足以填满所有页面，剩余页留空由AI补充
 *
 * @param {string} text - 用户输入的原始文本
 * @param {number} pageCount - 期望的页数
 * @returns {string[]} - 每页的内容片段
 */
export function splitContentIntoPages(text, pageCount) {
  const n = Math.max(1, Math.min(30, pageCount || 1))
  const trimmed = (text || '').trim()
  if (!trimmed) return Array(n).fill('')

  const sections = splitToSections(trimmed)
  const merged = mergeSubsections(sections)

  // 如果合并后全是无标题段落（没有检测到任何标题）
  if (merged.every((s) => !s.heading)) {
    // 按段落切分
    const paras = trimmed.split(/\n\s*\n/).map((p) => p.trim()).filter(Boolean)
    if (paras.length <= 1) return [trimmed, ...Array(Math.max(0, n - 1)).fill('')]
    return normalizeToCount(
      paras.map((p) => ({ heading: '', body: p, level: 4 })),
      n
    )
  }

  return normalizeToCount(merged, n)
}
