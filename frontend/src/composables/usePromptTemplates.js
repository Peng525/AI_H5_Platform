import { ref } from 'vue'

/**
 * 通用提示词模板列表加载（deck / image 共用）。
 * @param {() => Promise<unknown>} fetchFn - API 列表方法
 * @param {Array} fallbackTemplates - 离线兜底常量
 */
export function usePromptTemplates(fetchFn, fallbackTemplates) {
  const loaded = ref(false)
  const loading = ref(false)
  const loadError = ref('')
  const templates = ref([])
  const fromFallback = ref(false)
  let loadPromise = null

  async function load() {
    if (loaded.value && templates.value.length) return templates.value
    if (loadPromise) return loadPromise
    loading.value = true
    loadError.value = ''
    loadPromise = fetchFn()
      .then((rows) => {
        const list = Array.isArray(rows) ? rows : []
        if (list.length) {
          templates.value = list
          fromFallback.value = false
        } else {
          templates.value = [...fallbackTemplates]
          fromFallback.value = true
        }
        loaded.value = true
        return templates.value
      })
      .catch((e) => {
        templates.value = [...fallbackTemplates]
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
