<template>
  <div class="min-h-screen bg-background flex flex-col">
    <EditorTopBar project-title="AI 创建演示" />
  <div class="max-w-2xl mx-auto p-6 md:p-10 flex-1 w-full">
    <h1 class="text-2xl font-bold mb-2">AI 创建演示</h1>
    <p class="text-on-surface-variant text-sm mb-8">使用「全量生成」模板，一次性生成整套 H5 结构</p>

    <form class="space-y-5 bg-white rounded-xl border border-outline-variant p-6 shadow-card" @submit.prevent="submit">
      <label class="block">
        <span class="text-sm font-medium">演示主题 *</span>
        <input
          v-model="form.topic"
          required
          class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/30"
          placeholder="例如：2025 产品路演"
        />
      </label>
      <label class="block">
        <span class="text-sm font-medium">目标受众</span>
        <input v-model="form.audience" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" />
      </label>
      <label class="block">
        <span class="text-sm font-medium">页数</span>
        <input v-model.number="form.page_count" type="number" min="1" max="30" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" />
      </label>
      <label class="block">
        <span class="text-sm font-medium">风格</span>
        <input v-model="form.style" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" />
      </label>
      <label class="block">
        <span class="text-sm font-medium">会员档位 / 模型</span>
        <select v-model="form.tier" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2">
          <option value="free">免费档 · Gemini 3.1 Flash（含免费配图）</option>
          <option value="pro">升级档 · Gemini 3 Pro</option>
        </select>
      </label>
      <label class="block">
        <span class="text-sm font-medium">大模型通道</span>
        <select v-model="form.channel" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2">
          <option value="">auto（自动选择）</option>
          <option value="relay">中转 API</option>
          <option value="official">官方 API</option>
        </select>
      </label>

      <p v-if="error" class="text-red-600 text-sm">{{ error }}</p>

      <button
        type="submit"
        :disabled="loading"
        class="w-full py-3 rounded-lg bg-primary text-on-primary font-medium disabled:opacity-50"
      >
        {{ loading ? 'AI 生成中，请稍候…' : '开始生成' }}
      </button>
    </form>
  </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'
import { useAuth } from '../composables/useAuth'
import EditorTopBar from '../components/EditorTopBar.vue'

const router = useRouter()
const { user } = useAuth()
const loading = ref(false)
const error = ref('')
const form = reactive({
  topic: '',
  audience: '通用受众',
  page_count: 5,
  style: '专业简约',
  channel: '',
  tier: 'free',
})

async function submit() {
  loading.value = true
  error.value = ''
  try {
    const uid = user.value?.user_id
    const project = await api.createProject({ title: form.topic, theme: 'default' }, uid)
    const body = {
      topic: form.topic,
      audience: form.audience,
      page_count: form.page_count,
      style: form.style,
      tier: form.tier,
    }
    if (form.channel) body.channel = form.channel
    await api.generateFull(project.id, body, uid)
    router.push(`/editor/${project.id}`)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>
