<template>
  <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-lg flex flex-col overflow-hidden">
      <div class="px-6 py-4 border-b border-outline-variant shrink-0">
        <h2 class="text-lg font-bold">{{ mode === 'import' ? '从 PPT 导入模板' : '新建模板' }}</h2>
        <p class="text-xs text-on-surface-variant mt-0.5">
          {{ mode === 'import' ? '解析后将创建模板并进入可视化编辑器' : '填写基本信息后进入与用户端相同的编辑器' }}
        </p>
      </div>

      <div class="p-6 text-sm space-y-3 max-h-[70vh] overflow-y-auto">
        <template v-if="mode !== 'import'">
          <label class="block">
            <span class="font-medium">模板 ID</span>
            <input v-model="form.id" required class="mt-1 w-full border rounded-lg px-3 py-2 font-mono text-xs" placeholder="my-template-mobile" />
          </label>
        </template>
        <label class="block">
          <span class="font-medium">标题</span>
          <input v-model="form.title" required class="mt-1 w-full border rounded-lg px-3 py-2" />
        </label>
        <label class="block">
          <span class="font-medium">描述</span>
          <textarea v-model="form.description" rows="2" class="mt-1 w-full border rounded-lg px-3 py-2" />
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
            <select v-model="form.device" class="mt-1 w-full border rounded-lg px-3 py-2" @change="onDeviceChange">
              <option value="mobile">移动端</option>
              <option value="web">网页版</option>
            </select>
          </label>
        </div>
        <label class="block">
          <span class="font-medium">封面渐变 Tailwind 类</span>
          <input v-model="form.cover_gradient" class="mt-1 w-full border rounded-lg px-3 py-2 font-mono text-xs" />
        </label>
        <div class="flex flex-wrap gap-4">
          <label class="flex items-center gap-2">
            <input v-model="form.premium" type="checkbox" />
            <span>高级模板</span>
          </label>
          <label class="flex items-center gap-2">
            <input v-model="form.enabled" type="checkbox" />
            <span>上架展示</span>
          </label>
        </div>

        <div v-if="mode === 'import'" class="border-2 border-dashed border-outline-variant rounded-xl p-6 text-center">
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

      <div class="px-6 py-4 border-t border-outline-variant flex justify-end gap-2 shrink-0">
        <button type="button" class="px-4 py-2 border rounded-lg" :disabled="saving" @click="$emit('close')">取消</button>
        <button
          v-if="mode !== 'import'"
          type="button"
          class="px-4 py-2 bg-primary text-on-primary rounded-lg disabled:opacity-50"
          :disabled="saving || !form.id.trim() || !form.title.trim()"
          @click="createAndEdit"
        >
          {{ saving ? '创建中…' : '创建并编辑' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { api } from '../../api/client'

const DEFAULT_SETTINGS = {
  viewportId: 'mobile-375',
  scrollEffect: 'page',
  themeId: 'zjy-minimal',
  showScrollHint: false,
  defaultChatTapToContinue: true,
  bgm: { enabled: false, trackId: '', url: '', loop: true, volume: 0.35 },
}

const categories = ['对话故事', '简约商务', '叙事公益', '年度报告', '产品发布', '个人简历', '企业介绍']

const props = defineProps({
  open: Boolean,
  mode: { type: String, default: 'create' },
})

const emit = defineEmits(['close', 'open-editor'])

const saving = ref(false)
const error = ref('')
const importMessage = ref('')
const importError = ref(false)

const form = reactive({
  id: '',
  title: '',
  description: '',
  category: '简约商务',
  device: 'mobile',
  premium: false,
  cover_gradient: 'from-primary to-primary-container',
  default_viewport: 'mobile-375',
  enabled: true,
})

watch(
  () => props.open,
  (v) => {
    if (!v) return
    error.value = ''
    importMessage.value = ''
    importError.value = false
    if (props.mode !== 'import') {
      Object.assign(form, {
        id: '',
        title: '',
        description: '',
        category: '简约商务',
        device: 'mobile',
        premium: false,
        cover_gradient: 'from-primary to-primary-container',
        default_viewport: 'mobile-375',
        enabled: true,
      })
    }
  }
)

function onDeviceChange() {
  form.default_viewport = form.device === 'web' ? 'web-1280' : 'mobile-375'
}

async function createAndEdit() {
  saving.value = true
  error.value = ''
  const settings = {
    ...DEFAULT_SETTINGS,
    viewportId: form.default_viewport,
  }
  try {
    await api.createAdminTemplate({
      ...form,
      pages: 1,
      slides_json: [],
      settings_json: settings,
      sort_order: 0,
    })
    const draft = await api.startTemplateDraft(form.id.trim())
    emit('open-editor', { templateId: form.id.trim(), projectId: draft.project_id })
    emit('close')
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}

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
    emit('open-editor', { templateId: created.id, projectId: draft.project_id })
    emit('close')
  } catch (err) {
    importMessage.value = err.message || '导入失败'
    importError.value = true
  } finally {
    saving.value = false
  }
}
</script>
