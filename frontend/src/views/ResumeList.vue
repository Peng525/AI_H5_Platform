<template>
  <div class="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-10 w-full">
    <div class="flex flex-wrap items-center justify-between gap-3 mb-6">
      <div class="flex items-center gap-2">
        <span class="material-symbols-outlined text-[22px]">description</span>
        <h1 class="text-xl font-bold">个人简历</h1>
        <span v-if="items.length" class="text-xs text-on-surface-variant">（{{ items.length }}/5）</span>
      </div>
      <router-link
        to="/create/generate?tab=resume"
        class="inline-flex items-center gap-1 px-4 py-2 rounded-lg bg-primary text-on-primary text-sm"
      >
        <span class="material-symbols-outlined text-[16px]">add</span>
        新建简历
      </router-link>
    </div>

    <PageLoading v-if="loading" />
    <p v-else-if="error" class="text-sm text-red-600">{{ error }}</p>
    <div v-else-if="!items.length" class="text-center py-16 border border-dashed rounded-xl">
      <p class="text-on-surface-variant text-sm">暂无简历，最多保存 5 份</p>
      <router-link to="/create/generate?tab=resume" class="text-primary text-sm mt-2 inline-block">去生成 →</router-link>
    </div>
    <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      <ResumeThumbCard
        v-for="item in items"
        :key="item.public_id"
        :item="item"
        @delete="confirmDelete(item)"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import PageLoading from '../components/PageLoading.vue'
import ResumeThumbCard from '../components/resume/ResumeThumbCard.vue'
import { api } from '../api/client.js'
import { useToast } from '../composables/useToast.js'

const items = ref([])
const loading = ref(true)
const error = ref('')
const toast = useToast()

async function loadItems() {
  loading.value = true
  error.value = ''
  try {
    const data = await api.listResumes()
    items.value = data.items || []
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function confirmDelete(item) {
  if (!item?.public_id) return
  const ok = window.confirm(`确定删除「${item.title}」？此操作不可恢复。`)
  if (!ok) return
  try {
    await api.deleteResume(item.public_id)
    items.value = items.value.filter((x) => x.public_id !== item.public_id)
    toast.show('已删除', { type: 'success' })
  } catch (e) {
    toast.show(e.message || '删除失败', { type: 'error' })
  }
}

onMounted(loadItems)
</script>
