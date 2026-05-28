import { computed, ref, watch } from 'vue'
import { getViewportPreset } from '../constants/editorPresets'
import { slideBackgroundCSSValue, slideBackgroundToStorage } from '../utils/slideBackground'
import { api } from '../api/client'

const PREFIX = 'ai_h5_project_settings_'

const defaults = {
  viewportId: 'mobile-375',
  scrollEffect: 'page',
  themeId: 'zjy-minimal',
  showScrollHint: false,
  slideBackgrounds: {},
  bgm: { enabled: false, trackId: '', url: '', loop: true, volume: 0.35 },
  defaultChatTapToContinue: true,
}

const DEFAULT_CANVAS_BG = '#005daa'

export function useProjectEditorSettings(projectIdRef) {
  const settings = ref({ ...defaults })
  let saveTimer = null

  function load() {
    const id = projectIdRef.value
    if (!id) {
      settings.value = { ...defaults, slideBackgrounds: {}, bgm: { ...defaults.bgm } }
      return
    }
    try {
      const raw = localStorage.getItem(`${PREFIX}${id}`)
      if (!raw) {
        settings.value = { ...defaults, slideBackgrounds: {}, bgm: { ...defaults.bgm } }
        return
      }
      const parsed = JSON.parse(raw)
      settings.value = {
        ...defaults,
        ...parsed,
        slideBackgrounds: { ...defaults.slideBackgrounds, ...(parsed.slideBackgrounds || {}) },
        bgm: { ...defaults.bgm, ...(parsed.bgm || {}) },
      }
    } catch {
      settings.value = { ...defaults, slideBackgrounds: {}, bgm: { ...defaults.bgm } }
    }
  }

  function save() {
    const id = projectIdRef.value
    if (!id) return
    localStorage.setItem(`${PREFIX}${id}`, JSON.stringify(settings.value))
    scheduleCloudSave()
  }

  function scheduleCloudSave() {
    const id = projectIdRef.value
    if (!id) return
    clearTimeout(saveTimer)
    saveTimer = setTimeout(async () => {
      try {
        await api.updateProjectSettings(Number(id), {
          viewportId: settings.value.viewportId,
          scrollEffect: settings.value.scrollEffect,
          themeId: settings.value.themeId,
          showScrollHint: settings.value.showScrollHint,
          slideBackgrounds: settings.value.slideBackgrounds,
          bgm: settings.value.bgm,
          defaultChatTapToContinue: settings.value.defaultChatTapToContinue,
        })
      } catch (e) {
        console.warn('保存项目设置失败', e)
      }
    }, 600)
  }

  function applyFromServer(serverSettings) {
    if (!serverSettings) return
    settings.value = {
      ...defaults,
      ...settings.value,
      ...serverSettings,
      slideBackgrounds: {
        ...defaults.slideBackgrounds,
        ...(settings.value.slideBackgrounds || {}),
        ...(serverSettings.slideBackgrounds || {}),
      },
      bgm: {
        ...defaults.bgm,
        ...(settings.value.bgm || {}),
        ...(serverSettings.bgm || {}),
      },
    }
    save()
  }

  function setViewport(viewportId) {
    settings.value = { ...settings.value, viewportId }
    save()
  }

  function setScrollEffect(scrollEffect) {
    settings.value = { ...settings.value, scrollEffect }
    save()
  }

  function setBgm(patch) {
    settings.value = {
      ...settings.value,
      bgm: { ...settings.value.bgm, ...patch },
    }
    save()
  }

  function getSlideBackground(slideId) {
    if (!slideId) return slideBackgroundCSSValue(DEFAULT_CANVAS_BG)
    const key = String(slideId)
    const raw = settings.value.slideBackgrounds?.[key]
    return slideBackgroundCSSValue(raw ?? DEFAULT_CANVAS_BG)
  }

  function getSlideBackgroundRaw(slideId) {
    if (!slideId) return DEFAULT_CANVAS_BG
    const key = String(slideId)
    return settings.value.slideBackgrounds?.[key] ?? DEFAULT_CANVAS_BG
  }

  function setSlideBackground(slideId, color) {
    if (!slideId) return
    const key = String(slideId)
    settings.value = {
      ...settings.value,
      slideBackgrounds: { ...settings.value.slideBackgrounds, [key]: slideBackgroundToStorage(color) },
    }
    save()
  }

  function setThemeId(themeId) {
    settings.value = { ...settings.value, themeId }
    save()
  }

  const viewport = computed(() => getViewportPreset(settings.value.viewportId))

  watch(projectIdRef, load, { immediate: true })

  return {
    settings,
    viewport,
    load,
    save,
    applyFromServer,
    setViewport,
    setScrollEffect,
    setBgm,
    getSlideBackground,
    getSlideBackgroundRaw,
    setSlideBackground,
    setThemeId,
  }
}
