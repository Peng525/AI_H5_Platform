<template>
  <AdminShell title="H5 模板管理">
    <div class="flex justify-between items-center mb-6">
      <p class="text-sm text-on-surface-variant">管理探索模板库，用户可在「探索模板」页使用</p>
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
            <th class="px-4 py-3">分类</th>
            <th class="px-4 py-3">终端</th>
            <th class="px-4 py-3">状态</th>
            <th class="px-4 py-3 text-right">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in templates" :key="t.id" class="border-t border-outline-variant/60">
            <td class="px-4 py-3 font-mono text-xs">{{ t.id }}</td>
            <td class="px-4 py-3 font-medium">{{ t.title }}</td>
            <td class="px-4 py-3">{{ t.category }}</td>
            <td class="px-4 py-3">{{ t.device === 'web' ? '网页版' : '移动端' }}</td>
            <td class="px-4 py-3">
              <span :class="t.enabled ? 'text-secondary' : 'text-on-surface-variant'">
                {{ t.enabled ? '已上架' : '已下架' }}
              </span>
            </td>
            <td class="px-4 py-3 text-right space-x-2">
              <button type="button" class="text-primary hover:underline" @click="openEdit(t)">编辑</button>
              <button type="button" class="text-red-600 hover:underline" @click="remove(t)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="dialog.open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-6">
        <h2 class="text-lg font-bold mb-4">{{ dialog.mode === 'create' ? '新建模板' : '编辑模板' }}</h2>
        <form class="space-y-3 text-sm" @submit.prevent="save">
          <label v-if="dialog.mode === 'create'" class="block">
            <span class="font-medium">模板 ID</span>
            <input v-model="form.id" required class="mt-1 w-full border rounded-lg px-3 py-2" placeholder="tech-launch-mobile" />
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
              <input v-model="form.category" class="mt-1 w-full border rounded-lg px-3 py-2" />
            </label>
            <label class="block">
              <span class="font-medium">终端</span>
              <select v-model="form.device" class="mt-1 w-full border rounded-lg px-3 py-2">
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
              <span class="font-medium">默认视口</span>
              <input v-model="form.default_viewport" class="mt-1 w-full border rounded-lg px-3 py-2" />
            </label>
          </div>
          <label class="block">
            <span class="font-medium">封面渐变 Tailwind 类</span>
            <input v-model="form.cover_gradient" class="mt-1 w-full border rounded-lg px-3 py-2" />
          </label>
          <label class="flex items-center gap-2">
            <input v-model="form.premium" type="checkbox" />
            <span>高级模板</span>
          </label>
          <label class="flex items-center gap-2">
            <input v-model="form.enabled" type="checkbox" />
            <span>上架展示</span>
          </label>
          <p v-if="dialog.error" class="text-red-600">{{ dialog.error }}</p>
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" class="px-4 py-2 border rounded-lg" @click="dialog.open = false">取消</button>
            <button type="submit" class="px-4 py-2 bg-primary text-on-primary rounded-lg" :disabled="dialog.saving">
              {{ dialog.saving ? '保存中…' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </AdminShell>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../../api/client'
import AdminShell from '../../components/AdminShell.vue'

const templates = ref([])
const loading = ref(true)
const error = ref('')
const dialog = reactive({ open: false, mode: 'create', saving: false, error: '' })
const form = reactive({
  id: '',
  title: '',
  description: '',
  category: '',
  device: 'mobile',
  pages: 5,
  premium: false,
  cover_gradient: 'from-primary to-primary-container',
  default_viewport: 'mobile-375',
  enabled: true,
})

onMounted(load)

async function load() {
  loading.value = true
  error.value = ''
  try {
    templates.value = await api.listAdminTemplates()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function resetForm() {
  Object.assign(form, {
    id: '',
    title: '',
    description: '',
    category: '',
    device: 'mobile',
    pages: 5,
    premium: false,
    cover_gradient: 'from-primary to-primary-container',
    default_viewport: 'mobile-375',
    enabled: true,
  })
}

function openCreate() {
  resetForm()
  dialog.mode = 'create'
  dialog.error = ''
  dialog.open = true
}

function openEdit(t) {
  Object.assign(form, { ...t, premium: !!t.premium, enabled: !!t.enabled })
  dialog.mode = 'edit'
  dialog.error = ''
  dialog.open = true
}

async function save() {
  dialog.saving = true
  dialog.error = ''
  try {
    const body = { ...form }
    if (dialog.mode === 'create') {
      await api.createAdminTemplate(body)
    } else {
      const { id, ...rest } = body
      await api.updateAdminTemplate(id, rest)
    }
    dialog.open = false
    await load()
  } catch (e) {
    dialog.error = e.message
  } finally {
    dialog.saving = false
  }
}

async function remove(t) {
  if (!confirm(`确定删除模板「${t.title}」？`)) return
  try {
    await api.deleteAdminTemplate(t.id)
    await load()
  } catch (e) {
    error.value = e.message
  }
}
</script>
