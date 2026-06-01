<template>
  <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-3xl max-h-[92vh] flex flex-col overflow-hidden">
      <div class="px-6 py-4 border-b border-outline-variant flex items-center justify-between shrink-0">
        <div>
          <h2 class="text-lg font-bold">{{ mode === 'create' ? '新建版式' : '编辑版式' }}</h2>
          <p class="text-xs text-on-surface-variant mt-0.5">保存并启用后，将出现在编辑器素材面板的版式区</p>
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

      <form class="flex-1 overflow-y-auto p-6 text-sm space-y-4" @submit.prevent="save">
        <div v-show="tab === 'meta'" class="space-y-3">
          <label v-if="mode === 'create'" class="block">
            <span class="font-medium">版式 ID</span>
            <input
              v-model="form.id"
              required
              class="mt-1 w-full border rounded-lg px-3 py-2 font-mono text-xs"
              placeholder="custom-team-intro"
            />
            <span class="text-[10px] text-on-surface-variant">小写字母、数字与连字符</span>
          </label>
          <label class="block">
            <span class="font-medium">显示名称</span>
            <input v-model="form.label" required class="mt-1 w-full border rounded-lg px-3 py-2" />
          </label>
          <div class="grid grid-cols-2 gap-3">
            <label class="block">
              <span class="font-medium">图标（Material Symbol）</span>
              <input v-model="form.icon" class="mt-1 w-full border rounded-lg px-3 py-2 font-mono text-xs" placeholder="dashboard" />
            </label>
            <label class="block">
              <span class="font-medium">排序（越小越靠前）</span>
              <input v-model.number="form.sort_order" type="number" class="mt-1 w-full border rounded-lg px-3 py-2" />
            </label>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <label class="block">
              <span class="font-medium">分组</span>
              <select v-model="form.group" class="mt-1 w-full border rounded-lg px-3 py-2">
                <option value="business">商务</option>
                <option value="story">叙事</option>
                <option value="custom">自定义</option>
              </select>
            </label>
            <label class="block">
              <span class="font-medium">展示位置</span>
              <select v-model="form.placement" class="mt-1 w-full border rounded-lg px-3 py-2">
                <option value="more">更多版式弹窗</option>
                <option value="primary">主屏快捷版式</option>
              </select>
            </label>
          </div>
          <label class="block">
            <span class="font-medium">整页套用时的默认背景（可选）</span>
            <input v-model="form.canvas_background" class="mt-1 w-full border rounded-lg px-3 py-2 font-mono text-xs" placeholder="#ffffff 或 linear-gradient(...)" />
          </label>
          <label class="flex items-center gap-2">
            <input v-model="form.enabled" type="checkbox" />
            <span>启用（在编辑器素材面板展示）</span>
          </label>
        </div>

        <div v-show="tab === 'elements'" class="space-y-3">
          <p class="text-xs text-on-surface-variant">
            填写与画布保存一致的 <code class="bg-surface-container-low px-1 rounded">canvas_elements</code> JSON 数组。可从编辑器导出当前页元素后粘贴。
          </p>
          <label class="block">
            <span class="font-medium">手机端元素 JSON</span>
            <textarea
              v-model="elementsText"
              rows="12"
              class="mt-1 w-full border rounded-lg px-3 py-2 font-mono text-xs"
              spellcheck="false"
            />
          </label>
          <label class="block">
            <span class="font-medium">网页端元素 JSON（可选，留空则使用手机端）</span>
            <textarea
              v-model="elementsWebText"
              rows="8"
              class="mt-1 w-full border rounded-lg px-3 py-2 font-mono text-xs"
              spellcheck="false"
            />
          </label>
        </div>

        <p v-if="error" class="text-red-600 text-sm">{{ error }}</p>

        <div class="flex justify-end gap-2 pt-2 border-t border-outline-variant">
          <button type="button" class="px-4 py-2 rounded-lg border border-outline-variant" @click="$emit('close')">取消</button>
          <button type="submit" class="px-4 py-2 rounded-lg bg-primary text-on-primary font-medium" :disabled="saving">
            {{ saving ? '保存中…' : '保存' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { api } from '../../api/client'

const SAMPLE_ELEMENTS = `[
  {
    "type": "text",
    "x": 20,
    "y": 120,
    "width": 320,
    "height": 56,
    "zIndex": 2,
    "content": "版式标题",
    "style": {
      "fontSize": 22,
      "fontWeight": "bold",
      "color": "#1b1b1c",
      "textAlign": "center",
      "background": "transparent"
    }
  }
]`

const props = defineProps({
  open: { type: Boolean, default: false },
  mode: { type: String, default: 'create' },
  initial: { type: Object, default: null },
  /** 编辑内置版式首次保存时走创建 */
  isOverrideCreate: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'saved'])

const tabs = [
  { id: 'meta', label: '基本信息' },
  { id: 'elements', label: '画布元素' },
]

const tab = ref('meta')
const saving = ref(false)
const error = ref('')
const elementsText = ref(SAMPLE_ELEMENTS)
const elementsWebText = ref('[]')

const form = reactive({
  id: '',
  label: '',
  icon: 'dashboard',
  group: 'custom',
  placement: 'more',
  canvas_background: '',
  sort_order: 100,
  enabled: true,
})

function resetForm(data = null) {
  error.value = ''
  tab.value = 'meta'
  if (data) {
    form.id = data.id || ''
    form.label = data.label || ''
    form.icon = data.icon || 'dashboard'
    form.group = data.group || 'custom'
    form.placement = data.placement || 'more'
    form.canvas_background = data.canvas_background || ''
    form.sort_order = data.sort_order ?? 100
    form.enabled = data.enabled !== false
    elementsText.value = JSON.stringify(data.elements || [], null, 2)
    elementsWebText.value = JSON.stringify(data.elements_web || [], null, 2)
  } else {
    form.id = ''
    form.label = ''
    form.icon = 'dashboard'
    form.group = 'custom'
    form.placement = 'more'
    form.canvas_background = ''
    form.sort_order = 100
    form.enabled = true
    elementsText.value = SAMPLE_ELEMENTS
    elementsWebText.value = '[]'
  }
}

watch(
  () => props.open,
  (v) => {
    if (v) resetForm(props.mode === 'edit' ? props.initial : null)
  }
)

function parseJsonArray(text, fieldName) {
  const trimmed = (text || '').trim()
  if (!trimmed || trimmed === '[]') return []
  let parsed
  try {
    parsed = JSON.parse(trimmed)
  } catch {
    throw new Error(`${fieldName} JSON 格式无效`)
  }
  if (!Array.isArray(parsed)) throw new Error(`${fieldName} 必须是数组`)
  return parsed
}

async function save() {
  error.value = ''
  saving.value = true
  try {
    const elements = parseJsonArray(elementsText.value, '手机端元素')
    const elements_web = parseJsonArray(elementsWebText.value, '网页端元素')
    if (!elements.length && !elements_web.length) {
      throw new Error('至少填写手机端或网页端画布元素')
    }
    const body = {
      label: form.label.trim(),
      icon: form.icon.trim() || 'dashboard',
      group: form.group,
      placement: form.placement,
      canvas_background: form.canvas_background.trim(),
      sort_order: Number(form.sort_order) || 100,
      enabled: !!form.enabled,
      elements,
      elements_web,
    }
    if (props.mode === 'create' || props.isOverrideCreate) {
      body.id = form.id.trim()
      await api.createAdminLayout(body)
    } else {
      await api.updateAdminLayout(form.id, body)
    }
    emit('saved')
    emit('close')
  } catch (e) {
    error.value = e.message || '保存失败'
  } finally {
    saving.value = false
  }
}
</script>
