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
          <p class="text-on-surface-variant text-sm">修改后自动保存到服务端 .env</p>
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

      <div v-if="loading" class="text-on-surface-variant">加载中…</div>
      <div v-else class="space-y-6">
        <section class="bg-white rounded-xl border border-outline-variant p-6 shadow-card space-y-4">
          <h2 class="font-semibold">大模型通道</h2>
          <div class="grid md:grid-cols-2 gap-4 text-sm">
            <label class="block">
              <span class="text-on-surface-variant text-xs">默认通道</span>
              <select v-model="form.default_channel" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2">
                <option value="auto">auto（自动选择）</option>
                <option value="relay">relay（中转）</option>
                <option value="official">official（官方）</option>
              </select>
            </label>
            <label class="block">
              <span class="text-on-surface-variant text-xs">auto 顺序（逗号分隔）</span>
              <input v-model="form.auto_order" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" />
            </label>
            <label class="block">
              <span class="text-on-surface-variant text-xs">请求超时（秒）</span>
              <input v-model.number="form.timeout" type="number" min="30" max="600" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" />
            </label>
            <label class="block">
              <span class="text-on-surface-variant text-xs">免费用户 AI 配额</span>
              <input v-model.number="form.free_quota_per_user" type="number" min="0" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" />
            </label>
          </div>
        </section>

        <section class="bg-white rounded-xl border border-outline-variant p-6 shadow-card space-y-4">
          <h2 class="font-semibold">中转 API</h2>
          <div class="grid md:grid-cols-2 gap-4 text-sm">
            <label class="block md:col-span-2">
              <span class="text-on-surface-variant text-xs">Base URL</span>
              <input v-model="form.relay_base_url" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" placeholder="https://…/v1" />
            </label>
            <label class="block md:col-span-2">
              <span class="text-on-surface-variant text-xs">API Key</span>
              <input
                v-model="form.relay_api_key"
                type="password"
                class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2"
                :placeholder="form.relay_api_key_masked || '未配置'"
                @focus="onKeyFocus('relay')"
              />
            </label>
            <label class="block">
              <span class="text-on-surface-variant text-xs">默认模型</span>
              <input v-model="form.relay_model" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" />
            </label>
            <p class="text-xs self-end" :class="form.relay_configured ? 'text-secondary' : 'text-red-600'">
              {{ form.relay_configured ? '已配置' : '未配置' }}
            </p>
          </div>
        </section>

        <section class="bg-white rounded-xl border border-outline-variant p-6 shadow-card space-y-4">
          <h2 class="font-semibold">官方 API</h2>
          <div class="grid md:grid-cols-2 gap-4 text-sm">
            <label class="block md:col-span-2">
              <span class="text-on-surface-variant text-xs">Base URL</span>
              <input v-model="form.official_base_url" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" />
            </label>
            <label class="block md:col-span-2">
              <span class="text-on-surface-variant text-xs">API Key</span>
              <input
                v-model="form.official_api_key"
                type="password"
                class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2"
                :placeholder="form.official_api_key_masked || '未配置'"
                @focus="onKeyFocus('official')"
              />
            </label>
            <label class="block">
              <span class="text-on-surface-variant text-xs">默认模型</span>
              <input v-model="form.official_model" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" />
            </label>
            <p class="text-xs self-end" :class="form.official_configured ? 'text-secondary' : 'text-red-600'">
              {{ form.official_configured ? '已配置' : '未配置' }}
            </p>
          </div>
        </section>

        <section class="bg-white rounded-xl border border-outline-variant p-6 shadow-card space-y-4">
          <h2 class="font-semibold">AI 生图模型</h2>
          <div class="grid md:grid-cols-2 gap-4 text-sm">
            <label class="block">
              <span class="text-on-surface-variant text-xs">免费档生图</span>
              <input v-model="form.image_model_free" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" />
            </label>
            <label class="block">
              <span class="text-on-surface-variant text-xs">升级档生图</span>
              <input v-model="form.image_model_pro" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" />
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
            <button class="px-4 py-2 rounded-lg border text-sm" :disabled="testing" @click="runTest('relay', 'free')">
              中转 + 免费档
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

        <section class="bg-white rounded-xl border border-outline-variant p-6 shadow-card">
          <h2 class="font-semibold mb-4">提示词模板</h2>
          <ul class="space-y-2 text-sm">
            <li v-for="t in templates" :key="t.id" class="flex justify-between border-b border-outline-variant py-2 gap-4">
              <span class="font-medium shrink-0">{{ t.name }}</span>
              <span class="text-on-surface-variant text-right">{{ t.description }}</span>
            </li>
          </ul>
        </section>
      </div>
    </div>
  </AdminShell>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { api } from '../api/client'
import AdminShell from '../components/AdminShell.vue'
import { useAuth } from '../composables/useAuth'

const { user, refreshProfile } = useAuth()
const isAdmin = computed(() => !!user.value?.is_admin)

const form = ref({})
const templates = ref([])
const loading = ref(true)
const testing = ref(false)
const testMsg = ref('')
const testOk = ref(false)
const saveState = ref('')
const saveError = ref('')
const keyDirty = ref({ relay: false, official: false })
let saveTimer = null
let skipSave = false

onMounted(async () => {
  await refreshProfile()
  if (!user.value?.is_admin) {
    loading.value = false
    return
  }
  try {
    const [s, t] = await Promise.all([api.getLlmSettings(), api.getPromptTemplates()])
    form.value = {
      ...s,
      relay_api_key: s.relay_api_key_masked || '',
      official_api_key: s.official_api_key_masked || '',
    }
    templates.value = t.items || []
  } catch (e) {
    saveError.value = e.message
    saveState.value = 'error'
  } finally {
    loading.value = false
  }
})

function onKeyFocus(which) {
  if (!keyDirty.value[which]) {
    keyDirty.value[which] = true
    if (which === 'relay') form.value.relay_api_key = ''
    else form.value.official_api_key = ''
  }
}

function buildPayload() {
  const f = form.value
  const body = {
    default_channel: f.default_channel,
    auto_order: f.auto_order,
    timeout: f.timeout,
    free_quota_per_user: f.free_quota_per_user,
    relay_base_url: f.relay_base_url,
    relay_model: f.relay_model,
    official_base_url: f.official_base_url,
    official_model: f.official_model,
    model_free: f.image_model_free,
    model_pro: f.image_model_pro,
    image_model_free: f.image_model_free,
    image_model_pro: f.image_model_pro,
  }
  if (keyDirty.value.relay && f.relay_api_key) body.relay_api_key = f.relay_api_key
  if (keyDirty.value.official && f.official_api_key) body.official_api_key = f.official_api_key
  return body
}

async function persistSettings() {
  if (!isAdmin.value || skipSave) return
  saveState.value = 'saving'
  saveError.value = ''
  try {
    const updated = await api.updateLlmSettings(buildPayload())
    skipSave = true
    form.value = {
      ...updated,
      relay_api_key: keyDirty.value.relay ? form.value.relay_api_key : updated.relay_api_key_masked || '',
      official_api_key: keyDirty.value.official ? form.value.official_api_key : updated.official_api_key_masked || '',
    }
    keyDirty.value = { relay: false, official: false }
    skipSave = false
    saveState.value = 'saved'
    setTimeout(() => {
      if (saveState.value === 'saved') saveState.value = ''
    }, 2000)
  } catch (e) {
    saveState.value = 'error'
    saveError.value = e.message
  }
}

watch(
  form,
  () => {
    if (loading.value || skipSave) return
    clearTimeout(saveTimer)
    saveTimer = setTimeout(persistSettings, 800)
  },
  { deep: true }
)

async function runTest(channel, tier = 'free') {
  testing.value = true
  testMsg.value = ''
  try {
    const r = await api.testLlm(channel || undefined, tier)
    testOk.value = r.success
    testMsg.value = `${r.message} · 通道 ${r.channel} · 模型 ${r.model || ''}`
  } catch (e) {
    testOk.value = false
    testMsg.value = e.message
  } finally {
    testing.value = false
  }
}
</script>
