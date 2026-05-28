import { ref } from 'vue'
import { api } from '../api/client'

const tracks = ref([])
const loaded = ref(false)
const loading = ref(false)
const hint = ref('')

let loadPromise = null

export function useBgmCatalog() {
  async function loadBgmCatalog(force = false) {
    if (loaded.value && !force) return tracks.value
    if (loadPromise && !force) return loadPromise
    loading.value = true
    loadPromise = api
      .listBgmTracks()
      .then((res) => {
        tracks.value = res.tracks || []
        hint.value = res.hint || ''
        loaded.value = true
        return tracks.value
      })
      .catch((e) => {
        console.warn('加载 BGM 曲目失败', e)
        tracks.value = []
        return tracks.value
      })
      .finally(() => {
        loading.value = false
        loadPromise = null
      })
    return loadPromise
  }

  function findTrackById(id) {
    if (!id) return null
    return tracks.value.find((t) => t.id === id) || null
  }

  function findTrackByUrl(url) {
    if (!url) return null
    return tracks.value.find((t) => t.url === url) || null
  }

  return {
    tracks,
    loaded,
    loading,
    hint,
    loadBgmCatalog,
    findTrackById,
    findTrackByUrl,
  }
}
