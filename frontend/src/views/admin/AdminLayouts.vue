<template>
  <AdminShell title="版式管理">
    <div class="flex flex-wrap justify-between items-center gap-3 mb-6">
      <p class="text-sm text-on-surface-variant">
        点击「编辑」进入与用户端相同的可视化编辑器修改版式；保存后素材面板即时生效。内置 14 种版式可覆盖编辑。
      </p>
      <button
        type="button"
        class="px-4 py-2 rounded-lg bg-primary text-on-primary text-sm font-medium disabled:opacity-50"
        :disabled="!!openingAction || cooldownLeft > 0"
        @click="quickCreate"
      >
        {{ openingAction === 'create' ? '创建中…' : cooldownLeft > 0 ? `请稍候 ${cooldownLeft}s` : '新建版式' }}
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
                <button
                  type="button"
                  class="text-primary hover:underline disabled:opacity-40"
                  :disabled="!!openingAction || cooldownLeft > 0"
                  @click="openVisualEdit(item)"
                >
                  {{ openingAction === item.id ? '打开中…' : '编辑' }}
                </button>
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
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../../api/client'
import AdminShell from '../../components/AdminShell.vue'
import ConfirmDialog from '../../components/ConfirmDialog.vue'
import { useToast } from '../../composables/useToast.js'
import {
  BUSINESS_LAYOUT_BLOCKS,
  STORY_LAYOUT_BLOCKS,
  buildBlock,
  resetLayoutBlockIds,
} from '../../constants/layoutBlocks.js'

const OPEN_COOLDOWN_MS = 3000

const router = useRouter()
const { success: toastSuccess, error: toastError } = useToast()
const deleteConfirm = ref(null)
const resetConfirm = ref(null)

const dbLayouts = ref([])
const loading = ref(true)
const error = ref('')
const openingAction = ref(null)
const cooldownLeft = ref(0)

let cooldownTimer = null

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

function startCooldown() {
  cooldownLeft.value = Math.ceil(OPEN_COOLDOWN_MS / 1000)
  if (cooldownTimer) clearInterval(cooldownTimer)
  cooldownTimer = setInterval(() => {
    cooldownLeft.value -= 1
    if (cooldownLeft.value <= 0) {
      cooldownLeft.value = 0
      clearInterval(cooldownTimer)
      cooldownTimer = null
    }
  }, 1000)
}

function simplifyError(msg) {
  if (!msg) return '打开失败，请稍后重试'
  if (msg.includes('greenlet_spawn')) return '打开编辑草稿失败，请重启后端服务后再试'
  if (msg.length > 120) return `${msg.slice(0, 120)}…`
  return msg
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

async function quickCreate() {
  if (openingAction.value || cooldownLeft.value > 0) return
  openingAction.value = 'create'
  try {
    const draft = await api.quickCreateLayoutDraft({ label: '新版式' })
    goEditor({ layoutId: draft.layout_id, projectId: draft.project_public_id })
  } catch (e) {
    toastError(simplifyError(e.message))
    startCooldown()
  } finally {
    openingAction.value = null
  }
}

async function openVisualEdit(item) {
  if (openingAction.value || cooldownLeft.value > 0) return
  openingAction.value = item.id
  try {
    let seed = null
    if (item.builtin && !item.overridden) {
      resetLayoutBlockIds()
      seed = {
        label: item.label,
        icon: item.icon,
        group: item.group,
        placement: item.placement,
        elements: buildBlock(item.id, 'iphone', 'zjy-minimal'),
        elements_web: [],
      }
    }
    const draft = await api.startLayoutDraft(item.id, seed)
    goEditor({ layoutId: item.id, projectId: draft.project_public_id })
  } catch (e) {
    toastError(simplifyError(e.message))
    startCooldown()
  } finally {
    openingAction.value = null
  }
}

function goEditor({ layoutId, projectId }) {
  router.push({
    path: `/editor/${projectId}`,
    query: { adminLayout: layoutId },
  })
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

onMounted(load)

onUnmounted(() => {
  if (cooldownTimer) clearInterval(cooldownTimer)
})
</script>
