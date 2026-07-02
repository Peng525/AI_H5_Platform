<template>
  <div class="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-10 w-full">
    <div class="flex flex-wrap items-center justify-between gap-3 mb-6">
      <div class="flex items-center gap-2">
        <span class="material-symbols-outlined text-[22px]">description</span>
        <h1 class="text-xl font-bold">个人简历</h1>
      </div>
      <router-link to="/create/generate" class="inline-flex items-center gap-1 px-4 py-2 rounded-lg bg-primary text-on-primary text-sm">
        <span class="material-symbols-outlined text-[16px]">add</span>
        新建简历
      </router-link>
    </div>

    <PageLoading v-if="loading" />
    <p v-else-if="error" class="text-sm text-red-600">{{ error }}</p>
    <div v-else-if="!items.length" class="text-center py-16 border border-dashed rounded-xl">
      <p class="text-on-surface-variant text-sm">暂无简历，最多保存 5 份</p>
      <router-link to="/create/generate" class="text-primary text-sm mt-2 inline-block">去生成 →</router-link>
    </div>
    <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      <ResumeThumbCard v-for="item in items" :key="item.public_id" :item="item" />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import PageLoading from '../components/PageLoading.vue'
import ResumeThumbCard from '../components/resume/ResumeThumbCard.vue'
import { api } from '../api/client.js'

const items = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const data = await api.listResumes()
    items.value = data.items || []
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
})
</script>
