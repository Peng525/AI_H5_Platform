import { computed, onUnmounted, ref, watch } from 'vue'

import { resolveSlideCanvasBackground } from '../utils/slideBackground'
import { useBgmPlayer } from './useBgmPlayer.js'

/** 演示播放：对话门控 + BGM */
export function usePresentationPlayback(options = {}) {
  const {
    slidesRef,
    settingsRef,
    onNeedUserGesture,
  } = options

  const chatBlocking = ref(false)
  const chatSlideKey = ref(null)
  const bgmUnlocked = ref(false)

  const bgmConfig = computed(() => settingsRef?.value?.bgm || {})
  const {
    active: bgmActive,
    muted: bgmMuted,
    playing: bgmPlaying,
    tryPlay,
    toggleMute: toggleBgmMuteInternal,
    stop: stopBgm,
  } = useBgmPlayer(bgmConfig, { autoPlay: false })

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

  async function tryPlayBgm() {
    if (!bgmConfig.value.enabled || !bgmConfig.value.url || bgmMuted.value) return
    const ok = await tryPlay()
    if (ok) bgmUnlocked.value = true
    else onNeedUserGesture?.()
  }

  function unlockBgmFromGesture() {
    bgmUnlocked.value = true
    tryPlayBgm()
  }

  function toggleBgmMute() {
    toggleBgmMuteInternal()
    if (!bgmMuted.value) bgmUnlocked.value = true
  }

  watch(
    () => [bgmConfig.value.enabled, bgmConfig.value.url, bgmUnlocked.value, bgmMuted.value],
    () => {
      if (bgmUnlocked.value && !bgmMuted.value) tryPlayBgm()
    }
  )

  onUnmounted(() => {
    stopBgm()
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
    bgmPlaying,
    bgmActive,
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

export function resolveSlideBackground(projectId, slideId, settings, slide = null) {
  if (slide) return resolveSlideCanvasBackground(projectId, slide, settings)
  return resolveSlideCanvasBackground(projectId, { id: slideId }, settings)
}
