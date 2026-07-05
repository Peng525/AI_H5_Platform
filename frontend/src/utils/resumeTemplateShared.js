/** Shared theme + section helpers for resume visual templates. */

const THEME_BY_TEMPLATE = {
  template1: { accent: '#2563eb', header: '个人简历' },
  template2: { accent: '#0f766e', header: '个人简历' },
  template3: { accent: '#4f46e5', header: '个人简历' },
  template4: { accent: '#111827', header: '个人简历' },
  template5: { accent: '#1e40af', header: '个人简历' },
  template6: { accent: '#be185d', header: '个人简历' },
  template7: { accent: '#16a34a', header: 'Developer Profile' },
}

export function themeForTemplate(templateId, structured) {
  const base = THEME_BY_TEMPLATE[templateId] || THEME_BY_TEMPLATE.template1
  const name = structured?.basics?.name?.trim()
  if ((templateId === 'template6' || templateId === 'template7') && name) {
    return { ...base, header: name }
  }
  return base
}

export function sectionClass(layout, section) {
  const map = {
    single: 'mb-5',
    modern: 'mb-6 border-b border-slate-200 pb-4 last:border-0',
    multi: 'mb-5 p-3 border border-slate-200 rounded-lg',
    sidebar: 'mb-4',
    magazine: 'mb-6',
    tech: 'mb-5 font-mono',
    'two-column': 'mb-4',
  }
  return map[layout] || map.single
}
