<template>
  <div class="max-w-6xl mx-auto p-6 md:p-10">
    <div class="flex flex-wrap items-center justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl font-bold">我的演示项目</h1>
        <p class="text-on-surface-variant text-sm mt-1">管理、编辑与分享您的 H5 演示</p>
      </div>
      <router-link
        to="/create"
        class="px-5 py-2.5 rounded-lg bg-primary text-on-primary font-medium shadow-card hover:bg-primary-container transition"
      >
        + AI 创建演示
      </router-link>
    </div>

    <p v-if="loading" class="text-on-surface-variant">加载中…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>

    <div v-else-if="projects.length === 0" class="text-center py-20 bg-surface-container-low rounded-xl">
      <p class="text-on-surface-variant mb-4">暂无项目，从 AI 创建开始</p>
      <router-link to="/create" class="text-primary font-medium">立即创建 →</router-link>
    </div>

    <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <article
        v-for="p in projects"
        :key="p.id"
        class="bg-white rounded-lg border border-outline-variant p-5 shadow-card hover:shadow-lg transition cursor-pointer"
        @click="$router.push(`/editor/${p.id}`)"
      >
        <h2 class="font-semibold truncate">{{ p.title }}</h2>
        <p class="text-sm text-on-surface-variant mt-1">{{ p.slides?.length || 0 }} 页 · 主题 {{ p.theme }}</p>
        <div class="flex gap-2 mt-4" @click.stop>
          <button
            class="text-sm text-primary"
            @click="$router.push(`/preview/${p.id}`)"
          >
            预览
          </button>
          <button class="text-sm text-red-600 ml-auto" @click="remove(p.id)">删除</button>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api/client'

const projects = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    projects.value = await api.listProjects()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

async function remove(id) {
  if (!confirm('确定删除该项目？')) return
  try {
    await api.deleteProject(id)
    projects.value = projects.value.filter((p) => p.id !== id)
  } catch (e) {
    alert(e.message)
  }
}
</script>
