<template>
  <AdminShell title="H5 模板管理">
    <div class="flex flex-wrap justify-between items-center gap-3 mb-6">
      <p class="text-sm text-on-surface-variant">
        可视化编辑模板（与用户端相同编辑器：版式、音乐、素材、AI）；保存为探索模板预设
      </p>
      <div class="flex gap-2">
        <button
          type="button"
          class="px-4 py-2 rounded-lg border border-outline-variant text-sm font-medium hover:bg-surface-container-low disabled:opacity-50"
          :disabled="!!openingAction"
          @click="openImport"
        >
          从 PPT 导入
        </button>
        <button
          type="button"
          class="px-4 py-2 rounded-lg bg-primary text-on-primary text-sm font-medium disabled:opacity-50"
          :disabled="!!openingAction || cooldownLeft > 0"
          @click="quickCreate"
        >
          {{ openingAction === 'create' ? '创建中…' : cooldownLeft > 0 ? `请稍候 ${cooldownLeft}s` : '新建模板' }}
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
              <button
                type="button"
                class="text-primary hover:underline disabled:opacity-40 disabled:no-underline disabled:cursor-not-allowed"
                :disabled="!!openingAction || cooldownLeft > 0"
                @click="openVisualEdit(t)"
              >
                {{ openingAction === t.id ? '打开中…' : '编辑' }}
              </button>
              <button
                type="button"
                class="text-red-600 hover:underline disabled:opacity-40"
                :disabled="!!openingAction"
                @click="remove(t)"
              >
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <AdminTemplateEditor
      :open="editor.open"
      @close="editor.open = false"
      @open-editor="goEditor"
    />
    <ConfirmDialog
      :open="!!deleteConfirm"
      title="删除模板"
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
import { onMounted, onUnmounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../../api/client'
import AdminShell from '../../components/AdminShell.vue'
import AdminTemplateEditor from '../../components/admin/AdminTemplateEditor.vue'
import ConfirmDialog from '../../components/ConfirmDialog.vue'
import { useToast } from '../../composables/useToast.js'
import { normalizeUserErrorMessage } from '../../utils/apiErrorMessage.js'

const OPEN_COOLDOWN_MS = 3000

const router = useRouter()
const { success: toastSuccess, error: toastError } = useToast()
const deleteConfirm = ref(null)

const templates = ref([])
const loading = ref(true)
const openingAction = ref(null)
const cooldownLeft = ref(0)
const error = ref('')
const editor = reactive({ open: false })

let cooldownTimer = null

onMounted(load)

onUnmounted(() => {
  if (cooldownTimer) clearInterval(cooldownTimer)
})

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

async function quickCreate() {
  if (openingAction.value || cooldownLeft.value > 0) return
  openingAction.value = 'create'
  try {
    const draft = await api.quickCreateAdminTemplate()
    goEditor({ templateId: draft.template_id, projectId: draft.project_public_id })
  } catch (e) {
    toastError(simplifyError(e.message))
    startCooldown()
  } finally {
    openingAction.value = null
  }
}

function openImport() {
  if (openingAction.value) return
  editor.open = true
}

async function openVisualEdit(t) {
  if (openingAction.value || cooldownLeft.value > 0) return
  openingAction.value = t.id
  try {
    const draft = await api.startTemplateDraft(t.id)
    goEditor({ templateId: t.id, projectId: draft.project_public_id })
  } catch (e) {
    toastError(simplifyError(e.message))
    startCooldown()
  } finally {
    openingAction.value = null
  }
}

function simplifyError(msg) {
  if (!msg) return '打开失败，请稍后重试'
  const normalized = normalizeUserErrorMessage(msg)
  if (normalized.includes('greenlet_spawn')) return '打开编辑草稿失败，请重启后端服务后再试'
  if (normalized.length > 120) return `${normalized.slice(0, 120)}…`
  return normalized
}

function goEditor({ templateId, projectId }) {
  router.push({
    path: `/editor/${projectId}`,
    query: { adminPreset: templateId },
  })
}

function remove(t) {
  deleteConfirm.value = {
    message: `确定删除模板「${t.title}」？此操作不可撤销。`,
    item: t,
  }
}

async function onDeleteConfirm() {
  const t = deleteConfirm.value?.item
  deleteConfirm.value = null
  if (!t) return
  try {
    await api.deleteAdminTemplate(t.id)
    toastSuccess('模板已删除')
    await load()
  } catch (e) {
    error.value = e.message
    toastError(simplifyError(e.message))
  }
}
</script>
