import { computed, onUnmounted, ref, watch } from 'vue'

import { slideBackgroundCSSValue } from '../utils/slideBackground'

/** 演示播放：对话门控 + BGM */
export function usePresentationPlayback(options = {}) {
  const {
    slidesRef,
    settingsRef,
    onNeedUserGesture,
  } = options

  const chatBlocking = ref(false)
  const chatSlideKey = ref(null)
  const audioRef = ref(null)
  const bgmMuted = ref(false)
  const bgmUnlocked = ref(false)

  const bgmConfig = computed(() => settingsRef?.value?.bgm || {})

  function slideChatScript(slide) {
    if (!slide?.chat_script?.enabled) return null
    return slide.chat_script
  }

  function chatKeyForSlide(slide, index) {
    return slide?.id != null ? String(slide.id) : `idx-${index}`
  }

  function syncChatGate(slide, index) {
    const script = slideChatScript(slide)
    const key = chatKeyForSlide(slide, index)
    if (script) {
      chatSlideKey.value = key
      chatBlocking.value = true
    } else {
      chatSlideKey.value = key
      chatBlocking.value = false
    }
  }

  function onChatComplete() {
    chatBlocking.value = false
  }

  function ensureAudio() {
    if (audioRef.value) return audioRef.value
    const audio = new Audio()
    audio.loop = !!bgmConfig.value.loop
    audio.volume = Number(bgmConfig.value.volume ?? 0.35)
    audioRef.value = audio
    return audio
  }

  async function tryPlayBgm() {
    const cfg = bgmConfig.value
    if (!cfg.enabled || !cfg.url || bgmMuted.value) return
    const audio = ensureAudio()
    if (audio.src !== cfg.url) {
      audio.src = cfg.url
      audio.loop = cfg.loop !== false
      audio.volume = Number(cfg.volume ?? 0.35)
    }
    try {
      await audio.play()
      bgmUnlocked.value = true
    } catch {
      onNeedUserGesture?.()
    }
  }

  function unlockBgmFromGesture() {
    bgmUnlocked.value = true
    tryPlayBgm()
  }

  function toggleBgmMute() {
    bgmMuted.value = !bgmMuted.value
    const audio = audioRef.value
    if (!audio) return
    if (bgmMuted.value) {
      audio.pause()
    } else if (bgmUnlocked.value) {
      tryPlayBgm()
    }
  }

  function stopBgm() {
    audioRef.value?.pause()
  }

  watch(
    () => [bgmConfig.value.enabled, bgmConfig.value.url, bgmUnlocked.value, bgmMuted.value],
    () => {
      if (bgmUnlocked.value && !bgmMuted.value) tryPlayBgm()
    }
  )

  onUnmounted(() => {
    stopBgm()
    audioRef.value = null
  })

  function guardNavigation(fn) {
    return (...args) => {
      if (chatBlocking.value) return false
      fn?.(...args)
      return true
    }
  }

  return {
    chatBlocking,
    chatSlideKey,
    bgmMuted,
    bgmUnlocked,
    slideChatScript,
    syncChatGate,
    onChatComplete,
    tryPlayBgm,
    unlockBgmFromGesture,
    toggleBgmMute,
    stopBgm,
    guardNavigation,
  }
}

/** 合并服务端与 localStorage 的项目设置 */
export function mergeProjectSettings(projectId, serverSettings) {
  const defaults = {
    viewportId: 'mobile-375',
    scrollEffect: 'page',
    themeId: 'zjy-minimal',
    showScrollHint: false,
    slideBackgrounds: {},
    bgm: { enabled: false, trackId: '', url: '', loop: true, volume: 0.35 },
    defaultChatTapToContinue: true,
  }
  let local = {}
  try {
    const raw = localStorage.getItem(`ai_h5_project_settings_${projectId}`)
    if (raw) local = JSON.parse(raw)
  } catch { /* ignore */ }
  const merged = {
    ...defaults,
    ...local,
    ...(serverSettings || {}),
    slideBackgrounds: {
      ...defaults.slideBackgrounds,
      ...(local.slideBackgrounds || {}),
      ...(serverSettings?.slideBackgrounds || {}),
    },
    bgm: {
      ...defaults.bgm,
      ...(local.bgm || {}),
      ...(serverSettings?.bgm || {}),
    },
  }
  if (projectId) {
    localStorage.setItem(`ai_h5_project_settings_${projectId}`, JSON.stringify(merged))
  }
  return merged
}

export function resolveSlideBackground(projectId, slideId, settings) {
  const DEFAULT = '#005daa'
  if (!slideId) return slideBackgroundCSSValue(DEFAULT)
  const key = String(slideId)
  const fromSettings = settings?.slideBackgrounds?.[key]
  if (fromSettings) return slideBackgroundCSSValue(fromSettings)
  try {
    const raw = localStorage.getItem(`ai_h5_project_settings_${projectId}`)
    if (raw) {
      const s = JSON.parse(raw)
      const v = s.slideBackgrounds?.[key]
      if (v) return slideBackgroundCSSValue(v)
    }
  } catch { /* ignore */ }
  return slideBackgroundCSSValue(DEFAULT)
}
