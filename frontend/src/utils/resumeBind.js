/** Bind path helpers for resume structured JSON (mirrors backend visual_compiler). */

export function getBindValue(structured, bind) {
  if (!bind || !structured) return ''
  const topArr = bind.match(/^(\w+)\[(\d+)\]$/)
  if (topArr) {
    const [, key, idx] = topArr
    const arr = structured[key]
    return arr?.[Number(idx)] ?? ''
  }
  const bulletMatch = bind.match(/^(\w+)\[(\d+)\]\.(\w+)\[(\d+)\]$/)
  if (bulletMatch) {
    const [, arrKey, idx, field, bidx] = bulletMatch
    const arr = structured[arrKey]
    const item = arr?.[Number(idx)]
    const bullets = item?.[field]
    return bullets?.[Number(bidx)] ?? ''
  }
  const arrMatch = bind.match(/^(\w+)\[(\d+)\]\.(\w+)$/)
  if (arrMatch) {
    const [, arrKey, idx, field] = arrMatch
    const arr = structured[arrKey]
    const item = arr?.[Number(idx)]
    const val = item?.[field]
    if (Array.isArray(val)) return val.join('\n')
    return val ?? ''
  }
  const parts = bind.split('.')
  let cur = structured
  for (const p of parts) {
    if (!cur || typeof cur !== 'object') return ''
    cur = cur[p]
  }
  if (Array.isArray(cur)) return cur.join(', ')
  return cur ?? ''
}

export function setBindValue(structured, bind, value) {
  const out = structured && typeof structured === 'object' ? structured : {}
  const topArr = bind.match(/^(\w+)\[(\d+)\]$/)
  if (topArr) {
    const [, key, idx] = topArr
    if (!Array.isArray(out[key])) out[key] = []
    while (out[key].length <= Number(idx)) out[key].push('')
    out[key][Number(idx)] = value
    return out
  }
  const bulletMatch = bind.match(/^(\w+)\[(\d+)\]\.(\w+)\[(\d+)\]$/)
  if (bulletMatch) {
    const [, arrKey, idx, field, bidx] = bulletMatch
    if (!Array.isArray(out[arrKey])) out[arrKey] = []
    while (out[arrKey].length <= Number(idx)) out[arrKey].push({})
    if (!out[arrKey][Number(idx)] || typeof out[arrKey][Number(idx)] !== 'object') {
      out[arrKey][Number(idx)] = {}
    }
    if (!Array.isArray(out[arrKey][Number(idx)][field])) out[arrKey][Number(idx)][field] = []
    while (out[arrKey][Number(idx)][field].length <= Number(bidx)) {
      out[arrKey][Number(idx)][field].push('')
    }
    out[arrKey][Number(idx)][field][Number(bidx)] = value
    return out
  }
  const arrMatch = bind.match(/^(\w+)\[(\d+)\]\.(\w+)$/)
  if (arrMatch) {
    const [, arrKey, idx, field] = arrMatch
    if (!Array.isArray(out[arrKey])) out[arrKey] = []
    while (out[arrKey].length <= Number(idx)) out[arrKey].push({})
    if (!out[arrKey][Number(idx)] || typeof out[arrKey][Number(idx)] !== 'object') {
      out[arrKey][Number(idx)] = {}
    }
    if (field === 'bullets') {
      out[arrKey][Number(idx)][field] = value.split('\n').filter(Boolean)
    } else {
      out[arrKey][Number(idx)][field] = value
    }
    return out
  }
  const parts = bind.split('.')
  if (parts.length === 2) {
    if (!out[parts[0]] || typeof out[parts[0]] !== 'object') out[parts[0]] = {}
    out[parts[0]][parts[1]] = value
  }
  return out
}

export function mergeCellStyle(visualDocument, bind) {
  const styles = visualDocument?.styles || {}
  return styles[bind] || {}
}

export function setCellStyle(visualDocument, bind, patch) {
  const doc = visualDocument && typeof visualDocument === 'object'
    ? { ...visualDocument, styles: { ...(visualDocument.styles || {}) } }
    : { template_id: 'classic-blue', photo_file_id: null, styles: {} }
  doc.styles[bind] = { ...(doc.styles[bind] || {}), ...patch }
  return doc
}

export function defaultVisualDocument() {
  return { template_id: 'classic-blue', photo_file_id: null, styles: {} }
}

export function defaultStructured() {
  return {
    basics: {
      name: '',
      email: '',
      phone: '',
      summary: '',
      gender: '',
      age: '',
      native_place: '',
      education: '',
      motto: '踏实肯干，责任心强，期待在贵公司实现价值。',
    },
    job_intention: { position: '', city: '', salary: '', availability: '随时到岗' },
    experience: [],
    education: [],
    skills: [],
    skill_bars: [
      { name: '计算机', level: 85, label: '精通' },
      { name: '英语', level: 70, label: '良好' },
    ],
    honors: [],
    self_evaluation: '',
  }
}
