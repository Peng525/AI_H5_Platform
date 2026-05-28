<template>
  <div class="rounded-lg border border-outline-variant bg-surface-container-lowest p-4">
    <p class="text-sm font-medium mb-2">安全验证</p>
    <div v-if="provider === 'tencent' && appId" class="space-y-2">
      <button
        type="button"
        class="w-full py-2.5 rounded-lg border border-outline-variant text-sm hover:bg-surface-container-low"
        :disabled="loading"
        @click="showCaptcha"
      >
        {{ verified ? '✓ 验证已通过' : '点击完成拼图验证' }}
      </button>
      <p v-if="error" class="text-xs text-red-600">{{ error }}</p>
    </div>
    <div v-else class="space-y-2">
      <button
        type="button"
        class="w-full py-2.5 rounded-lg border border-dashed border-outline-variant text-sm text-on-surface-variant hover:bg-surface-container-low"
        :disabled="loading"
        @click="mockVerify"
      >
        {{ verified ? '✓ 开发模式验证已通过' : '开发模式：点击完成验证' }}
      </button>
      <p class="text-xs text-on-surface-variant">生产环境请配置腾讯云验证码（CAPTCHA_PROVIDER=tencent）</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api/client'

const emit = defineEmits(['verified', 'ticket'])

const provider = ref('mock')
const appId = ref('')
const verified = ref(false)
const loading = ref(false)
const error = ref('')
const ticket = ref('')
const randstr = ref('')

let captchaInstance = null
let sdkLoaded = false

onMounted(async () => {
  try {
    const cfg = await api.getCaptchaConfig()
    provider.value = cfg.provider || 'mock'
    appId.value = cfg.app_id || ''
    if (provider.value === 'tencent' && appId.value) {
      await loadSdk(cfg.sdk_url)
    }
  } catch {
    provider.value = 'mock'
  }
})

function loadSdk(url) {
  if (sdkLoaded || document.querySelector('script[data-tencent-captcha]')) {
    sdkLoaded = true
    return Promise.resolve()
  }
  return new Promise((resolve, reject) => {
    const s = document.createElement('script')
    s.src = url || 'https://turing.captcha.qcloud.com/TJCaptcha.js'
    s.dataset.tencentCaptcha = '1'
    s.onload = () => {
      sdkLoaded = true
      resolve()
    }
    s.onerror = () => reject(new Error('验证码 SDK 加载失败'))
    document.head.appendChild(s)
  })
}

function reset() {
  verified.value = false
  ticket.value = ''
  randstr.value = ''
  emit('verified', false)
  emit('ticket', { ticket: '', randstr: '' })
}

function pass(t, r) {
  ticket.value = t
  randstr.value = r
  verified.value = true
  error.value = ''
  emit('verified', true)
  emit('ticket', { ticket: t, randstr: r })
}

function mockVerify() {
  pass('mock_ticket_dev', 'mock_randstr_dev')
}

async function showCaptcha() {
  if (verified.value) return
  loading.value = true
  error.value = ''
  try {
    await loadSdk()
    if (typeof window.TencentCaptcha !== 'function') {
      throw new Error('验证码组件未就绪')
    }
    captchaInstance = new window.TencentCaptcha(appId.value, (res) => {
      if (res.ret === 0 && res.ticket) {
        pass(res.ticket, res.randstr)
      } else if (res.ret !== 2) {
        error.value = '验证未通过，请重试'
        reset()
      }
    }, { userLanguage: 'zh-cn' })
    captchaInstance.show()
  } catch (e) {
    error.value = e.message || '无法打开验证码'
    reset()
  } finally {
    loading.value = false
  }
}

defineExpose({ reset })
</script>
