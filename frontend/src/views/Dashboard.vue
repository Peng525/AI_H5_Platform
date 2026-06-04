<template>
  <div>
    <div class="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-10 w-full">
      <div class="space-y-4 mb-6">
        <!-- Title -->
        <div class="flex items-center gap-2 min-w-0">
          <span class="material-symbols-outlined text-[22px] text-on-surface-variant">stacked_bar_chart</span>
          <h1 class="text-xl font-bold text-on-surface">项目</h1>
        </div>

        <!-- Actions + batch delete -->
        <div class="flex w-full flex-wrap items-center justify-between gap-3">
          <div class="flex flex-wrap items-center gap-2">
            <router-link to="/create/generate" :class="btnPrimary">
              <span class="material-symbols-outlined text-[14px]">add</span>
              新建演示
            </router-link>
            <div class="relative">
              <button type="button" :class="btnAction" :disabled="importing" @click="triggerImport">
                <span class="material-symbols-outlined text-[14px]">upload</span>
                {{ importing ? '导入中…' : '导入 PPT' }}
              </button>
              <input
                ref="fileInputRef"
                type="file"
                accept=".pptx,application/vnd.openxmlformats-officedocument.presentationml.presentation"
                class="hidden"
                @change="onFileSelected"
              />
            </div>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <template v-if="selectMode">
              <span class="text-sm text-on-surface-variant">已选 {{ selectedIds.size }} 项</span>
              <button type="button" :class="btnDefault" @click="toggleSelectAll">
                {{ allSelected ? '取消全选' : '全选' }}
              </button>
              <button type="button" :class="btnDefault" @click="exitSelectMode">
                取消
              </button>
              <button
                type="button"
                :class="btnDanger"
                :disabled="selectedIds.size === 0"
                @click="askBatchRemove"
              >
                删除选中
              </button>
            </template>
            <button
              v-else-if="projects.length > 0"
              type="button"
              :class="[btnDanger, 'inline-flex items-center gap-1']"
              @click="enterSelectMode"
            >
              <span class="material-symbols-outlined text-[14px]">delete</span>
              批量删除
            </button>
          </div>
        </div>
      </div>

      <p v-if="importError" class="mb-4 text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
        {{ importError }}
      </p>

      <PageLoading v-if="loading" />
      <p v-else-if="error" class="text-sm text-red-600">{{ error }}</p>

      <div v-else-if="projects.length === 0" class="text-center py-20 bg-surface-container-low rounded-xl border border-dashed border-outline-variant">
        <span class="material-symbols-outlined text-5xl text-on-surface-variant/40">folder_open</span>
        <p class="text-sm text-on-surface-variant mt-4 mb-4">暂无项目，点击上方「新建演示」或「导入 PPT」开始</p>
        <router-link to="/create/generate" class="text-sm text-primary font-medium hover:underline">立即创建 →</router-link>
      </div>

      <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <article
          v-for="p in projects"
          :key="p.id"
          class="bg-white rounded-xl border overflow-hidden shadow-card transition group relative"
          :class="[
            selectMode && selectedIds.has(p.public_id)
              ? 'border-primary ring-2 ring-primary/30'
              : 'border-outline-variant hover:shadow-lg',
          ]"
          @click="onCardClick(p)"
        >
          <label
            v-if="selectMode"
            class="absolute top-3 right-3 z-20 flex items-center justify-center"
            @click.stop
          >
            <input
              type="checkbox"
              class="w-5 h-5 rounded border-outline-variant accent-primary cursor-pointer"
              :checked="selectedIds.has(p.public_id)"
              @change="toggleSelect(p.public_id)"
            />
          </label>

          <ProjectCoverThumb :project="p" />

          <div class="p-4">
            <div class="flex items-start justify-between gap-2">
              <h2 class="font-semibold truncate group-hover:text-primary transition-colors flex-1 min-w-0">{{ p.title }}</h2>
              <div v-if="!selectMode" class="relative shrink-0" @click.stop>
                <button
                  type="button"
                  class="w-8 h-8 rounded-lg hover:bg-surface-container-high flex items-center justify-center text-on-surface-variant"
                  :aria-expanded="openMenuId === p.id"
                  @click.stop="toggleMenu(p.id)"
                >
                  <span class="material-symbols-outlined text-[20px]">more_horiz</span>
                </button>
                <div
                  v-if="openMenuId === p.id"
                  class="absolute right-0 top-full mt-1 w-32 bg-white border border-outline-variant rounded-lg shadow-lg py-1 z-30"
                >
                  <button type="button" class="w-full text-left px-3 py-2 text-sm hover:bg-surface-container-low" @click="goEdit(p.public_id)">
                    编辑
                  </button>
                  <button type="button" class="w-full text-left px-3 py-2 text-sm hover:bg-surface-container-low" @click="goPreview(p.public_id)">
                    预览
                  </button>
                  <button type="button" class="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50" @click="askRemove(p)">
                    删除
                  </button>
                </div>
              </div>
            </div>
            <p v-if="relativeTime(p)" class="text-sm text-on-surface-variant mt-1">{{ relativeTime(p) }}</p>
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
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import PageLoading from '../components/PageLoading.vue'
import ProjectCoverThumb from '../components/ProjectCoverThumb.vue'
import { usePptImport } from '../composables/usePptImport'
import { formatRelativeTime } from '../utils/formatRelativeTime'

const projects = ref([])
const loading = ref(true)
const error = ref('')
const router = useRouter()
const selectMode = ref(false)
const selectedIds = ref(new Set())
const openMenuId = ref(null)

const btnDefault =
  'px-3 py-1.5 rounded-lg border border-outline-variant bg-white text-on-surface text-sm font-medium hover:bg-surface-container-low transition whitespace-nowrap'
const btnPrimary =
  'inline-flex items-center gap-1 px-4 py-2 rounded-lg bg-primary text-on-primary text-sm font-medium hover:bg-primary/90 transition whitespace-nowrap'
const btnAction =
  'inline-flex items-center gap-1 px-4 py-2 rounded-lg border border-outline-variant bg-white text-on-surface text-sm font-medium hover:bg-surface-container-low transition whitespace-nowrap disabled:opacity-50'
const btnDanger =
  'px-3 py-1.5 rounded-lg bg-red-600 text-white text-sm font-medium hover:bg-red-700 transition whitespace-nowrap disabled:opacity-40'

const {
  importing,
  importError,
  fileInputRef,
  triggerImport,
  onFileSelected,
} = usePptImport()

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

function relativeTime(project) {
  return formatRelativeTime(project.updated_at)
}

function toggleMenu(id) {
  openMenuId.value = openMenuId.value === id ? null : id
}

function closeMenus() {
  openMenuId.value = null
}

function goEdit(id) {
  closeMenus()
  router.push(`/editor/${id}`)
}

function goPreview(id) {
  closeMenus()
  router.push(`/preview/${id}`)
}

function onDocumentClick() {
  closeMenus()
}

onMounted(async () => {
  document.addEventListener('click', onDocumentClick)
  await loadProjects()
})

onUnmounted(() => document.removeEventListener('click', onDocumentClick))

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
  closeMenus()
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
  selectedIds.value = new Set(projects.value.map((p) => p.public_id))
}

function onCardClick(project) {
  if (selectMode.value) {
    toggleSelect(project.public_id)
    return
  }
  router.push(`/editor/${project.public_id}`)
}

function askRemove(project) {
  closeMenus()
  deleteDialog.mode = 'single'
  deleteDialog.id = project.public_id
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
      projects.value = projects.value.filter((p) => !succeeded.includes(p.public_id))
      if (failed.length) {
        error.value = `${failed.length} 个项目删除失败，请重试`
      }
      exitSelectMode()
    } else if (deleteDialog.id) {
      await api.deleteProject(deleteDialog.id)
      cleanupLocalProjectData(deleteDialog.id)
      projects.value = projects.value.filter((p) => p.public_id !== deleteDialog.id)
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
