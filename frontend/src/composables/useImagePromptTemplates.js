import { ref } from 'vue'
import { api } from '../api/client'
import { IMAGE_PROMPT_TEMPLATES } from '../constants/imagePromptTemplates'

const loaded = ref(false)
const loading = ref(false)
const loadError = ref('')
const templates = ref([])
const fromFallback = ref(false)
let loadPromise = null

export function useImagePromptTemplates() {
  async function load() {
    if (loaded.value && templates.value.length) return templates.value
    if (loadPromise) return loadPromise
    loading.value = true
    loadError.value = ''
    loadPromise = api
      .listImagePromptTemplates()
      .then((rows) => {
        const list = Array.isArray(rows) ? rows : []
        if (list.length) {
          templates.value = list
          fromFallback.value = false
        } else {
          templates.value = [...IMAGE_PROMPT_TEMPLATES]
          fromFallback.value = true
        }
        loaded.value = true
        return templates.value
      })
      .catch((e) => {
        templates.value = [...IMAGE_PROMPT_TEMPLATES]
        fromFallback.value = true
        loadError.value = e.message || '加载失败'
        loaded.value = true
        return templates.value
      })
      .finally(() => {
        loading.value = false
        loadPromise = null
      })
    return loadPromise
  }

  function reload() {
    loaded.value = false
    loadPromise = null
    return load()
  }

  return {
    loaded,
    loading,
    loadError,
    templates,
    fromFallback,
    load,
    reload,
  }
}
