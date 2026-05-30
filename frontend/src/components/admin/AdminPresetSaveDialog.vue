<template>
  <div v-if="open" class="fixed inset-0 z-[80] flex items-center justify-center bg-black/40 p-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[92vh] flex flex-col overflow-hidden">
      <div class="px-6 py-4 border-b border-outline-variant shrink-0">
        <h2 class="text-lg font-bold">保存为模板预设</h2>
        <p class="text-xs text-on-surface-variant mt-0.5">将当前编辑器内容写回探索模板库</p>
      </div>

      <div class="flex-1 overflow-y-auto p-6 text-sm space-y-3">
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
            <select v-model="form.device" class="mt-1 w-full border rounded-lg px-3 py-2">
              <option value="mobile">移动端</option>
              <option value="web">网页版</option>
            </select>
          </label>
        </div>
        <label class="block">
          <span class="font-medium">封面渐变 Tailwind 类</span>
          <input v-model="form.cover_gradient" class="mt-1 w-full border rounded-lg px-3 py-2 font-mono text-xs" />
        </label>
        <label class="block">
          <span class="font-medium">排序（越小越靠前）</span>
          <input v-model.number="form.sort_order" type="number" class="mt-1 w-full border rounded-lg px-3 py-2" />
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
        <p v-if="error" class="text-red-600 text-xs">{{ error }}</p>
      </div>

      <div class="px-6 py-4 border-t border-outline-variant flex justify-end gap-2 shrink-0">
        <button type="button" class="px-4 py-2 border rounded-lg" :disabled="saving" @click="$emit('close')">取消</button>
        <button
          type="button"
          class="px-4 py-2 bg-primary text-on-primary rounded-lg disabled:opacity-50"
          :disabled="saving"
          @click="save"
        >
          {{ saving ? '保存中…' : '保存预设' }}
        </button>
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
  templateId: { type: String, default: '' },
  projectId: { type: [String, Number], default: null },
  initial: { type: Object, default: null },
})

const emit = defineEmits(['close', 'saved'])

const saving = ref(false)
const error = ref('')
const form = reactive({
  title: '',
  description: '',
  category: '简约商务',
  device: 'mobile',
  premium: false,
  cover_gradient: 'from-primary to-primary-container',
  sort_order: 0,
  enabled: true,
})

watch(
  () => props.open,
  (v) => {
    if (!v) return
    error.value = ''
    const t = props.initial || {}
    Object.assign(form, {
      title: t.title || '',
      description: t.description || '',
      category: t.category || '简约商务',
      device: t.device || 'mobile',
      premium: !!t.premium,
      cover_gradient: t.cover_gradient || 'from-primary to-primary-container',
      sort_order: t.sort_order || 0,
      enabled: t.enabled !== false,
    })
  }
)

async function save() {
  if (!props.templateId || !props.projectId) return
  saving.value = true
  error.value = ''
  try {
    const result = await api.saveTemplatePreset(props.templateId, {
      project_id: Number(props.projectId),
      ...form,
    })
    emit('saved', result)
    emit('close')
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}
</script>
