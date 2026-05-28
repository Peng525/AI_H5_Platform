import { ref, watch } from 'vue'

const STORAGE_PREFIX = 'ai_h5_canvas_'

function storageKey(projectId, slideId) {
  return `${STORAGE_PREFIX}${projectId}_${slideId}`
}

function genId() {
  return `el_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
}

export function defaultElement(type, overrides = {}) {
  const base = {
    id: genId(),
    type,
    x: 24,
    y: 120,
    width: type === 'shape' ? 80 : 200,
    height: type === 'shape' ? 80 : type === 'image' ? 120 : 40,
    zIndex: 1,
    content: type === 'text' ? '双击编辑文本' : type === 'image' ? '' : '',
    style: {
      fontSize: 16,
      color: '#1b1b1c',
      background: type === 'shape' ? '#005daa' : 'transparent',
      borderRadius: type === 'shape' ? 8 : 0,
      fontWeight: 'normal',
      textAlign: 'left',
    },
  }
  return { ...base, ...overrides, style: { ...base.style, ...(overrides.style || {}) } }
}

export function useSlideCanvas(projectIdRef, slideIdRef) {
  const elements = ref([])
  const selectedId = ref(null)

  function loadElements() {
    const pid = projectIdRef.value
    const sid = slideIdRef.value
    if (!pid || !sid) {
      elements.value = []
      return
    }
    try {
      const raw = localStorage.getItem(storageKey(pid, sid))
      elements.value = raw ? JSON.parse(raw) : []
    } catch {
      elements.value = []
    }
    selectedId.value = null
  }

  function saveElements() {
    const pid = projectIdRef.value
    const sid = slideIdRef.value
    if (!pid || !sid) return
    try {
      localStorage.setItem(
        storageKey(pid, sid),
        JSON.stringify(elements.value.map((el) => ({ ...el, updatedAt: Date.now() })))
      )
    } catch (e) {
      console.warn('画布保存失败', e)
    }
  }

  function addElement(type, overrides = {}) {
    const maxZ = elements.value.reduce((m, el) => Math.max(m, el.zIndex || 0), 0)
    const el = defaultElement(type, { ...overrides, zIndex: maxZ + 1 })
    elements.value.push(el)
    selectedId.value = el.id
    saveElements()
    return el
  }

  function updateElement(id, patch) {
    const idx = elements.value.findIndex((el) => el.id === id)
    if (idx < 0) return
    const prev = elements.value[idx]
    elements.value[idx] = {
      ...prev,
      ...patch,
      style: patch.style ? { ...prev.style, ...patch.style } : prev.style,
    }
    saveElements()
  }

  function removeElement(id) {
    elements.value = elements.value.filter((el) => el.id !== id)
    if (selectedId.value === id) selectedId.value = null
    saveElements()
  }

  function duplicateElement(id) {
    const src = elements.value.find((el) => el.id === id)
    if (!src) return
    const copy = {
      ...JSON.parse(JSON.stringify(src)),
      id: genId(),
      x: src.x + 12,
      y: src.y + 12,
      zIndex: (src.zIndex || 0) + 1,
    }
    elements.value.push(copy)
    selectedId.value = copy.id
    saveElements()
    return copy
  }

  function bringToFront(id) {
    const maxZ = elements.value.reduce((m, el) => Math.max(m, el.zIndex || 0), 0)
    updateElement(id, { zIndex: maxZ + 1 })
  }

  function syncFromSlide(slide) {
    if (!slide || elements.value.length > 0) return
    const items = []
    if (slide.title) {
      items.push(
        defaultElement('text', {
          x: 20,
          y: 80,
          width: 320,
          height: 48,
          content: slide.title,
          style: { fontSize: 22, color: '#ffffff', fontWeight: 'bold', background: 'transparent' },
        })
      )
    }
    if (slide.subtitle) {
      items.push(
        defaultElement('text', {
          x: 20,
          y: 130,
          width: 320,
          height: 32,
          content: slide.subtitle,
          style: { fontSize: 14, color: '#ffffff', background: 'transparent' },
        })
      )
    }
    ;(slide.bullets || []).forEach((b, i) => {
      items.push(
        defaultElement('text', {
          x: 24,
          y: 170 + i * 28,
          width: 300,
          height: 24,
          content: `• ${b}`,
          style: { fontSize: 14, color: '#ffffff', background: 'transparent' },
        })
      )
    })
    if (items.length) {
      elements.value = items
      saveElements()
    }
  }

  watch([projectIdRef, slideIdRef], () => loadElements(), { immediate: true })

  return {
    elements,
    selectedId,
    loadElements,
    saveElements,
    addElement,
    updateElement,
    removeElement,
    duplicateElement,
    bringToFront,
    syncFromSlide,
  }
}
