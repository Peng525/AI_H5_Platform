<template>
  <div v-if="!isAdmin" class="min-h-screen flex items-center justify-center p-8 bg-surface-container-low">
    <div class="text-center max-w-md">
      <span class="material-symbols-outlined text-5xl text-on-surface-variant mb-3">lock</span>
      <h1 class="text-xl font-bold mb-2">无权访问</h1>
      <p class="text-on-surface-variant text-sm mb-6">系统设置仅管理员可见。</p>
      <router-link to="/login" class="px-4 py-2 bg-primary text-on-primary rounded-lg text-sm">去登录</router-link>
    </div>
  </div>

  <AdminShell v-else title="系统设置">
    <div class="max-w-3xl">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-2xl font-bold mb-1">大模型与环境配置</h1>
          <p class="text-on-surface-variant text-sm">修改后点击底部「保存」按钮写入服务端 .env</p>
        </div>
        <span
          v-if="saveState === 'saved'"
          class="text-xs text-secondary flex items-center gap-1"
        >
          <span class="material-symbols-outlined text-[16px]">check_circle</span>
          已保存
        </span>
        <span v-else-if="saveState === 'saving'" class="text-xs text-on-surface-variant">保存中…</span>
        <span v-else-if="saveState === 'error'" class="text-xs text-red-600">{{ saveError }}</span>
      </div>

      <div
        v-if="loadError"
        class="mb-4 px-4 py-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-700 flex items-start gap-2"
      >
        <span class="material-symbols-outlined text-[18px] shrink-0">error</span>
        <span>加载配置失败：{{ loadError }}</span>
      </div>

      <div v-if="loading" class="text-on-surface-variant">加载中…</div>
      <div v-else class="space-y-6">
        <!-- API 供应商 -->
        <section class="bg-white rounded-xl border border-outline-variant p-6 shadow-card space-y-4">
          <div class="flex items-center justify-between">
            <h2 class="font-semibold">API 供应商</h2>
            <button
              type="button"
              class="px-3 py-2 rounded-lg bg-primary text-on-primary text-sm"
              @click="addProvider"
            >
              + 新建 API
            </button>
          </div>

          <p class="text-on-surface-variant text-xs -mt-1">
            免费档走中转、付费档走官方；同档位配置多个 API 时，出错自动重试下一个。
          </p>

          <p v-if="!form.providers.length" class="text-on-surface-variant text-sm">
            暂无供应商，点击右上角「新建 API」添加。
          </p>

          <div
            v-for="(p, i) in form.providers"
            :key="p.id"
            class="border border-outline-variant rounded-xl p-4 space-y-3 bg-surface-container-low"
          >
            <div class="flex items-center justify-between gap-3">
              <label class="flex-1">
                <span class="text-on-surface-variant text-xs">名称</span>
                <input v-model="p.name" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 bg-white" placeholder="如 DeepSeek 官方" />
              </label>
              <div class="flex items-end gap-4 pt-5">
                <div class="flex items-center gap-2 text-xs whitespace-nowrap">
                  <span class="text-on-surface-variant">档位</span>
                  <label class="flex items-center gap-1 cursor-pointer">
                    <input type="radio" value="free" v-model="p.tier" />
                    <span>免费</span>
                  </label>
                  <label class="flex items-center gap-1 cursor-pointer">
                    <input type="radio" value="pro" v-model="p.tier" />
                    <span>付费</span>
                  </label>
                </div>
                <button
                  type="button"
                  class="text-xs text-red-600 hover:underline whitespace-nowrap"
                  @click="removeProvider(i)"
                >
                  删除
                </button>
              </div>
            </div>

            <div class="grid md:grid-cols-2 gap-3 text-sm">
              <label class="block md:col-span-2">
                <span class="text-on-surface-variant text-xs">Base URL</span>
                <input v-model="p.base_url" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 bg-white" placeholder="https://…/v1" />
              </label>
              <label class="block md:col-span-2">
                <span class="text-on-surface-variant text-xs">API Key</span>
                <input
                  v-model="p.api_key"
                  type="password"
                  class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 bg-white"
                  :placeholder="p.api_key_masked || '未配置'"
                />
              </label>
              <label class="block">
                <span class="text-on-surface-variant text-xs">默认模型</span>
                <input v-model="p.model" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 bg-white" placeholder="如 deepseek-chat" />
              </label>
              <p class="text-xs self-end" :class="p.base_url && p.api_key ? 'text-secondary' : 'text-red-600'">
                {{ p.base_url && p.api_key ? '已配置' : '未配置' }}
              </p>
            </div>
          </div>
        </section>

        <!-- 其他设置 -->
        <section class="bg-white rounded-xl border border-outline-variant p-6 shadow-card space-y-4">
          <h2 class="font-semibold">其他设置</h2>
          <div class="grid md:grid-cols-2 gap-4 text-sm">
            <label class="block">
              <span class="text-on-surface-variant text-xs">请求超时（秒）</span>
              <input v-model.number="form.timeout" type="number" min="30" max="600" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" placeholder="120" />
            </label>
            <label class="block">
              <span class="text-on-surface-variant text-xs">免费用户 AI 配额</span>
              <input v-model.number="form.free_quota_per_user" type="number" min="0" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" placeholder="5" />
            </label>
          </div>
        </section>

        <!-- AI 生图模型 -->
        <section class="bg-white rounded-xl border border-outline-variant p-6 shadow-card space-y-4">
          <h2 class="font-semibold">AI 生图模型</h2>
          <div class="grid md:grid-cols-2 gap-4 text-sm">
            <label class="block">
              <span class="text-on-surface-variant text-xs">免费档生图</span>
              <input v-model="form.image_model_free" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" placeholder="如 gpt-image-2" />
            </label>
            <label class="block">
              <span class="text-on-surface-variant text-xs">升级档生图</span>
              <input v-model="form.image_model_pro" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" placeholder="如 deepseek-v4-pros" />
            </label>
          </div>

          <div class="flex flex-wrap gap-2 pt-2">
            <button
              class="px-4 py-2 rounded-lg bg-primary text-on-primary text-sm disabled:opacity-50"
              :disabled="testing"
              @click="runTest('', 'free')"
            >
              测试免费生图
            </button>
            <button
              class="px-4 py-2 rounded-lg bg-secondary text-white text-sm disabled:opacity-50"
              :disabled="testing"
              @click="runTest('', 'pro')"
            >
              测试升级生图
            </button>
          </div>
          <div
            v-if="testMsg"
            class="px-4 py-3 rounded-lg text-sm flex items-start gap-2"
            :class="testOk ? 'bg-secondary/10 text-secondary border border-secondary/20' : 'bg-red-50 text-red-700 border border-red-200'"
          >
            <span class="material-symbols-outlined text-[18px] shrink-0">{{ testOk ? 'check_circle' : 'error' }}</span>
            <span>{{ testMsg }}</span>
          </div>
        </section>

        <div class="flex justify-end">
          <button
            type="button"
            class="px-6 py-2.5 rounded-lg bg-primary text-on-primary text-sm font-medium disabled:opacity-50"
            :disabled="saveState === 'saving'"
            @click="persistSettings"
          >
            保存
          </button>
        </div>
      </div>
    </div>
  </AdminShell>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../api/client'
import AdminShell from '../components/AdminShell.vue'
import { useAuth } from '../composables/useAuth'

const { user, refreshProfile } = useAuth()
const isAdmin = computed(() => !!user.value?.is_admin)

const form = ref({
  providers: [],
  image_model_free: '',
  image_model_pro: '',
  timeout: 120,
  free_quota_per_user: 5,
})
const loading = ref(true)
const testing = ref(false)
const testMsg = ref('')
const testOk = ref(false)
const saveState = ref('')
const saveError = ref('')
const loadError = ref('')

function providersFromServer(list) {
  return (list || []).map((p) => ({
    id: p.id,
    name: p.name || p.id,
    tier: p.tier || 'free',
    base_url: p.base_url || '',
    api_key: '',
    api_key_masked: p.api_key_masked || '',
    model: p.model || '',
  }))
}

onMounted(async () => {
  await refreshProfile()
  if (!user.value?.is_admin) {
    loading.value = false
    return
  }
  try {
    const s = await api.getLlmSettings()
    form.value = {
      providers: providersFromServer(s.providers),
      image_model_free: s.image_model_free || '',
      image_model_pro: s.image_model_pro || '',
      timeout: s.timeout ?? 120,
      free_quota_per_user: s.free_quota_per_user ?? 5,
    }
  } catch (e) {
    loadError.value = e.message
  } finally {
    loading.value = false
  }
})

function addProvider() {
  const id = `custom-${Date.now()}`
  form.value.providers.push({
    id,
    name: `新 API ${form.value.providers.length + 1}`,
    tier: 'free',
    base_url: '',
    api_key: '',
    api_key_masked: '',
    model: '',
  })
}

function removeProvider(index) {
  form.value.providers.splice(index, 1)
}

function buildPayload() {
  const f = form.value
  return {
    providers: f.providers.map((p) => ({
      id: p.id,
      name: p.name || p.id,
      tier: p.tier || 'free',
      base_url: p.base_url || '',
      api_key: p.api_key || '',
      model: p.model || '',
    })),
    image_model_free: f.image_model_free,
    image_model_pro: f.image_model_pro,
    timeout: f.timeout,
    free_quota_per_user: f.free_quota_per_user,
  }
}

async function persistSettings() {
  if (!isAdmin.value) return
  saveState.value = 'saving'
  saveError.value = ''
  try {
    const updated = await api.updateLlmSettings(buildPayload())
    form.value = {
      providers: providersFromServer(updated.providers),
      image_model_free: updated.image_model_free || '',
      image_model_pro: updated.image_model_pro || '',
      timeout: updated.timeout ?? 120,
      free_quota_per_user: updated.free_quota_per_user ?? 5,
    }
    saveState.value = 'saved'
    setTimeout(() => {
      if (saveState.value === 'saved') saveState.value = ''
    }, 2000)
  } catch (e) {
    saveState.value = 'error'
    saveError.value = e.message
  }
}

async function runTest(channel, tier = 'free') {
  testing.value = true
  testMsg.value = ''
  try {
    const r = await api.testLlm(channel || undefined, tier)
    testOk.value = r.success
    testMsg.value = `${r.message} · 通道 ${r.channel} · 模型 ${r.model || ''}`
  } catch (e) {
    testOk.value = false
    testMsg.value = e.message || '测试失败'
  } finally {
    testing.value = false
  }
}
</script>
