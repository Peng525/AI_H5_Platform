<template>
  <AdminShell title="H5 模板管理">
    <div class="flex flex-wrap justify-between items-center gap-3 mb-6">
      <p class="text-sm text-on-surface-variant">创建、编辑模板并发布到「探索模板」页；支持上传 PPT 自动解析</p>
      <div class="flex gap-2">
        <button
          type="button"
          class="px-4 py-2 rounded-lg border border-outline-variant text-sm font-medium hover:bg-surface-container-low"
          @click="openImport"
        >
          从 PPT 导入
        </button>
        <button
          type="button"
          class="px-4 py-2 rounded-lg bg-primary text-on-primary text-sm font-medium"
          @click="openCreate"
        >
          新建模板
        </button>
      </div>
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
            <th class="px-4 py-3">页数</th>
            <th class="px-4 py-3">状态</th>
            <th class="px-4 py-3 text-right">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in templates" :key="t.id" class="border-t border-outline-variant/60">
            <td class="px-4 py-3 font-mono text-xs">{{ t.id }}</td>
            <td class="px-4 py-3 font-medium">
              {{ t.title }}
              <span v-if="t.featured" class="ml-1 text-[10px] text-secondary">有内容</span>
            </td>
            <td class="px-4 py-3">{{ t.category }}</td>
            <td class="px-4 py-3">{{ t.device === 'web' ? '网页版' : '移动端' }}</td>
            <td class="px-4 py-3">{{ t.pages }}</td>
            <td class="px-4 py-3">
              <span :class="t.enabled ? 'text-secondary' : 'text-on-surface-variant'">
                {{ t.enabled ? '已上架' : '已下架' }}
              </span>
            </td>
            <td class="px-4 py-3 text-right space-x-2 whitespace-nowrap">
              <button type="button" class="text-primary hover:underline" @click="openEdit(t)">编辑</button>
              <button type="button" class="text-red-600 hover:underline" @click="remove(t)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <AdminTemplateEditor
      :open="editor.open"
      :mode="editor.mode"
      :initial="editor.data"
      :initial-tab="editor.tab"
      @close="editor.open = false"
      @saved="onSaved"
    />
  </AdminShell>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../../api/client'
import AdminShell from '../../components/AdminShell.vue'
import AdminTemplateEditor from '../../components/admin/AdminTemplateEditor.vue'

const templates = ref([])
const loading = ref(true)
const error = ref('')
const editor = reactive({ open: false, mode: 'create', data: null, tab: 'meta' })

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

function openCreate() {
  editor.mode = 'create'
  editor.data = null
  editor.tab = 'meta'
  editor.open = true
}

function openImport() {
  editor.mode = 'create'
  editor.data = null
  editor.tab = 'import'
  editor.open = true
}

async function openEdit(t) {
  try {
    const detail = await api.getAdminTemplate(t.id)
    editor.mode = 'edit'
    editor.data = detail
    editor.tab = 'meta'
    editor.open = true
  } catch (e) {
    error.value = e.message
  }
}

function onSaved() {
  editor.open = false
  load()
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
