<template>
  <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-lg flex flex-col overflow-hidden">
      <div class="px-6 py-4 border-b border-outline-variant shrink-0">
        <h2 class="text-lg font-bold">从 PPT 导入模板</h2>
        <p class="text-xs text-on-surface-variant mt-0.5">解析后将创建模板并进入与用户端相同的可视化编辑器</p>
      </div>

      <div class="p-6 text-sm space-y-3 max-h-[70vh] overflow-y-auto">
        <label class="block">
          <span class="font-medium">标题（可选）</span>
          <input v-model="form.title" class="mt-1 w-full border rounded-lg px-3 py-2" placeholder="默认使用文件名" />
        </label>
        <div class="grid grid-cols-2 gap-3">
          <label class="block">
            <span class="font-medium">分类</span>
            <select v-model="form.category" class="mt-1 w-full border rounded-lg px-3 py-2">
              <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
            </select>
          </label>
          <label class="block">
            <span class="font-medium">终端</span>
            <select v-model="form.device" class="mt-1 w-full border rounded-lg px-3 py-2">
              <option value="mobile">移动端</option>
              <option value="web">网页版</option>
            </select>
          </label>
        </div>
        <label class="block">
          <span class="font-medium">模板 ID（可选，留空自动生成）</span>
          <input v-model="form.id" class="mt-1 w-full border rounded-lg px-3 py-2 font-mono text-xs" placeholder="my-template-mobile" />
        </label>
        <label class="flex items-center gap-2">
          <input v-model="form.enabled" type="checkbox" />
          <span>导入后立即上架</span>
        </label>

        <div class="border-2 border-dashed border-outline-variant rounded-xl p-6 text-center">
          <p class="text-on-surface-variant text-xs mb-3">上传 PowerPoint (.pptx)</p>
          <label class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-on-primary text-sm cursor-pointer">
            <span class="material-symbols-outlined text-[18px]">upload_file</span>
            选择文件
            <input type="file" accept=".pptx" class="hidden" @change="onPptxSelected" />
          </label>
          <p v-if="importMessage" class="mt-3 text-xs" :class="importError ? 'text-red-600' : 'text-secondary'">{{ importMessage }}</p>
        </div>

        <p v-if="error" class="text-red-600 text-xs">{{ error }}</p>
      </div>

      <div class="px-6 py-4 border-t border-outline-variant flex justify-end shrink-0">
        <button type="button" class="px-4 py-2 border rounded-lg" :disabled="saving" @click="$emit('close')">取消</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { api } from '../../api/client'

const categories = ['对话故事', '简约商务', '叙事公益', '年度报告', '产品发布', '个人简历', '企业介绍']

const props = defineProps({
  open: Boolean,
})

const emit = defineEmits(['close', 'open-editor'])

const saving = ref(false)
const error = ref('')
const importMessage = ref('')
const importError = ref(false)

const form = reactive({
  id: '',
  title: '',
  category: '简约商务',
  device: 'mobile',
  enabled: false,
})

watch(
  () => props.open,
  (v) => {
    if (!v) return
    error.value = ''
    importMessage.value = ''
    importError.value = false
    Object.assign(form, { id: '', title: '', category: '简约商务', device: 'mobile', enabled: false })
  }
)

async function onPptxSelected(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  saving.value = true
  importMessage.value = '正在解析并创建模板…'
  importError.value = false
  error.value = ''
  try {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('device', form.device)
    fd.append('category', form.category)
    if (form.title) fd.append('title', form.title)
    if (form.id.trim()) fd.append('template_id', form.id.trim())
    fd.append('enabled', form.enabled ? 'true' : 'false')
    const created = await api.importAdminPptxTemplate(fd)
    const draft = await api.startTemplateDraft(created.id)
    emit('open-editor', { templateId: created.id, projectId: draft.project_public_id })
    emit('close')
  } catch (err) {
    importMessage.value = err.message || '导入失败'
    importError.value = true
  } finally {
    saving.value = false
  }
}
</script>
