<template>
  <div class="min-h-screen bg-background">
    <AppShell :show-quota="false" />
    <div class="max-w-5xl mx-auto p-6 md:p-10">
      <h1 class="text-3xl font-bold text-center mb-2">升级套餐，解锁官方高速 API</h1>
      <p class="text-center text-on-surface-variant mb-10">使用 Gemini 3 Pro 模型，享受无限次 AI 生成</p>

      <div class="grid md:grid-cols-3 gap-6">
        <article
          v-for="p in plans"
          :key="p.id"
          class="bg-white rounded-xl border p-6 shadow-card relative transition-all cursor-pointer"
          :class="[
            p.recommended ? 'border-primary border-2 scale-[1.02]' : 'border-outline-variant',
            selected?.id === p.id ? 'ring-2 ring-primary/30' : '',
          ]"
          @click="selectPlan(p)"
        >
          <span v-if="p.recommended" class="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-on-primary text-xs px-3 py-1 rounded-full font-medium">
            推荐
          </span>
          <h3 class="font-bold text-lg">{{ p.name }}</h3>
          <p class="text-3xl font-bold mt-2 text-primary">¥{{ p.price }}</p>
          <p class="text-sm text-on-surface-variant mt-2">{{ p.desc }}</p>
          <button
            class="mt-6 w-full py-2.5 rounded-lg text-sm font-medium transition"
            :class="p.recommended ? 'bg-primary text-on-primary' : 'border border-outline-variant hover:bg-surface-container-low'"
            @click.stop="selectPlan(p)"
          >
            选择套餐
          </button>
        </article>
      </div>

      <div v-if="selected" class="mt-12 bg-white rounded-2xl border border-outline-variant p-8 shadow-card max-w-md mx-auto">
        <p class="font-medium text-center mb-2">已选择「{{ selected.name }}」</p>
        <p class="text-center text-2xl font-bold text-primary mb-6">应付 ¥{{ selected.price }}</p>

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
const plans = ref([])
const selected = ref(null)
const payMsg = ref('')
const payOk = ref(false)
const paying = ref(false)
const activeOrder = ref(null)
const qrImageSrc = ref('')
const countdownSec = ref(0)
let pollTimer = null
let countdownTimer = null

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

function selectPlan(plan) {
  if (selected.value?.id !== plan.id) {
    activeOrder.value = null
    qrImageSrc.value = ''
    payMsg.value = ''
    stopPoll()
    stopCountdown()
  }
  selected.value = plan
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
  plans.value = res.items
  selected.value = res.items.find((p) => p.recommended) || res.items[0]
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
    const res = await api.createOrder({
      plan_id: selected.value.id,
      payment_channel: 'wechat_qr',
    })
    activeOrder.value = res
  } catch (e) {
    payOk.value = false
    payMsg.value = e.message
  } finally {
    paying.value = false
  }
}
</script>
