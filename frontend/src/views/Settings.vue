<template>
  <div class="max-w-2xl mx-auto p-6 md:p-10">
    <h1 class="text-2xl font-bold mb-2">系统设置</h1>
    <p class="text-on-surface-variant text-sm mb-8">大模型通道配置由服务端环境变量管理（.env）</p>

    <div v-if="loading" class="text-on-surface-variant">加载中…</div>
    <div v-else class="space-y-6">
      <section class="bg-white rounded-xl border border-outline-variant p-6 shadow-card">
        <h2 class="font-semibold mb-4">大模型状态</h2>
        <dl class="grid grid-cols-2 gap-3 text-sm">
          <dt class="text-on-surface-variant">默认通道</dt>
          <dd class="font-medium">{{ settings.default_channel }}（auto 将按顺序自动选择）</dd>
          <dt class="text-on-surface-variant">auto 顺序</dt>
          <dd>{{ settings.auto_order }}</dd>
          <dt class="text-on-surface-variant">中转 API</dt>
          <dd :class="settings.relay_configured ? 'text-secondary' : 'text-red-600'">
            {{ settings.relay_configured ? '已配置' : '未配置' }}
          </dd>
          <dt class="text-on-surface-variant">官方 API</dt>
          <dd :class="settings.official_configured ? 'text-secondary' : 'text-red-600'">
            {{ settings.official_configured ? '已配置' : '未配置' }}
          </dd>
          <dt class="text-on-surface-variant">中转模型</dt>
          <dd>{{ settings.relay_model }}</dd>
          <dt class="text-on-surface-variant">官方模型</dt>
          <dd>{{ settings.official_model }}</dd>
        </dl>

        <div class="mt-6 flex flex-wrap gap-2">
          <button
            class="px-4 py-2 rounded-lg bg-primary text-on-primary text-sm disabled:opacity-50"
            :disabled="testing"
            @click="runTest('')"
          >
            测试 auto
          </button>
          <button class="px-4 py-2 rounded-lg border text-sm" :disabled="testing" @click="runTest('relay')">
            测试中转
          </button>
          <button class="px-4 py-2 rounded-lg border text-sm" :disabled="testing" @click="runTest('official')">
            测试官方
          </button>
        </div>
        <p v-if="testMsg" class="mt-3 text-sm" :class="testOk ? 'text-secondary' : 'text-red-600'">{{ testMsg }}</p>
      </section>

      <section class="bg-white rounded-xl border border-outline-variant p-6 shadow-card">
        <h2 class="font-semibold mb-4">提示词模板</h2>
        <ul class="space-y-2 text-sm">
          <li v-for="t in templates" :key="t.id" class="flex justify-between border-b border-outline-variant py-2">
            <span class="font-medium">{{ t.name }}</span>
            <span class="text-on-surface-variant">{{ t.description }}</span>
          </li>
        </ul>
      </section>

      <section class="text-sm text-on-surface-variant bg-surface-container-low rounded-lg p-4">
        <p>请在项目根目录复制 <code class="bg-white px-1 rounded">.env.example</code> 为 <code class="bg-white px-1 rounded">.env</code> 并填写 API Key。</p>
        <p class="mt-2">推荐设置 <code>LLM_DEFAULT_CHANNEL=auto</code>。</p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api/client'

const settings = ref({})
const templates = ref([])
const loading = ref(true)
const testing = ref(false)
const testMsg = ref('')
const testOk = ref(false)

onMounted(async () => {
  try {
    settings.value = await api.getLlmSettings()
    const t = await api.getTemplates()
    templates.value = t.items || []
  } finally {
    loading.value = false
  }
})

async function runTest(channel) {
  testing.value = true
  testMsg.value = ''
  try {
    const r = await api.testLlm(channel || undefined)
    testOk.value = r.success
    testMsg.value = `${r.message}（实际通道：${r.channel}）`
  } catch (e) {
    testOk.value = false
    testMsg.value = e.message
  } finally {
    testing.value = false
  }
}
</script>
