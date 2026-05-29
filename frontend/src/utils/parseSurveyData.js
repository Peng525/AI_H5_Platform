/** 解析问卷/统计表格为文字云词条 */

const TEXT_HEADERS = ['词', '选项', '关键词', 'keyword', 'word', 'text', '名称', '标签']
const WEIGHT_HEADERS = ['票', '数', '权重', 'weight', 'count', '频次', '比例', '人数', 'value', '票数']

function parseNumber(val) {
  if (val == null || val === '') return null
  const n = Number(String(val).replace(/[%％,，]/g, '').trim())
  return Number.isFinite(n) && n > 0 ? n : null
}

function detectDelimiter(line) {
  if (line.includes('\t')) return '\t'
  if (line.includes(';')) return ';'
  return ','
}

function splitRow(line, delim) {
  const parts = []
  let cur = ''
  let inQuote = false
  for (let i = 0; i < line.length; i++) {
    const c = line[i]
    if (c === '"') {
      inQuote = !inQuote
      continue
    }
    if (!inQuote && (c === delim || c === '\t')) {
      parts.push(cur.trim())
      cur = ''
      continue
    }
    cur += c
  }
  parts.push(cur.trim())
  return parts.map((p) => p.replace(/^"|"$/g, ''))
}

function findColumnIndex(headers, candidates) {
  const lower = headers.map((h) => String(h).toLowerCase())
  for (const c of candidates) {
    const idx = lower.findIndex((h) => h.includes(c.toLowerCase()))
    if (idx >= 0) return idx
  }
  return -1
}

function mergeWords(list) {
  const map = new Map()
  for (const { text, weight } of list) {
    const t = String(text || '').trim()
    if (!t) continue
    const w = Number(weight) || 50
    map.set(t, (map.get(t) || 0) + w)
  }
  return [...map.entries()].map(([text, weight]) => ({ text, weight }))
}

export function wordsFromManual(tags) {
  const list = (tags || []).map((t) => {
    if (typeof t === 'string') return { text: t, weight: 50 }
    return { text: t.text || '', weight: t.weight ?? 50 }
  })
  return mergeWords(list)
}

export function parseTableText(text) {
  const lines = String(text || '')
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter(Boolean)
  if (!lines.length) return []

  const delim = detectDelimiter(lines[0])
  const rows = lines.map((l) => splitRow(l, delim))
  const headers = rows[0]
  let textIdx = findColumnIndex(headers, TEXT_HEADERS)
  let weightIdx = findColumnIndex(headers, WEIGHT_HEADERS)

  const dataRows = textIdx >= 0 || weightIdx >= 0 ? rows.slice(1) : rows
  if (textIdx < 0 && weightIdx < 0) {
    textIdx = 0
    weightIdx = rows[0].length > 1 ? 1 : -1
  }

  const list = dataRows.map((row) => {
    const text = row[textIdx >= 0 ? textIdx : 0]
    const weightRaw = weightIdx >= 0 ? row[weightIdx] : null
    return { text, weight: parseNumber(weightRaw) ?? 50 }
  })
  return mergeWords(list)
}

export function parseFrequencyFromText(text) {
  const tokens = String(text || '')
    .split(/[\s,，;；、\n\r\t]+/)
    .map((t) => t.trim())
    .filter((t) => t.length >= 2)
  const map = new Map()
  for (const t of tokens) map.set(t, (map.get(t) || 0) + 1)
  return [...map.entries()].map(([text, weight]) => ({ text, weight }))
}

export async function parseUploadedFile(file) {
  const name = (file?.name || '').toLowerCase()
  if (name.endsWith('.csv') || name.endsWith('.txt')) {
    const text = await file.text()
    return parseTableText(text)
  }
  if (name.endsWith('.xlsx') || name.endsWith('.xls')) {
    const XLSX = await import('xlsx')
    const buf = await file.arrayBuffer()
    const wb = XLSX.read(buf, { type: 'array' })
    const sheet = wb.Sheets[wb.SheetNames[0]]
    const csv = XLSX.utils.sheet_to_csv(sheet)
    return parseTableText(csv)
  }
  throw new Error('仅支持 .csv / .txt / .xlsx 文件')
}

export function toWordCloudList(words) {
  return (words || []).map((w) => [w.text, w.weight])
}

export function defaultWordCloudContent() {
  return {
    words: [
      { text: '年轻人', weight: 120 },
      { text: '性价比', weight: 95 },
      { text: '文旅', weight: 80 },
      { text: 'AI', weight: 70 },
      { text: '创新', weight: 60 },
    ],
    shapeId: 'cloud',
    customMaskUrl: '',
    fontFamily: 'system',
    maxFontSize: 80,
    minFontSize: 14,
    density: 'normal',
    rotation: 'random',
    colorMode: 'auto',
    colors: [],
    backgroundColor: '#ffffff',
    backgroundAlpha: 1,
  }
}
