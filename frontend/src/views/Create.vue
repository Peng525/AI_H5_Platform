<template>
  <div class="min-h-screen bg-background flex flex-col">
    <EditorTopBar />
    <div class="max-w-xl mx-auto p-6 md:p-10 flex-1 w-full">
      <h1 class="text-2xl font-bold mb-2">新建演示</h1>
      <p class="text-on-surface-variant text-sm mb-8">创建空白项目，在编辑器中使用 AI 生图并手动排版</p>

      <form class="bg-white rounded-xl border border-outline-variant p-6 shadow-card space-y-5" @submit.prevent="submit">
        <label class="block">
          <span class="text-sm font-medium">演示标题 *</span>
          <input
            v-model="title"
            required
            class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/30"
            placeholder="例如：2025 产品路演"
          />
        </label>

        <p v-if="error" class="text-red-600 text-sm">{{ error }}</p>

        <button
          type="submit"
          class="w-full py-2.5 rounded-lg bg-primary text-on-primary font-medium disabled:opacity-50"
          :disabled="loading"
        >
          {{ loading ? '创建中…' : '创建并进入编辑器' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'
import EditorTopBar from '../components/EditorTopBar.vue'

const router = useRouter()
const title = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  if (!title.value.trim()) {
    error.value = '请填写演示标题'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const project = await api.createProject({ title: title.value.trim(), theme: 'default' })
    router.push(`/editor/${project.id}`)
  } catch (e) {
    error.value = e.message
    loading.value = false
  }
}
</script>
