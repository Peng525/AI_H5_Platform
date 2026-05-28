<template>
  <div class="min-h-screen bg-background flex flex-col">
    <AppShell page-title="我的项目" />
    <div class="max-w-6xl mx-auto p-6 md:p-10 flex-1 w-full">
      <div class="flex flex-wrap items-center justify-between gap-4 mb-8">
        <div>
          <h1 class="text-2xl font-bold">我的演示项目</h1>
          <p class="text-on-surface-variant text-sm mt-1">管理、编辑与分享您的 H5 演示</p>
        </div>
        <router-link
          to="/create"
          class="px-5 py-2.5 rounded-lg bg-primary text-on-primary font-medium shadow-card hover:bg-primary-container transition flex items-center gap-1"
        >
          <span class="material-symbols-outlined text-[18px]">auto_awesome</span>
          AI 创建演示
        </router-link>
      </div>

      <p v-if="loading" class="text-on-surface-variant">加载中…</p>
      <p v-else-if="error" class="text-red-600">{{ error }}</p>

      <div v-else-if="projects.length === 0" class="text-center py-20 bg-surface-container-low rounded-xl border border-dashed border-outline-variant">
        <span class="material-symbols-outlined text-5xl text-on-surface-variant/40">folder_open</span>
        <p class="text-on-surface-variant mt-4 mb-4">暂无项目，从 AI 创建开始</p>
        <router-link to="/create" class="text-primary font-medium hover:underline">立即创建 →</router-link>
      </div>

      <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <article
          v-for="p in projects"
          :key="p.id"
          class="bg-white rounded-xl border border-outline-variant overflow-hidden shadow-card hover:shadow-lg transition group cursor-pointer"
          @click="$router.push(`/editor/${p.id}`)"
        >
          <div class="h-24 bg-gradient-to-br from-primary/80 to-primary-container flex items-end p-4">
            <span class="text-white/90 text-xs font-medium">{{ p.slides?.length || 0 }} 页</span>
          </div>
          <div class="p-5">
            <h2 class="font-semibold truncate group-hover:text-primary transition-colors">{{ p.title }}</h2>
            <p class="text-sm text-on-surface-variant mt-1">主题 · {{ p.theme }}</p>
            <div class="flex gap-3 mt-4 pt-4 border-t border-outline-variant/50" @click.stop>
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
      title="删除演示项目"
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
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api/client'
import AppShell from '../components/AppShell.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const projects = ref([])
const loading = ref(true)
const error = ref('')

const deleteDialog = reactive({
  open: false,
  loading: false,
  id: null,
  title: '',
  message: '',
})

onMounted(async () => {
  try {
    projects.value = await api.listProjects()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

function askRemove(project) {
  deleteDialog.id = project.id
  deleteDialog.title = project.title
  deleteDialog.message = `确定要删除「${project.title}」吗？删除后无法恢复，请谨慎操作。`
  deleteDialog.open = true
}

function closeDeleteDialog() {
  if (deleteDialog.loading) return
  deleteDialog.open = false
  deleteDialog.id = null
}

async function confirmRemove() {
  if (!deleteDialog.id) return
  deleteDialog.loading = true
  try {
    await api.deleteProject(deleteDialog.id)
    projects.value = projects.value.filter((p) => p.id !== deleteDialog.id)
    deleteDialog.open = false
    deleteDialog.id = null
  } catch (e) {
    error.value = e.message
  } finally {
    deleteDialog.loading = false
  }
}
</script>
