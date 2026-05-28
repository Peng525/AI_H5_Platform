<template>
  <div class="min-h-screen bg-background">
    <AppShell :show-quota="false" />
    <div class="max-w-4xl mx-auto p-6 md:p-10">
      <h1 class="text-3xl font-bold text-center mb-2">升级套餐，解锁 AI 配图</h1>
      <p class="text-center text-on-surface-variant mb-10">
        统一 GPT 配图引擎 · 按次包约 50% 毛利 · 包月尊享官方直连通道
      </p>

      <div class="grid md:grid-cols-2 gap-6">
        <article
          v-for="p in displayPlans"
          :key="p.id"
          class="bg-white rounded-xl border border-outline-variant p-6 shadow-card relative transition-all cursor-pointer"
          @click="selectPlan(p)"
        >
          <span
            v-if="p.recommended"
            class="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-on-primary text-xs px-3 py-1 rounded-full font-medium"
          >
            推荐
          </span>
          <h3 class="font-bold text-lg">{{ p.name }}</h3>
          <p class="text-3xl font-bold mt-2 text-primary">¥{{ formatPrice(p.price) }}</p>
          <p class="text-sm text-on-surface-variant mt-2">{{ p.desc }}</p>

          <div v-if="p.id === 'custom'" class="mt-5 space-y-3" @click.stop>
            <div class="flex items-center justify-between text-sm">
              <span class="text-on-surface-variant">配图次数</span>
              <span class="font-semibold text-primary">{{ customQuota }} 次</span>
            </div>
            <input
              v-model.number="customQuota"
              type="range"
              :min="quotaMin"
              :max="quotaMax"
              step="1"
              class="w-full accent-primary"
              @input="onCustomQuotaChange"
            />
            <div class="flex justify-between text-xs text-on-surface-variant">
              <span>{{ quotaMin }} 次</span>
              <span>{{ quotaMax }} 次</span>
            </div>
          </div>

          <button
            class="mt-6 w-full py-2.5 rounded-lg text-sm font-medium transition"
            :class="
              selected?.id === p.id
                ? 'bg-primary text-on-primary'
                : 'border border-outline-variant text-on-surface hover:bg-surface-container-low'
            "
            @click.stop="selectPlan(p)"
          >
            {{ selected?.id === p.id ? '已选择' : '选择套餐' }}
          </button>
        </article>
      </div>

      <div v-if="selected" class="mt-12 bg-white rounded-2xl border border-outline-variant p-8 shadow-card max-w-md mx-auto">
        <p class="font-medium text-center mb-2">已选择「{{ selected.name }}」</p>
        <p class="text-center text-2xl font-bold text-primary mb-6">应付 ¥{{ formatPrice(selected.price) }}</p>

        <div class="text-center">
          <button
            v-if="canStartPay"
            class="px-8 py-3 rounded-lg text-white font-medium inline-flex items-center gap-2 disabled:opacity-50"
            style="background: #07C160"
            :disabled="paying"
            @click="startWechatPay"
          >
            <span class="material-symbols-outlined">qr_code_2</span>
            微信扫码支付
          </button>

          <div v-if="activeOrder" class="mt-4 space-y-3">
            <div v-if="showQr" class="w-48 h-48 mx-auto border rounded-xl overflow-hidden bg-white p-2 flex items-center justify-center">
              <img v-if="qrImageSrc" :src="qrImageSrc" alt="微信收款码" class="w-full h-full object-contain" @error="onQrError" />
            </div>
            <p v-if="showQr" class="text-lg font-bold text-primary">
              请支付 ¥{{ Number(activeOrder.amount).toFixed(2) }}
            </p>
            <p v-if="showQr && countdownSec > 0" class="text-sm text-amber-700 font-medium">
              请在 {{ countdownLabel }} 内完成转账
            </p>
            <p v-if="showQr" class="text-xs text-on-surface-variant">
              转账后请等待管理员确认收款，套餐将自动开通
            </p>
            <p v-else-if="activeOrder.status === 'paid'" class="text-sm text-secondary font-medium">
              支付已确认，套餐已开通
            </p>
            <p v-else-if="activeOrder.status === 'expired'" class="text-sm text-red-600">
              订单已超时关闭，请重新发起支付
            </p>
            <p v-else-if="activeOrder.status === 'rejected'" class="text-sm text-red-600">
              订单未通过，请重新发起支付
            </p>
          </div>
        </div>
      </div>

      <p v-if="payMsg" class="mt-6 text-center font-medium" :class="payOk ? 'text-secondary' : 'text-red-600'">{{ payMsg }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import QRCode from 'qrcode'
import { api } from '../api/client'
import { useAuth } from '../composables/useAuth'
import AppShell from '../components/AppShell.vue'

const { updateUser } = useAuth()
const planItems = ref([])
const pricing = ref(null)
const customQuota = ref(20)
const customPrice = ref(6.8)
const selected = ref(null)
const payMsg = ref('')
const payOk = ref(false)
const paying = ref(false)
const activeOrder = ref(null)
const qrImageSrc = ref('')
const countdownSec = ref(0)
let pollTimer = null
let countdownTimer = null

const quotaMin = computed(() => pricing.value?.pack_quota_min ?? 10)
const quotaMax = computed(() => pricing.value?.pack_quota_max ?? 50)

const customPlan = computed(() => {
  const item = planItems.value.find((p) => p.id === 'custom') || {}
  return {
    id: 'custom',
    name: `AI 配图 ${customQuota.value} 次`,
    price: customPrice.value,
    quota: customQuota.value,
    desc: item.desc || 'GPT 配图 · 10～50 次自选',
    recommended: false,
  }
})

const monthlyPlan = computed(() => {
  const item = planItems.value.find((p) => p.id === 'monthly') || {}
  return {
    id: 'monthly',
    name: item.name || '官方直连包月',
    price: item.price ?? 49.9,
    quota: item.quota ?? 60,
    desc: item.desc || '每月 60 次 · 尊享官方直连通道',
    recommended: true,
  }
})

const displayPlans = computed(() => [customPlan.value, monthlyPlan.value])

const showQr = computed(() => {
  const s = activeOrder.value?.status
  return s === 'pending' || s === 'claimed'
})

const canStartPay = computed(() => {
  const s = activeOrder.value?.status
  return !activeOrder.value || s === 'rejected' || s === 'expired'
})

const countdownLabel = computed(() => {
  const m = Math.floor(countdownSec.value / 60)
  const s = countdownSec.value % 60
  return `${m}:${String(s).padStart(2, '0')}`
})

function formatPrice(v) {
  return Number(v).toFixed(1)
}

function clearPayState() {
  activeOrder.value = null
  qrImageSrc.value = ''
  payMsg.value = ''
  stopPoll()
  stopCountdown()
}

function selectPlan(plan) {
  if (selected.value?.id !== plan.id) {
    clearPayState()
  }
  selected.value = plan
}

async function refreshCustomPrice() {
  try {
    const res = await api.quotePack(customQuota.value)
    customPrice.value = res.price
    if (selected.value?.id === 'custom') {
      selected.value = { ...customPlan.value }
    }
  } catch {
    /* 忽略计价失败 */
  }
}

function onCustomQuotaChange() {
  clearPayState()
  refreshCustomPrice()
  if (selected.value?.id === 'custom') {
    selected.value = { ...customPlan.value }
  }
}

function stopCountdown() {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
  countdownSec.value = 0
}

function startCountdown(expiresAt) {
  stopCountdown()
  if (!expiresAt) return
  const tick = () => {
    const left = Math.max(0, Math.floor((new Date(expiresAt).getTime() - Date.now()) / 1000))
    countdownSec.value = left
    if (left <= 0) {
      stopCountdown()
      if (activeOrder.value && showQr.value) {
        activeOrder.value = { ...activeOrder.value, status: 'expired' }
        payMsg.value = '订单已超时，请重新发起支付'
        stopPoll()
      }
    }
  }
  tick()
  countdownTimer = setInterval(tick, 1000)
}

async function renderQr(order) {
  qrImageSrc.value = ''
  if (!order?.qr_code_url) return
  const url = order.qr_code_url
  if (url.startsWith('weixin://')) {
    try {
      qrImageSrc.value = await QRCode.toDataURL(url, { width: 192, margin: 1 })
    } catch {
      payMsg.value = '二维码生成失败'
    }
    return
  }
  const bust = url.includes('?') ? '&' : '?'
  qrImageSrc.value = `${url}${bust}t=${Date.now()}`
}

onMounted(async () => {
  const res = await api.getPlans()
  planItems.value = res.items || []
  pricing.value = res.pricing || null
  if (res.items?.find((p) => p.quota_default)) {
    customQuota.value = res.items.find((p) => p.id === 'custom')?.quota_default ?? 20
  }
  await refreshCustomPrice()
  selected.value = monthlyPlan.value
})

onUnmounted(() => {
  stopPoll()
  stopCountdown()
})

watch(activeOrder, (order) => {
  if (order) {
    renderQr(order)
    if (order.expires_at) startCountdown(order.expires_at)
  }
  if (order?.status === 'pending' || order?.status === 'claimed') {
    startPoll()
  } else {
    stopPoll()
    if (order?.status !== 'pending' && order?.status !== 'claimed') stopCountdown()
  }
})

function stopPoll() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function startPoll() {
  stopPoll()
  pollTimer = setInterval(refreshOrderStatus, 5000)
}

async function refreshOrderStatus() {
  if (!activeOrder.value?.order_id) return
  try {
    const order = await api.getOrder(activeOrder.value.order_id)
    activeOrder.value = {
      ...activeOrder.value,
      status: order.status,
      amount: order.amount,
      expires_at: order.expires_at,
    }
    if (order.status === 'paid') {
      payOk.value = true
      payMsg.value = '套餐已开通，感谢支持！'
      const me = await api.getMe()
      updateUser(me)
      stopPoll()
      stopCountdown()
    } else if (order.status === 'expired') {
      payMsg.value = '订单已超时，请重新发起支付'
      stopPoll()
      stopCountdown()
    }
  } catch {
    /* 忽略轮询失败 */
  }
}

function onQrError() {
  payMsg.value =
    '收款码加载失败：请将 wechat-pay-qr.png 放到 backend/pay_assets/ 目录，然后重启服务'
  payOk.value = false
}

async function startWechatPay() {
  if (!selected.value || paying.value) return
  paying.value = true
  payMsg.value = ''
  payOk.value = false
  try {
    const body = {
      plan_id: selected.value.id,
      payment_channel: 'wechat_qr',
    }
    if (selected.value.id === 'custom') {
      body.quota = customQuota.value
    }
    const res = await api.createOrder(body)
    activeOrder.value = res
  } catch (e) {
    payOk.value = false
    payMsg.value = e.message
  } finally {
    paying.value = false
  }
}
</script>
