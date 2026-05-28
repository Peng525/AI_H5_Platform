import { computed, ref, watch } from 'vue'
import { getViewportPreset } from '../constants/editorPresets'

const PREFIX = 'ai_h5_project_settings_'

const defaults = {
  viewportId: 'mobile-375',
  scrollEffect: 'page',
  slideBackgrounds: {},
}

const DEFAULT_CANVAS_BG = '#005daa'

export function useProjectEditorSettings(projectIdRef) {
  const settings = ref({ ...defaults })

  function load() {
    const id = projectIdRef.value
    if (!id) {
      settings.value = { ...defaults }
      return
    }
    try {
      const raw = localStorage.getItem(`${PREFIX}${id}`)
      if (!raw) {
        settings.value = { ...defaults }
        return
      }
      const parsed = JSON.parse(raw)
      settings.value = {
        ...defaults,
        ...parsed,
        slideBackgrounds: { ...defaults.slideBackgrounds, ...(parsed.slideBackgrounds || {}) },
      }
    } catch {
      settings.value = { ...defaults }
    }
  }

  function save() {
    const id = projectIdRef.value
    if (!id) return
    localStorage.setItem(`${PREFIX}${id}`, JSON.stringify(settings.value))
  }

  function setViewport(viewportId) {
    settings.value = { ...settings.value, viewportId }
    save()
  }

  function setScrollEffect(scrollEffect) {
    settings.value = { ...settings.value, scrollEffect }
    save()
  }

  function getSlideBackground(slideId) {
    if (!slideId) return DEFAULT_CANVAS_BG
    const key = String(slideId)
    return settings.value.slideBackgrounds?.[key] ?? DEFAULT_CANVAS_BG
  }

  function setSlideBackground(slideId, color) {
    if (!slideId) return
    const key = String(slideId)
    settings.value = {
      ...settings.value,
      slideBackgrounds: { ...settings.value.slideBackgrounds, [key]: color },
    }
    save()
  }

  /** 使用 computed，便于在模板中直接绑定 */
  const viewport = computed(() => getViewportPreset(settings.value.viewportId))

  watch(projectIdRef, load, { immediate: true })

  return {
    settings,
    viewport,
    load,
    save,
    setViewport,
    setScrollEffect,
    getSlideBackground,
    setSlideBackground,
  }
}
