<template>
  <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-3xl max-h-[92vh] flex flex-col overflow-hidden">
      <div class="px-6 py-4 border-b border-outline-variant flex items-center justify-between shrink-0">
        <div>
          <h2 class="text-lg font-bold">{{ mode === 'create' ? '新建模板' : '编辑模板' }}</h2>
          <p class="text-xs text-on-surface-variant mt-0.5">保存并勾选「上架展示」后，将自动出现在探索模板页</p>
        </div>
        <button type="button" class="p-1 rounded hover:bg-surface-container" @click="$emit('close')">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <div class="flex border-b border-outline-variant text-sm shrink-0 px-4">
        <button
          v-for="t in tabs"
          :key="t.id"
          type="button"
          class="px-4 py-2.5 border-b-2 -mb-px"
          :class="tab === t.id ? 'border-primary text-primary font-medium' : 'border-transparent text-on-surface-variant'"
          @click="tab = t.id"
        >
          {{ t.label }}
        </button>
      </div>

      <div class="flex-1 overflow-y-auto p-6 text-sm space-y-4">
        <div v-show="tab === 'meta'" class="space-y-3">
          <label v-if="mode === 'create'" class="block">
            <span class="font-medium">模板 ID</span>
            <input v-model="form.id" required class="mt-1 w-full border rounded-lg px-3 py-2 font-mono text-xs" placeholder="my-template-mobile" />
          </label>
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
          <div class="grid grid-cols-2 gap-3">
            <label class="block">
              <span class="font-medium">页数</span>
              <input v-model.number="form.pages" type="number" min="1" class="mt-1 w-full border rounded-lg px-3 py-2" />
            </label>
            <label class="block">
              <span class="font-medium">排序（越小越靠前）</span>
              <input v-model.number="form.sort_order" type="number" class="mt-1 w-full border rounded-lg px-3 py-2" />
            </label>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <label class="block">
              <span class="font-medium">默认视口</span>
              <input v-model="form.default_viewport" class="mt-1 w-full border rounded-lg px-3 py-2" />
            </label>
            <label class="block">
              <span class="font-medium">封面渐变 Tailwind 类</span>
              <input v-model="form.cover_gradient" class="mt-1 w-full border rounded-lg px-3 py-2" />
            </label>
          </div>
          <div class="flex flex-wrap gap-4">
            <label class="flex items-center gap-2">
              <input v-model="form.premium" type="checkbox" />
              <span>高级模板</span>
            </label>
            <label class="flex items-center gap-2">
              <input v-model="form.enabled" type="checkbox" />
              <span>上架展示（发布到模板页）</span>
            </label>
          </div>
        </div>

        <div v-show="tab === 'slides'" class="space-y-2">
          <div class="flex items-center justify-between gap-2">
            <p class="text-on-surface-variant text-xs">
              共 {{ slideCount }} 页幻灯片 · 含画布元素、背景与动效
            </p>
            <button type="button" class="text-xs text-primary hover:underline" @click="formatSlidesJson">格式化 JSON</button>
          </div>
          <textarea
            v-model="slidesJsonText"
            rows="16"
            class="w-full border rounded-lg px-3 py-2 font-mono text-xs leading-relaxed"
            spellcheck="false"
          />
          <p v-if="slidesJsonError" class="text-red-600 text-xs">{{ slidesJsonError }}</p>
        </div>

        <div v-show="tab === 'settings'" class="space-y-2">
          <div class="flex items-center justify-between gap-2">
            <p class="text-on-surface-variant text-xs">项目级设置：视口、滚动模式、主题等</p>
            <button type="button" class="text-xs text-primary hover:underline" @click="formatSettingsJson">格式化 JSON</button>
          </div>
          <textarea
            v-model="settingsJsonText"
            rows="12"
            class="w-full border rounded-lg px-3 py-2 font-mono text-xs leading-relaxed"
            spellcheck="false"
          />
          <p v-if="settingsJsonError" class="text-red-600 text-xs">{{ settingsJsonError }}</p>
        </div>

        <div v-show="tab === 'import'" class="space-y-4">
          <div
            class="border-2 border-dashed border-outline-variant rounded-xl p-8 text-center hover:border-primary/50 transition-colors"
            :class="importing ? 'opacity-60 pointer-events-none' : ''"
          >
            <span class="material-symbols-outlined text-4xl text-on-surface-variant">upload_file</span>
            <p class="mt-2 font-medium">上传 PowerPoint (.pptx)</p>
            <p class="text-xs text-on-surface-variant mt-1">自动解析文本、形状与图片，生成 slides_json</p>
            <label class="inline-block mt-4 px-4 py-2 rounded-lg bg-primary text-on-primary cursor-pointer text-sm font-medium">
              选择文件
              <input type="file" accept=".pptx,application/vnd.openxmlformats-officedocument.presentationml.presentation" class="hidden" @change="onPptxSelected" />
            </label>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <label class="block">
              <span class="font-medium">解析为终端</span>
              <select v-model="importDevice" class="mt-1 w-full border rounded-lg px-3 py-2">
                <option value="mobile">移动端 (375×812)</option>
                <option value="web">网页版 (1280×720)</option>
              </select>
            </label>
            <label class="block">
              <span class="font-medium">导入分类</span>
              <select v-model="importCategory" class="mt-1 w-full border rounded-lg px-3 py-2">
                <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
              </select>
            </label>
          </div>

          <label class="flex items-center gap-2">
            <input v-model="importAndPublish" type="checkbox" />
            <span>解析后直接发布到模板页</span>
          </label>

          <p v-if="importMessage" class="text-xs" :class="importError ? 'text-red-600' : 'text-secondary'">{{ importMessage }}</p>
        </div>

        <p v-if="error" class="text-red-600">{{ error }}</p>
      </div>

      <div class="px-6 py-4 border-t border-outline-variant flex justify-end gap-2 shrink-0">
        <button type="button" class="px-4 py-2 border rounded-lg" @click="$emit('close')">取消</button>
        <button type="button" class="px-4 py-2 bg-primary text-on-primary rounded-lg disabled:opacity-50" :disabled="saving" @click="save">
          {{ saving ? '保存中…' : (form.enabled ? '保存并发布' : '保存') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
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
  initial: { type: Object, default: null },
  initialTab: { type: String, default: 'meta' },
})

const emit = defineEmits(['close', 'saved'])

const tabs = [
  { id: 'meta', label: '基本信息' },
  { id: 'slides', label: '幻灯片内容' },
  { id: 'settings', label: '项目设置' },
  { id: 'import', label: 'PPT 导入' },
]

const tab = ref('meta')
const saving = ref(false)
const error = ref('')
const slidesJsonText = ref('[]')
const settingsJsonText = ref('{}')
const slidesJsonError = ref('')
const settingsJsonError = ref('')
const importing = ref(false)
const importDevice = ref('mobile')
const importCategory = ref('简约商务')
const importAndPublish = ref(true)
const importMessage = ref('')
const importError = ref(false)

const form = reactive({
  id: '',
  title: '',
  description: '',
  category: '简约商务',
  device: 'mobile',
  pages: 1,
  premium: false,
  cover_gradient: 'from-primary to-primary-container',
  default_viewport: 'mobile-375',
  sort_order: 0,
  enabled: true,
})

const slideCount = computed(() => {
  try {
    const arr = JSON.parse(slidesJsonText.value || '[]')
    return Array.isArray(arr) ? arr.length : 0
  } catch {
    return 0
  }
})

watch(
  () => props.open,
  (v) => {
    if (!v) return
    tab.value = props.initialTab || 'meta'
    error.value = ''
    slidesJsonError.value = ''
    settingsJsonError.value = ''
    importMessage.value = ''
    importError.value = false
    if (props.mode === 'edit' && props.initial) {
      applyTemplate(props.initial)
    } else {
      resetForm()
    }
  }
)

function resetForm() {
  Object.assign(form, {
    id: '',
    title: '',
    description: '',
    category: '简约商务',
    device: 'mobile',
    pages: 1,
    premium: false,
    cover_gradient: 'from-primary to-primary-container',
    default_viewport: 'mobile-375',
    sort_order: 0,
    enabled: true,
  })
  slidesJsonText.value = '[]'
  settingsJsonText.value = JSON.stringify({ ...DEFAULT_SETTINGS }, null, 2)
}

function applyTemplate(t) {
  Object.assign(form, {
    id: t.id,
    title: t.title,
    description: t.description || '',
    category: t.category || '简约商务',
    device: t.device || 'mobile',
    pages: t.pages || 1,
    premium: !!t.premium,
    cover_gradient: t.cover_gradient || 'from-primary to-primary-container',
    default_viewport: t.default_viewport || 'mobile-375',
    sort_order: t.sort_order || 0,
    enabled: !!t.enabled,
  })
  slidesJsonText.value = JSON.stringify(t.slides_json || [], null, 2)
  settingsJsonText.value = JSON.stringify(t.settings_json || { ...DEFAULT_SETTINGS }, null, 2)
}

function onDeviceChange() {
  form.default_viewport = form.device === 'web' ? 'web-1280' : 'mobile-375'
  const settings = JSON.parse(settingsJsonText.value || '{}')
  settings.viewportId = form.default_viewport
  settingsJsonText.value = JSON.stringify(settings, null, 2)
}

function formatSlidesJson() {
  try {
    slidesJsonText.value = JSON.stringify(JSON.parse(slidesJsonText.value || '[]'), null, 2)
    slidesJsonError.value = ''
  } catch (e) {
    slidesJsonError.value = 'JSON 格式错误'
  }
}

function formatSettingsJson() {
  try {
    settingsJsonText.value = JSON.stringify(JSON.parse(settingsJsonText.value || '{}'), null, 2)
    settingsJsonError.value = ''
  } catch {
    settingsJsonError.value = 'JSON 格式错误'
  }
}

function parseJsonFields() {
  slidesJsonError.value = ''
  settingsJsonError.value = ''
  let slides = []
  let settings = {}
  try {
    slides = JSON.parse(slidesJsonText.value || '[]')
    if (!Array.isArray(slides)) throw new Error('slides_json 必须是数组')
  } catch (e) {
    slidesJsonError.value = `幻灯片 JSON 无效：${e.message}`
    tab.value = 'slides'
    return null
  }
  try {
    settings = JSON.parse(settingsJsonText.value || '{}')
    if (typeof settings !== 'object' || Array.isArray(settings)) throw new Error('settings_json 必须是对象')
  } catch (e) {
    settingsJsonError.value = `设置 JSON 无效：${e.message}`
    tab.value = 'settings'
    return null
  }
  return { slides, settings }
}

function applyParsedTemplate(parsed) {
  applyTemplate(parsed)
  if (props.mode === 'create') {
    form.id = parsed.id || form.id
  }
  form.pages = parsed.pages || slideCount.value || 1
  importMessage.value = `已解析 ${slideCount.value} 页，请在「基本信息」中确认后保存。`
  importError.value = false
  tab.value = 'meta'
}

async function onPptxSelected(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  importing.value = true
  importMessage.value = '正在解析 PPT…'
  importError.value = false
  try {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('device', importDevice.value)
    fd.append('category', importCategory.value)
    if (form.title) fd.append('title', form.title)

    if (importAndPublish.value && props.mode === 'create') {
      if (form.id) fd.append('template_id', form.id)
      if (form.title) fd.append('title', form.title)
      fd.append('enabled', 'true')
      const created = await api.importAdminPptxTemplate(fd)
      importMessage.value = `已导入并发布模板「${created.title}」`
      emit('saved', created)
      emit('close')
      return
    }

    const parsed = await api.parseAdminPptxTemplate(fd)
    applyParsedTemplate(parsed)
  } catch (err) {
    importMessage.value = err.message || '导入失败'
    importError.value = true
  } finally {
    importing.value = false
  }
}

async function save() {
  const parsed = parseJsonFields()
  if (!parsed) return
  saving.value = true
  error.value = ''
  const pages = Math.max(form.pages || 1, parsed.slides.length || 1)
  const body = {
    ...form,
    pages,
    slides_json: parsed.slides,
    settings_json: parsed.settings,
  }
  try {
    let result
    if (props.mode === 'create') {
      result = await api.createAdminTemplate(body)
    } else {
      const { id, ...rest } = body
      result = await api.updateAdminTemplate(id, rest)
    }
    emit('saved', result)
    emit('close')
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}
</script>
