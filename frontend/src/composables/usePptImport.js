import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'

export function usePptImport() {
  const router = useRouter()
  const importing = ref(false)
  const importError = ref('')
  const fileInputRef = ref(null)

  function triggerImport() {
    importError.value = ''
    fileInputRef.value?.click()
  }

  async function onFileSelected(e) {
    const file = e.target.files?.[0]
    e.target.value = ''
    if (!file) return
    if (!file.name.toLowerCase().endsWith('.pptx')) {
      importError.value = '请选择 .pptx 格式的 PowerPoint 文件'
      return
    }
    importing.value = true
    importError.value = ''
    try {
      const fd = new FormData()
      fd.append('file', file)
      const project = await api.importProjectPptx(fd)
      router.push(`/editor/${project.id}`)
    } catch (err) {
      importError.value = err.message || '导入失败'
    } finally {
      importing.value = false
    }
  }

  return {
    importing,
    importError,
    fileInputRef,
    triggerImport,
    onFileSelected,
  }
}
