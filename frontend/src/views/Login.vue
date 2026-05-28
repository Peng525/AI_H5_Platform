<template>
  <div class="min-h-screen bg-surface-container-low flex items-center justify-center p-4">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-card p-8 border border-outline-variant">
      <div class="text-center mb-8">
        <div class="w-12 h-12 mx-auto rounded-lg bg-primary flex items-center justify-center text-on-primary font-bold text-sm mb-4">
          AI
        </div>
        <h1 class="text-xl font-bold">欢迎来到 AI 智能 H5 平台</h1>
        <p class="text-sm text-on-surface-variant mt-1">专业、高效的智能创作工具</p>
      </div>

      <form class="space-y-4" @submit.prevent="submit">
        <label class="block text-sm">
          <span class="font-medium">手机号或邮箱</span>
          <div class="relative mt-1">
            <span class="material-symbols-outlined absolute left-3 top-2.5 text-on-surface-variant text-lg">person</span>
            <input
              v-model="account"
              required
              class="w-full pl-10 pr-3 py-2.5 border border-outline-variant rounded-lg"
              placeholder="输入您的账号"
            />
          </div>
        </label>
        <label class="block text-sm">
          <span class="font-medium">密码</span>
          <div class="relative mt-1">
            <span class="material-symbols-outlined absolute left-3 top-2.5 text-on-surface-variant text-lg">lock</span>
            <input
              v-model="password"
              type="password"
              required
              minlength="6"
              class="w-full pl-10 pr-3 py-2.5 border border-outline-variant rounded-lg"
              placeholder="输入密码"
            />
          </div>
        </label>

        <PuzzleCaptcha @verified="captchaOk = $event" />

        <p v-if="error" class="text-red-600 text-sm">{{ error }}</p>

        <div class="flex gap-2">
          <button type="button" class="flex-1 py-2.5 border border-outline-variant rounded-lg text-sm text-on-surface-variant" disabled>
            获取验证码
          </button>
          <button
            type="submit"
            :disabled="loading || !captchaOk"
            class="flex-[2] py-2.5 bg-primary text-on-primary rounded-lg font-medium disabled:opacity-50 flex items-center justify-center gap-1"
          >
            注册 / 登录
            <span class="material-symbols-outlined text-lg">login</span>
          </button>
        </div>
      </form>

      <p class="text-xs text-center text-on-surface-variant mt-6">
        登录即代表同意 <a href="#" class="text-primary">用户协议</a> 与
        <a href="#" class="text-primary">隐私政策</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'
import { useAuth } from '../composables/useAuth'
import PuzzleCaptcha from '../components/PuzzleCaptcha.vue'

const router = useRouter()
const { setSession } = useAuth()
const account = ref('')
const password = ref('')
const captchaOk = ref(false)
const loading = ref(false)
const error = ref('')

async function submit() {
  if (!captchaOk.value) {
    error.value = '请先完成拼图验证'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const body = { account: account.value, password: password.value, captcha_ok: captchaOk.value }
    const data = await api.login(body).catch(() => api.register(body))
    setSession(data)
    router.push('/templates')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>
