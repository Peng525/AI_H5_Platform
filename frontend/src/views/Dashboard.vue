<template>
  <div class="min-h-screen bg-background flex flex-col">
    <AppShell />
    <div class="max-w-6xl mx-auto p-6 md:p-10 flex-1 w-full">
      <div class="flex flex-wrap items-center justify-between gap-4 mb-8">
        <div>
          <h1 class="text-2xl font-bold">我的演示项目</h1>
          <p class="text-on-surface-variant text-sm mt-1">管理、编辑与分享您的 H5 演示</p>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <template v-if="selectMode">
            <span class="text-sm text-on-surface-variant mr-1">已选 {{ selectedIds.size }} 项</span>
            <button
              type="button"
              class="px-3 py-2 rounded-lg border border-outline-variant text-sm hover:bg-white transition"
              @click="toggleSelectAll"
            >
              {{ allSelected ? '取消全选' : '全选' }}
            </button>
            <button
              type="button"
              class="px-3 py-2 rounded-lg border border-outline-variant text-sm hover:bg-white transition"
              @click="exitSelectMode"
            >
              取消
            </button>
            <button
              type="button"
              class="px-4 py-2 rounded-lg bg-red-600 text-white text-sm font-medium hover:bg-red-700 transition disabled:opacity-40"
              :disabled="selectedIds.size === 0"
              @click="askBatchRemove"
            >
              删除选中
            </button>
          </template>
          <template v-else>
            <button
              v-if="projects.length > 0"
              type="button"
              class="px-4 py-2.5 rounded-lg border border-outline-variant text-sm font-medium hover:bg-white transition"
              @click="enterSelectMode"
            >
              批量删除
            </button>
            <router-link
              to="/create"
              class="px-5 py-2.5 rounded-lg bg-primary text-on-primary font-medium shadow-card hover:bg-primary-container transition flex items-center gap-1"
            >
              <span class="material-symbols-outlined text-[18px]">add</span>
              新建演示
            </router-link>
          </template>
        </div>
      </div>

      <p v-if="loading" class="text-on-surface-variant">加载中…</p>
      <p v-else-if="error" class="text-red-600">{{ error }}</p>

      <div v-else-if="projects.length === 0" class="text-center py-20 bg-surface-container-low rounded-xl border border-dashed border-outline-variant">
        <span class="material-symbols-outlined text-5xl text-on-surface-variant/40">folder_open</span>
        <p class="text-on-surface-variant mt-4 mb-4">暂无项目，从新建演示开始</p>
        <router-link to="/create" class="text-primary font-medium hover:underline">立即创建 →</router-link>
      </div>

      <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <article
          v-for="p in projects"
          :key="p.id"
          class="bg-white rounded-xl border overflow-hidden shadow-card transition group"
          :class="[
            selectMode && selectedIds.has(p.id)
              ? 'border-primary ring-2 ring-primary/30'
              : 'border-outline-variant hover:shadow-lg',
            selectMode ? 'cursor-pointer' : 'cursor-pointer',
          ]"
          @click="onCardClick(p)"
        >
          <div class="h-24 bg-gradient-to-br from-primary/80 to-primary-container flex items-end p-4 relative">
            <label
              v-if="selectMode"
              class="absolute top-3 right-3 flex items-center justify-center"
              @click.stop
            >
              <input
                type="checkbox"
                class="w-5 h-5 rounded border-white accent-primary cursor-pointer"
                :checked="selectedIds.has(p.id)"
                @change="toggleSelect(p.id)"
              />
            </label>
            <span class="text-white/90 text-xs font-medium">{{ p.slides?.length || 0 }} 页</span>
          </div>
          <div class="p-5">
            <h2 class="font-semibold truncate group-hover:text-primary transition-colors">{{ p.title }}</h2>
            <p class="text-sm text-on-surface-variant mt-1">主题 · {{ p.theme }}</p>
            <div v-if="!selectMode" class="flex gap-3 mt-4 pt-4 border-t border-outline-variant/50" @click.stop>
              <button
                type="button"
                class="text-sm text-primary font-medium hover:underline"
                @click="$router.push(`/editor/${p.id}`)"
              >
                编辑
              </button>
              <button
                type="button"
                class="text-sm text-on-surface-variant hover:text-primary"
                @click="$router.push(`/preview/${p.id}`)"
              >
                预览
              </button>
              <button
                type="button"
                class="text-sm text-red-600 ml-auto hover:underline"
                @click="askRemove(p)"
              >
                删除
              </button>
            </div>
          </div>
        </article>
      </div>
    </div>

    <ConfirmDialog
      :open="deleteDialog.open"
      :title="deleteDialog.title"
      :message="deleteDialog.message"
      confirm-text="确认删除"
      cancel-text="取消"
      danger
      :loading="deleteDialog.loading"
      @confirm="confirmRemove"
      @cancel="closeDeleteDialog"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'
import AppShell from '../components/AppShell.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const projects = ref([])
const loading = ref(true)
const error = ref('')
const router = useRouter()
const selectMode = ref(false)
const selectedIds = ref(new Set())

const allSelected = computed(
  () => projects.value.length > 0 && selectedIds.value.size === projects.value.length
)

const deleteDialog = reactive({
  open: false,
  loading: false,
  mode: 'single',
  id: null,
  ids: [],
  title: '',
  message: '',
})

onMounted(loadProjects)

async function loadProjects() {
  loading.value = true
  error.value = ''
  try {
    projects.value = await api.listProjects()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function enterSelectMode() {
  selectMode.value = true
  selectedIds.value = new Set()
}

function exitSelectMode() {
  selectMode.value = false
  selectedIds.value = new Set()
}

function toggleSelect(id) {
  const next = new Set(selectedIds.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  selectedIds.value = next
}

function toggleSelectAll() {
  if (allSelected.value) {
    selectedIds.value = new Set()
    return
  }
  selectedIds.value = new Set(projects.value.map((p) => p.id))
}

function onCardClick(project) {
  if (selectMode.value) {
    toggleSelect(project.id)
    return
  }
  router.push(`/editor/${project.id}`)
}

function askRemove(project) {
  deleteDialog.mode = 'single'
  deleteDialog.id = project.id
  deleteDialog.ids = []
  deleteDialog.title = '删除演示项目'
  deleteDialog.message = `确定要删除「${project.title}」吗？删除后无法恢复，请谨慎操作。`
  deleteDialog.open = true
}

function askBatchRemove() {
  const ids = [...selectedIds.value]
  if (!ids.length) return
  deleteDialog.mode = 'batch'
  deleteDialog.id = null
  deleteDialog.ids = ids
  deleteDialog.title = '批量删除演示项目'
  deleteDialog.message = `确定要删除选中的 ${ids.length} 个项目吗？删除后无法恢复，请谨慎操作。`
  deleteDialog.open = true
}

function closeDeleteDialog() {
  if (deleteDialog.loading) return
  deleteDialog.open = false
  deleteDialog.id = null
  deleteDialog.ids = []
}

function cleanupLocalProjectData(projectId) {
  const pid = String(projectId)
  localStorage.removeItem(`ai_h5_project_settings_${pid}`)
  const prefix = `ai_h5_canvas_${pid}_`
  const removeKeys = []
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i)
    if (key?.startsWith(prefix)) removeKeys.push(key)
  }
  removeKeys.forEach((k) => localStorage.removeItem(k))
}

async function confirmRemove() {
  deleteDialog.loading = true
  error.value = ''
  try {
    if (deleteDialog.mode === 'batch') {
      const ids = [...deleteDialog.ids]
      const results = await Promise.allSettled(ids.map((id) => api.deleteProject(id)))
      const failed = results.filter((r) => r.status === 'rejected')
      const succeeded = ids.filter((_, i) => results[i].status === 'fulfilled')
      succeeded.forEach((id) => cleanupLocalProjectData(id))
      projects.value = projects.value.filter((p) => !succeeded.includes(p.id))
      if (failed.length) {
        error.value = `${failed.length} 个项目删除失败，请重试`
      }
      exitSelectMode()
    } else if (deleteDialog.id) {
      await api.deleteProject(deleteDialog.id)
      cleanupLocalProjectData(deleteDialog.id)
      projects.value = projects.value.filter((p) => p.id !== deleteDialog.id)
    }
    deleteDialog.open = false
    deleteDialog.id = null
    deleteDialog.ids = []
  } catch (e) {
    error.value = e.message
  } finally {
    deleteDialog.loading = false
  }
}
</script>
