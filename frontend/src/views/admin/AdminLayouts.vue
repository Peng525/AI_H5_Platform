<template>
  <AdminShell title="版式管理">
    <div class="flex flex-wrap justify-between items-center gap-3 mb-6">
      <p class="text-sm text-on-surface-variant">
        管理编辑器素材面板中的版式块。内置 14 种版式由代码提供；此处可新增自定义标准模板，保存后用户在「版式」区即可使用。
      </p>
      <button
        type="button"
        class="px-4 py-2 rounded-lg bg-primary text-on-primary text-sm font-medium"
        @click="openCreate"
      >
        新建版式
      </button>
    </div>

    <p v-if="loading" class="text-on-surface-variant">加载中…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>

    <div v-else class="bg-white rounded-xl border border-outline-variant overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-surface-container-low text-left">
          <tr>
            <th class="px-4 py-3">ID</th>
            <th class="px-4 py-3">名称</th>
            <th class="px-4 py-3">分组</th>
            <th class="px-4 py-3">展示</th>
            <th class="px-4 py-3">排序</th>
            <th class="px-4 py-3">状态</th>
            <th class="px-4 py-3 text-right">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!layouts.length">
            <td colspan="7" class="px-4 py-8 text-center text-on-surface-variant">暂无自定义版式，点击「新建版式」添加</td>
          </tr>
          <tr v-for="item in layouts" :key="item.id" class="border-t border-outline-variant/60">
            <td class="px-4 py-3 font-mono text-xs">{{ item.id }}</td>
            <td class="px-4 py-3 font-medium flex items-center gap-1.5">
              <span class="material-symbols-outlined text-primary text-[18px]">{{ item.icon }}</span>
              {{ item.label }}
            </td>
            <td class="px-4 py-3">{{ groupLabel(item.group) }}</td>
            <td class="px-4 py-3">{{ placementLabel(item.placement) }}</td>
            <td class="px-4 py-3">{{ item.sort_order }}</td>
            <td class="px-4 py-3">
              <span :class="item.enabled ? 'text-secondary' : 'text-on-surface-variant'">
                {{ item.enabled ? '已启用' : '已停用' }}
              </span>
            </td>
            <td class="px-4 py-3 text-right space-x-2 whitespace-nowrap">
              <button type="button" class="text-primary hover:underline" @click="openEdit(item)">编辑</button>
              <button type="button" class="text-red-600 hover:underline" @click="remove(item)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <AdminLayoutEditor
      :open="editor.open"
      :mode="editor.mode"
      :initial="editor.data"
      @close="editor.open = false"
      @saved="onSaved"
    />
    <ConfirmDialog
      :open="!!deleteConfirm"
      title="删除版式"
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
import AdminLayoutEditor from '../../components/admin/AdminLayoutEditor.vue'
import ConfirmDialog from '../../components/ConfirmDialog.vue'
import { useToast } from '../../composables/useToast.js'

const { success: toastSuccess, error: toastError } = useToast()
const deleteConfirm = ref(null)

const layouts = ref([])
const loading = ref(true)
const error = ref('')
const editor = reactive({ open: false, mode: 'create', data: null })

const GROUP_LABELS = { business: '商务', story: '叙事', custom: '自定义' }
const PLACEMENT_LABELS = { primary: '主屏快捷', more: '更多版式' }

function groupLabel(g) {
  return GROUP_LABELS[g] || g
}

function placementLabel(p) {
  return PLACEMENT_LABELS[p] || p
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    layouts.value = await api.listAdminLayouts()
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editor.mode = 'create'
  editor.data = null
  editor.open = true
}

async function openEdit(item) {
  try {
    const detail = await api.getAdminLayout(item.id)
    editor.mode = 'edit'
    editor.data = detail
    editor.open = true
  } catch (e) {
    toastError(e.message || '加载详情失败')
  }
}

function remove(item) {
  deleteConfirm.value = {
    message: `确定删除版式「${item.label}」？`,
    item,
  }
}

async function onDeleteConfirm() {
  const item = deleteConfirm.value?.item
  deleteConfirm.value = null
  if (!item) return
  try {
    await api.deleteAdminLayout(item.id)
    toastSuccess('版式已删除')
    await load()
  } catch (e) {
    toastError(e.message || '删除失败')
  }
}

function onSaved() {
  load()
}

onMounted(load)
</script>
