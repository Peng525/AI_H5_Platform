<template>
  <AdminShell title="版式管理">
    <div class="flex flex-wrap justify-between items-center gap-3 mb-6">
      <p class="text-sm text-on-surface-variant">
        管理编辑器素材面板中的版式块。内置 14 种版式可编辑覆盖；自定义版式可新增。保存后用户在「版式」区即可使用。
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
      <div class="overflow-x-auto">
        <table class="w-full text-sm min-w-[720px]">
          <thead class="bg-surface-container-low text-left">
            <tr>
              <th class="px-4 py-3">ID</th>
              <th class="px-4 py-3">名称</th>
              <th class="px-4 py-3">类型</th>
              <th class="px-4 py-3">分组</th>
              <th class="px-4 py-3">展示</th>
              <th class="px-4 py-3">排序</th>
              <th class="px-4 py-3">状态</th>
              <th class="px-4 py-3 text-right">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in layouts" :key="item.id" class="border-t border-outline-variant/60">
              <td class="px-4 py-3 font-mono text-xs">{{ item.id }}</td>
              <td class="px-4 py-3 font-medium">
                <span class="inline-flex items-center gap-1.5">
                  <span class="material-symbols-outlined text-primary text-[18px]">{{ item.icon }}</span>
                  {{ item.label }}
                </span>
              </td>
              <td class="px-4 py-3">
                <span
                  v-if="item.builtin"
                  class="text-[10px] px-1.5 py-0.5 rounded bg-surface-container-high text-on-surface-variant"
                >
                  内置{{ item.overridden ? '·已覆盖' : '' }}
                </span>
                <span v-else class="text-[10px] px-1.5 py-0.5 rounded bg-primary/10 text-primary">自定义</span>
              </td>
              <td class="px-4 py-3">{{ groupLabel(item.group) }}</td>
              <td class="px-4 py-3">{{ placementLabel(item.placement) }}</td>
              <td class="px-4 py-3">{{ item.sort_order ?? '—' }}</td>
              <td class="px-4 py-3">
                <span :class="item.enabled !== false ? 'text-secondary' : 'text-on-surface-variant'">
                  {{ item.enabled !== false ? '已启用' : '已停用' }}
                </span>
              </td>
              <td class="px-4 py-3 text-right space-x-2 whitespace-nowrap">
                <button type="button" class="text-primary hover:underline" @click="openEdit(item)">编辑</button>
                <button
                  v-if="item.overridden"
                  type="button"
                  class="text-amber-700 hover:underline"
                  @click="resetDefault(item)"
                >
                  恢复默认
                </button>
                <button
                  v-if="!item.builtin"
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
    </div>

    <AdminLayoutEditor
      :open="editor.open"
      :mode="editor.mode"
      :initial="editor.data"
      :is-override-create="editor.isOverrideCreate"
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
    <ConfirmDialog
      :open="!!resetConfirm"
      title="恢复默认版式"
      :message="resetConfirm?.message || ''"
      confirm-text="恢复"
      cancel-text="取消"
      @confirm="onResetConfirm"
      @cancel="resetConfirm = null"
    />
  </AdminShell>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { api } from '../../api/client'
import AdminShell from '../../components/AdminShell.vue'
import AdminLayoutEditor from '../../components/admin/AdminLayoutEditor.vue'
import ConfirmDialog from '../../components/ConfirmDialog.vue'
import { useToast } from '../../composables/useToast.js'
import {
  BUSINESS_LAYOUT_BLOCKS,
  STORY_LAYOUT_BLOCKS,
  buildBlock,
  resetLayoutBlockIds,
} from '../../constants/layoutBlocks.js'

const { success: toastSuccess, error: toastError } = useToast()
const deleteConfirm = ref(null)
const resetConfirm = ref(null)

const dbLayouts = ref([])
const loading = ref(true)
const error = ref('')
const editor = reactive({ open: false, mode: 'create', data: null, isOverrideCreate: false })

const PRIMARY_IDS = new Set(['cover-minimal', 'section-title', 'bullets-three'])

const GROUP_LABELS = { business: '商务', story: '叙事', custom: '自定义' }
const PLACEMENT_LABELS = { primary: '主屏快捷', more: '更多版式' }

const layouts = computed(() => mergeLayouts(dbLayouts.value))

function groupLabel(g) {
  return GROUP_LABELS[g] || g
}

function placementLabel(p) {
  return PLACEMENT_LABELS[p] || p
}

function mergeLayouts(dbRows) {
  const dbMap = new Map(dbRows.map((row) => [row.id, row]))
  const merged = []

  const builtins = [
    ...BUSINESS_LAYOUT_BLOCKS.map((b) => ({ ...b, group: 'business' })),
    ...STORY_LAYOUT_BLOCKS.map((b) => ({ ...b, group: 'story' })),
  ]

  for (const b of builtins) {
    const db = dbMap.get(b.id)
    if (db) {
      merged.push({ ...db, builtin: true, overridden: true })
      dbMap.delete(b.id)
    } else {
      merged.push({
        id: b.id,
        label: b.label,
        icon: b.icon,
        group: b.group,
        placement: PRIMARY_IDS.has(b.id) ? 'primary' : 'more',
        sort_order: 0,
        enabled: true,
        builtin: true,
        overridden: false,
      })
    }
  }

  for (const db of dbMap.values()) {
    merged.push({ ...db, builtin: false, overridden: false })
  }

  return merged.sort((a, b) => {
    if (a.builtin !== b.builtin) return a.builtin ? -1 : 1
    return (a.sort_order ?? 100) - (b.sort_order ?? 100)
  })
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    dbLayouts.value = await api.listAdminLayouts()
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editor.mode = 'create'
  editor.data = null
  editor.isOverrideCreate = false
  editor.open = true
}

async function openEdit(item) {
  try {
    if (item.builtin && !item.overridden) {
      resetLayoutBlockIds()
      const elements = buildBlock(item.id, 'iphone', 'zjy-minimal')
      editor.mode = 'edit'
      editor.isOverrideCreate = true
      editor.data = {
        id: item.id,
        label: item.label,
        icon: item.icon,
        group: item.group,
        placement: item.placement,
        canvas_background: '',
        sort_order: item.sort_order ?? 0,
        enabled: true,
        elements,
        elements_web: [],
      }
      editor.open = true
      return
    }
    const detail = await api.getAdminLayout(item.id)
    editor.mode = 'edit'
    editor.isOverrideCreate = false
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

function resetDefault(item) {
  resetConfirm.value = {
    message: `确定将「${item.label}」恢复为代码内置默认？将删除当前覆盖配置。`,
    item,
  }
}

async function onResetConfirm() {
  const item = resetConfirm.value?.item
  resetConfirm.value = null
  if (!item) return
  try {
    await api.deleteAdminLayout(item.id)
    toastSuccess('已恢复为内置默认')
    await load()
  } catch (e) {
    toastError(e.message || '恢复失败')
  }
}

function onSaved() {
  load()
}

onMounted(load)
</script>
