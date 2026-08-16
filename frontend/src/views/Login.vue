<template>
  <div class="min-h-screen bg-surface-container-low flex items-center justify-center p-4">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-card p-8 border border-outline-variant">
      <div class="text-center mb-8">
        <div class="w-12 h-12 mx-auto rounded-lg bg-primary flex items-center justify-center text-on-primary font-bold text-sm mb-4">
          AI
        </div>
        <h1 class="text-xl font-bold">欢迎来到 AI 智能 H5 平台</h1>
        <p class="text-sm text-on-surface-variant mt-1">请先登录后再使用编辑器等功能</p>
        <p class="text-xs text-on-surface-variant mt-2">首次使用将自动创建账号，无需单独注册</p>
      </div>

      <div v-if="autoLogging" class="text-center py-8 text-on-surface-variant text-sm">
        <span class="material-symbols-outlined animate-spin text-primary text-2xl mb-2">progress_activity</span>
        <p>正在恢复登录状态…</p>
      </div>

      <form v-else class="space-y-4" @submit.prevent="submit">
        <label class="block text-sm">
          <span class="font-medium">邮箱</span>
          <div class="relative mt-1">
            <span class="material-symbols-outlined absolute left-3 top-2.5 text-on-surface-variant text-lg">mail</span>
            <input
              v-model="account"
              type="email"
              required
              class="w-full pl-10 pr-3 py-2.5 border border-outline-variant rounded-lg"
              placeholder="name@example.com"
            />
          </div>
          <p class="text-xs text-on-surface-variant mt-1">请使用邮箱注册，暂不支持手机号</p>
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

        <label class="flex items-start gap-2 text-sm cursor-pointer select-none">
          <input v-model="rememberMe" type="checkbox" class="mt-0.5 rounded border-outline-variant text-primary focus:ring-primary" />
          <span>
            记住邮箱并保持登录
            <span class="block text-xs text-on-surface-variant font-normal mt-0.5">仅保存邮箱与登录状态，不保存密码</span>
          </span>
        </label>

        <SlideCaptcha @ticket="onCaptchaTicket" @verified="captchaOk = $event" />

        <p v-if="error" class="text-red-600 text-sm">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading || !captchaOk"
          class="w-full py-2.5 bg-primary text-on-primary rounded-lg font-medium disabled:opacity-50 flex items-center justify-center gap-1"
        >
          {{ loading ? '登录中…' : '注册 / 登录' }}
          <span v-if="!loading" class="material-symbols-outlined text-lg">login</span>
        </button>
      </form>

      <p class="text-xs text-center text-on-surface-variant mt-6">
        登录即代表同意 <a href="#" class="text-primary">用户协议</a> 与
        <a href="#" class="text-primary">隐私政策</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api/client'
import { useAuth } from '../composables/useAuth'
import SlideCaptcha from '../components/SlideCaptcha.vue'

const route = useRoute()
const router = useRouter()
const { setSession, saveRememberCredentials, clearRememberCredentials, isLoggedIn, getRememberedCredentials, refreshProfile } = useAuth()
const account = ref('')
const password = ref('')
const rememberMe = ref(false)
const captchaOk = ref(false)
const captchaTicket = ref({ ticket: '', randstr: '' })
const loading = ref(false)
const autoLogging = ref(false)
const error = ref('')

onMounted(async () => {
  if (route.query.from === 'logout') {
    const saved = getRememberedCredentials()
    if (saved) {
      account.value = saved.account
      rememberMe.value = true
    }
    return
  }

  if (isLoggedIn.value) {
    goAfterLogin(null)
    return
  }

  const saved = getRememberedCredentials()
  if (saved) {
    account.value = saved.account
    rememberMe.value = true
  }

  const token = localStorage.getItem('ai_h5_token')
  if (rememberMe.value && token) {
    autoLogging.value = true
    const me = await refreshProfile()
    autoLogging.value = false
    if (me) {
      goAfterLogin(useAuth().user.value)
      return
    }
    error.value = '登录已过期，请重新完成验证并登录'
  }
})

function onCaptchaTicket(payload) {
  captchaTicket.value = payload
}

function goAfterLogin(data) {
  const redirect = route.query.redirect
  const user = data || useAuth().user.value
  if (user?.is_admin) {
    router.replace(typeof redirect === 'string' && redirect.startsWith('/admin') ? redirect : '/admin')
    return
  }
  if (typeof redirect === 'string' && redirect.startsWith('/') && !redirect.startsWith('/admin')) {
    router.replace(redirect)
    return
  }
  router.replace('/create/generate')
}

async function submit() {
  if (!captchaOk.value) {
    error.value = '请先完成拼图验证'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const body = {
      account: account.value.trim(),
      password: password.value,
      captcha_ticket: captchaTicket.value.ticket,
      captcha_randstr: captchaTicket.value.randstr,
    }
    const data = await api.login(body).catch(() => api.register(body))
    setSession(data, rememberMe.value)
    if (rememberMe.value) {
      saveRememberCredentials(account.value.trim())
    } else {
      clearRememberCredentials()
    }
    goAfterLogin(data)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@keyframes spin {
  to { transform: rotate(360deg); }
}
.animate-spin {
  animation: spin 1s linear infinite;
  display: inline-block;
}
</style>
