<template>
  <AdminShell title="演示提示词">
    <div class="flex flex-wrap justify-between items-center gap-3 mb-6">
      <p class="text-sm text-on-surface-variant">
        管理生成页「演示文稿」Tab 中的提示词模板。保存后用户在生成页空态即可选用；内置模板可编辑但不可删除。
      </p>
      <button
        type="button"
        class="px-4 py-2 rounded-lg bg-primary text-on-primary text-sm font-medium"
        @click="openCreate"
      >
        新建模板
      </button>
    </div>

    <p v-if="loading" class="text-on-surface-variant">加载中…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>

    <div v-else class="bg-white rounded-xl border border-outline-variant overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-surface-container-low text-left">
          <tr>
            <th class="px-4 py-3">ID</th>
            <th class="px-4 py-3">标题</th>
            <th class="px-4 py-3">描述</th>
            <th class="px-4 py-3">排序</th>
            <th class="px-4 py-3">来源</th>
            <th class="px-4 py-3">状态</th>
            <th class="px-4 py-3 text-right">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!templates.length">
            <td colspan="7" class="px-4 py-8 text-center text-on-surface-variant">暂无模板，点击「新建模板」添加</td>
          </tr>
          <tr v-for="item in templates" :key="item.id" class="border-t border-outline-variant/60">
            <td class="px-4 py-3 font-mono text-xs">{{ item.id }}</td>
            <td class="px-4 py-3 font-medium">{{ item.title }}</td>
            <td class="px-4 py-3 text-on-surface-variant max-w-xs truncate">{{ item.description || '—' }}</td>
            <td class="px-4 py-3">{{ item.sort_order }}</td>
            <td class="px-4 py-3">
              <span :class="item.source === 'builtin' ? 'text-on-surface-variant' : 'text-primary'">
                {{ item.source === 'builtin' ? '内置' : '自定义' }}
              </span>
            </td>
            <td class="px-4 py-3">
              <span :class="item.enabled ? 'text-secondary' : 'text-on-surface-variant'">
                {{ item.enabled ? '已启用' : '已停用' }}
              </span>
            </td>
            <td class="px-4 py-3 text-right space-x-2 whitespace-nowrap">
              <button type="button" class="text-primary hover:underline" @click="openEdit(item)">编辑</button>
              <button
                v-if="item.source !== 'builtin'"
                type="button"
                class="text-red-600 hover:underline"
                @click="remove(item)"
              >
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div
      v-if="editor.open"
      class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/40"
      @click.self="editor.open = false"
    >
      <div class="bg-white rounded-xl border border-outline-variant w-full max-w-lg max-h-[90vh] overflow-y-auto shadow-elevated">
        <div class="px-5 py-4 border-b border-outline-variant flex items-center justify-between">
          <h2 class="font-semibold">{{ editor.mode === 'create' ? '新建演示提示词' : '编辑演示提示词' }}</h2>
          <button type="button" class="text-on-surface-variant hover:text-on-surface material-symbols-outlined" @click="editor.open = false">close</button>
        </div>
        <form class="p-5 space-y-4" @submit.prevent="save">
          <label v-if="editor.mode === 'create'" class="block text-sm">
            <span class="font-medium">ID</span>
            <input
              v-model="form.id"
              required
              pattern="[a-z0-9][a-z0-9-]{1,62}"
              class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 font-mono text-sm"
              placeholder="例如 coral-reef-edu"
            />
            <span class="text-xs text-on-surface-variant mt-1 block">小写字母、数字与连字符</span>
          </label>
          <label class="block text-sm">
            <span class="font-medium">标题</span>
            <input v-model="form.title" required class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" />
          </label>
          <label class="block text-sm">
            <span class="font-medium">描述</span>
            <input v-model="form.description" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" />
          </label>
          <label class="block text-sm">
            <span class="font-medium">预览图 URL（可选）</span>
            <input v-model="form.preview_url" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 text-sm" placeholder="https://…" />
          </label>
          <div class="space-y-3">
            <p class="text-sm font-medium">提示词要素</p>
            <label v-for="label in fieldLabels" :key="label" class="block text-sm">
              <span class="text-on-surface-variant">{{ label }}</span>
              <textarea
                v-model="formFields[label]"
                rows="2"
                class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 text-sm resize-y"
              />
            </label>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <label class="block text-sm">
              <span class="font-medium">排序</span>
              <input v-model.number="form.sort_order" type="number" min="0" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" />
            </label>
            <label class="flex items-center gap-2 text-sm pt-6">
              <input v-model="form.enabled" type="checkbox" class="rounded border-outline-variant" />
              <span>启用</span>
            </label>
          </div>
          <p v-if="saveError" class="text-red-600 text-sm">{{ saveError }}</p>
          <div class="flex gap-2 pt-2">
            <button type="submit" class="px-4 py-2 bg-primary text-on-primary rounded-lg text-sm font-medium" :disabled="saving">
              {{ saving ? '保存中…' : '保存' }}
            </button>
            <button type="button" class="px-4 py-2 border border-outline-variant rounded-lg text-sm" @click="editor.open = false">取消</button>
          </div>
        </form>
      </div>
    </div>

    <ConfirmDialog
      :open="!!deleteConfirm"
      title="删除演示提示词"
      :message="deleteConfirm?.message || ''"
      confirm-text="删除"
      cancel-text="取消"
      danger
      @confirm="onDeleteConfirm"
      @cancel="deleteConfirm = null"
    />
  </AdminShell>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../../api/client'
import AdminShell from '../../components/AdminShell.vue'
import ConfirmDialog from '../../components/ConfirmDialog.vue'
import { DECK_PROMPT_FIELD_LABELS } from '../../constants/deckPromptTemplates'
import { useToast } from '../../composables/useToast.js'

const { success: toastSuccess, error: toastError } = useToast()

const fieldLabels = DECK_PROMPT_FIELD_LABELS
const templates = ref([])
const loading = ref(true)
const error = ref('')
const saving = ref(false)
const saveError = ref('')
const deleteConfirm = ref(null)
const editor = reactive({ open: false, mode: 'create' })

const form = reactive({
  id: '',
  title: '',
  description: '',
  preview_url: '',
  sort_order: 100,
  enabled: true,
})
const formFields = reactive(Object.fromEntries(fieldLabels.map((l) => [l, ''])))

function emptyFields() {
  fieldLabels.forEach((l) => {
    formFields[l] = ''
  })
}

function fieldsFromTemplate(tpl) {
  emptyFields()
  for (const f of tpl?.fields || []) {
    if (fieldLabels.includes(f.label)) {
      formFields[f.label] = f.value || ''
    }
  }
}

function buildFieldsPayload() {
  return fieldLabels
    .map((label) => ({ label, value: (formFields[label] || '').trim() }))
    .filter((f) => f.value)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    templates.value = await api.listAdminDeckPrompts()
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editor.mode = 'create'
  editor.open = true
  saveError.value = ''
  Object.assign(form, { id: '', title: '', description: '', preview_url: '', sort_order: 100, enabled: true })
  emptyFields()
}

async function openEdit(item) {
  try {
    const detail = await api.getAdminDeckPrompt(item.id)
    editor.mode = 'edit'
    editor.open = true
    saveError.value = ''
    Object.assign(form, {
      id: detail.id,
      title: detail.title,
      description: detail.description || '',
      preview_url: detail.preview_url || '',
      sort_order: detail.sort_order ?? 100,
      enabled: detail.enabled !== false,
    })
    fieldsFromTemplate(detail)
  } catch (e) {
    toastError(e.message || '加载详情失败')
  }
}

async function save() {
  const fields = buildFieldsPayload()
  if (!fields.length) {
    saveError.value = '至少填写一项提示词要素'
    return
  }
  saving.value = true
  saveError.value = ''
  try {
    const body = {
      title: form.title.trim(),
      description: form.description.trim(),
      preview_url: form.preview_url.trim(),
      fields,
      sort_order: form.sort_order,
      enabled: form.enabled,
    }
    if (editor.mode === 'create') {
      await api.createAdminDeckPrompt({ id: form.id.trim(), ...body })
      toastSuccess('模板已创建')
    } else {
      await api.updateAdminDeckPrompt(form.id, body)
      toastSuccess('模板已保存')
    }
    editor.open = false
    await load()
  } catch (e) {
    saveError.value = e.message || '保存失败'
  } finally {
    saving.value = false
  }
}

function remove(item) {
  deleteConfirm.value = { message: `确定删除「${item.title}」？`, item }
}

async function onDeleteConfirm() {
  const item = deleteConfirm.value?.item
  deleteConfirm.value = null
  if (!item) return
  try {
    await api.deleteAdminDeckPrompt(item.id)
    toastSuccess('模板已删除')
    await load()
  } catch (e) {
    toastError(e.message || '删除失败')
  }
}

onMounted(load)
</script>
