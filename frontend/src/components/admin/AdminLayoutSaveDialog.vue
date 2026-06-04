<template>
  <div v-if="open" class="fixed inset-0 z-[80] flex items-center justify-center bg-black/40 p-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[92vh] flex flex-col overflow-hidden">
      <div class="px-6 py-4 border-b border-outline-variant shrink-0">
        <h2 class="text-lg font-bold">保存版式</h2>
        <p class="text-xs text-on-surface-variant mt-0.5">将当前画布内容写回版式库，素材面板即时生效</p>
      </div>

      <div class="flex-1 overflow-y-auto p-6 text-sm space-y-3">
        <label class="block">
          <span class="font-medium">显示名称</span>
          <input v-model="form.label" required class="mt-1 w-full border rounded-lg px-3 py-2" />
        </label>
        <div class="grid grid-cols-2 gap-3">
          <label class="block">
            <span class="font-medium">图标（Material Symbol）</span>
            <input v-model="form.icon" class="mt-1 w-full border rounded-lg px-3 py-2 font-mono text-xs" />
          </label>
          <label class="block">
            <span class="font-medium">排序</span>
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
          <span class="font-medium">整页套用默认背景（可选）</span>
          <input v-model="form.canvas_background" class="mt-1 w-full border rounded-lg px-3 py-2 font-mono text-xs" />
        </label>
        <label class="flex items-center gap-2">
          <input v-model="form.enabled" type="checkbox" />
          <span>在编辑器素材面板展示</span>
        </label>
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
          {{ saving ? '保存中…' : '保存版式' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { api } from '../../api/client'

const props = defineProps({
  open: Boolean,
  layoutId: { type: String, default: '' },
  projectId: { type: [String, Number], default: null },
  initial: { type: Object, default: null },
})

const emit = defineEmits(['close', 'saved'])

const saving = ref(false)
const error = ref('')
const form = reactive({
  label: '',
  icon: 'dashboard',
  group: 'custom',
  placement: 'more',
  canvas_background: '',
  sort_order: 100,
  enabled: true,
})

watch(
  () => props.open,
  (v) => {
    if (!v) return
    error.value = ''
    const t = props.initial || {}
    Object.assign(form, {
      label: t.label || '',
      icon: t.icon || 'dashboard',
      group: t.group || 'custom',
      placement: t.placement || 'more',
      canvas_background: t.canvas_background || '',
      sort_order: t.sort_order ?? 100,
      enabled: t.enabled !== false,
    })
  }
)

async function save() {
  if (!props.layoutId || !props.projectId) return
  saving.value = true
  error.value = ''
  try {
    await flushCanvas()
    const result = await api.saveLayoutFromProject(props.layoutId, {
      project_public_id: String(props.projectId),
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

async function flushCanvas() {
  const { flushCanvasSave } = await import('../../composables/useEditorCanvasSave')
  await flushCanvasSave()
}
</script>
