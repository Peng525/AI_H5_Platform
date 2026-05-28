<template>
  <div class="min-h-screen bg-background flex flex-col">
    <EditorTopBar />
    <div class="max-w-2xl mx-auto p-6 md:p-10 flex-1 w-full">
      <h1 class="text-2xl font-bold mb-2">AI 创建演示</h1>
      <p class="text-on-surface-variant text-sm mb-6">使用「全量生成」模板，一次性生成整套 H5 结构</p>

      <div class="flex items-center gap-2 mb-8">
        <div
          v-for="(s, i) in steps"
          :key="s.id"
          class="flex items-center gap-2 flex-1"
        >
          <div
            class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium shrink-0"
            :class="step >= i ? 'bg-primary text-on-primary' : 'bg-surface-container-high text-on-surface-variant'"
          >
            {{ i + 1 }}
          </div>
          <span class="text-xs hidden sm:block" :class="step >= i ? 'text-primary font-medium' : 'text-on-surface-variant'">{{ s.label }}</span>
          <div v-if="i < steps.length - 1" class="flex-1 h-px bg-outline-variant mx-1" />
        </div>
      </div>

      <div v-if="loading" class="bg-white rounded-xl border border-outline-variant p-12 text-center shadow-card">
        <div class="w-12 h-12 mx-auto border-4 border-primary/30 border-t-primary rounded-full animate-spin mb-4" />
        <p class="font-medium">AI 正在生成演示结构…</p>
        <p class="text-sm text-on-surface-variant mt-2">通常需要 10–30 秒，请稍候</p>
      </div>

      <form v-else class="bg-white rounded-xl border border-outline-variant p-6 shadow-card space-y-5" @submit.prevent="onNext">
        <template v-if="step === 0">
          <label class="block">
            <span class="text-sm font-medium">演示主题 *</span>
            <input
              v-model="form.topic"
              required
              class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/30"
              placeholder="例如：2025 产品路演"
            />
          </label>
        </template>

        <template v-else-if="step === 1">
          <label class="block">
            <span class="text-sm font-medium">目标受众</span>
            <input v-model="form.audience" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" placeholder="例如：投资人、客户" />
          </label>
          <label class="block">
            <span class="text-sm font-medium">页数</span>
            <input v-model.number="form.page_count" type="number" min="1" max="30" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" />
          </label>
        </template>

        <template v-else-if="step === 2">
          <label class="block">
            <span class="text-sm font-medium">风格</span>
            <input v-model="form.style" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" placeholder="专业简约、科技风…" />
          </label>
          <label class="block">
            <span class="text-sm font-medium">会员档位 / 模型</span>
            <select v-model="form.tier" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2">
              <option value="free">免费档 · Gemini 3.1 Flash</option>
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
        </template>

        <template v-else>
          <div class="bg-surface-container-low rounded-lg p-4 text-sm space-y-2">
            <p><span class="text-on-surface-variant">主题：</span>{{ form.topic }}</p>
            <p><span class="text-on-surface-variant">受众：</span>{{ form.audience }}</p>
            <p><span class="text-on-surface-variant">页数：</span>{{ form.page_count }} 页</p>
            <p><span class="text-on-surface-variant">风格：</span>{{ form.style }}</p>
            <p><span class="text-on-surface-variant">模型：</span>{{ form.tier === 'pro' ? 'Gemini 3 Pro' : 'Gemini 3.1 Flash' }}</p>
          </div>
        </template>

        <p v-if="error" class="text-red-600 text-sm">{{ error }}</p>

        <div class="flex gap-3 pt-2">
          <button
            v-if="step > 0"
            type="button"
            class="px-5 py-2.5 border border-outline-variant rounded-lg text-sm"
            @click="step--"
          >
            上一步
          </button>
          <button
            type="submit"
            class="flex-1 py-2.5 rounded-lg bg-primary text-on-primary font-medium"
          >
            {{ step < steps.length - 1 ? '下一步' : '开始生成' }}
          </button>
        </div>
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
const step = ref(0)
const steps = [
  { id: 'topic', label: '主题' },
  { id: 'detail', label: '详情' },
  { id: 'model', label: '模型' },
  { id: 'confirm', label: '确认' },
]
const form = reactive({
  topic: '',
  audience: '通用受众',
  page_count: 5,
  style: '专业简约',
  channel: '',
  tier: 'free',
})

function onNext() {
  if (step.value < steps.length - 1) {
    if (step.value === 0 && !form.topic.trim()) {
      error.value = '请填写演示主题'
      return
    }
    error.value = ''
    step.value++
    return
  }
  submit()
}

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
    loading.value = false
  }
}
</script>
