import { computed, onUnmounted, ref, watch } from 'vue'

function resolveAudioUrl(url) {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('blob:')) return url
  if (url.startsWith('/')) return url
  return `/${url.replace(/^\//, '')}`
}

/** 编辑器 / 预览中的 BGM 播放与静音 */
export function useBgmPlayer(bgmConfigRef, options = {}) {
  const { autoPlay = true } = options
  const muted = ref(false)
  const playing = ref(false)
  let audio = null

  const active = computed(() => {
    const cfg = bgmConfigRef?.value
    return !!(cfg?.enabled && cfg?.url)
  })

  function bindAudioEvents(el) {
    el.onplay = () => {
      playing.value = true
    }
    el.onpause = () => {
      playing.value = false
    }
    el.onended = () => {
      playing.value = false
    }
  }

  function ensureAudio() {
    if (!audio) {
      audio = new Audio()
      bindAudioEvents(audio)
    }
    return audio
  }

  async function tryPlay() {
    const cfg = bgmConfigRef?.value
    if (!cfg?.enabled || !cfg?.url || muted.value) {
      if (audio && !cfg?.enabled) {
        audio.pause()
        audio.removeAttribute('src')
      }
      return
    }

    const el = ensureAudio()
    const nextSrc = resolveAudioUrl(cfg.url)
    const currentSrc = el.getAttribute('src') || el.src
    if (!currentSrc.endsWith(nextSrc)) {
      el.src = nextSrc
    }
    el.loop = cfg.loop !== false
    el.volume = Number(cfg.volume ?? 0.35)

    try {
      await el.play()
      return true
    } catch {
      playing.value = false
      if (!muted.value) muted.value = true
      return false
    }
  }

  function toggleMute() {
    if (!active.value) return
    if (muted.value) {
      muted.value = false
      tryPlay().then((ok) => {
        if (!ok) muted.value = true
      })
      return
    }
    muted.value = true
    audio?.pause()
    playing.value = false
  }

  function stop() {
    audio?.pause()
    playing.value = false
  }

  watch(
    () => [
      bgmConfigRef?.value?.enabled,
      bgmConfigRef?.value?.url,
      bgmConfigRef?.value?.loop,
      bgmConfigRef?.value?.volume,
    ],
    () => {
      if (!autoPlay) {
        if (!active.value) stop()
        return
      }
      if (active.value && !muted.value) tryPlay()
      else if (!active.value) stop()
    },
    { immediate: autoPlay }
  )

  onUnmounted(() => {
    stop()
    if (audio) {
      audio.onplay = null
      audio.onpause = null
      audio.onended = null
      audio = null
    }
  })

  return {
    active,
    muted,
    playing,
    tryPlay,
    toggleMute,
    stop,
  }
}
