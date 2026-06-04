/**
 * Phase 2：将 structured 幻灯片转为 Reveal.js section HTML 骨架（可选全屏预览）
 */
import { SLIDE_TEMPLATE_REGISTRY } from '../slide-templates/registry.js'

export function structuredToRevealSections(slides = []) {
  return slides
    .map((slide, index) => {
      const st = slide.structured || {}
      const template = st.template || slide.layout || 'section'
      const title = st.title || slide.title || `第 ${index + 1} 页`
      const subtitle = st.subtitle || slide.subtitle || ''
      const modules = (st.modules || [])
        .map(
          (m) =>
            `<div class="reveal-card"><strong>${escapeHtml(m.title || '')}</strong><p>${escapeHtml(m.body || '')}</p></div>`
        )
        .join('')
      return `<section data-template="${template}">
        <h2>${escapeHtml(title)}</h2>
        ${subtitle ? `<p class="subtitle">${escapeHtml(subtitle)}</p>` : ''}
        ${st.headline ? `<p class="headline"><strong>${escapeHtml(st.headline)}</strong></p>` : ''}
        <div class="modules-grid">${modules}</div>
      </section>`
    })
    .join('\n')
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

/** 是否启用 Reveal 预览（query ?reveal=1 或 settings.useRevealPreview） */
export function shouldUseRevealPreview(routeQuery, settings = {}) {
  if (routeQuery?.reveal === '1' || routeQuery?.reveal === 'true') return true
  return !!settings.useRevealPreview
}

export { SLIDE_TEMPLATE_REGISTRY }
