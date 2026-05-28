<template>
  <div class="min-h-screen bg-background">
    <AppShell :show-quota="false" />
    <div class="max-w-6xl mx-auto px-4 py-8 md:px-8 md:py-12">
      <header class="mb-8 md:mb-10">
        <h1 class="text-2xl md:text-3xl font-bold">升级套餐</h1>
        <p class="mt-2 text-on-surface-variant text-sm md:text-base">
          GPT 生图 ¥0.5/张 · 按次 10～50 张，或包月 80 张 ¥29.9
        </p>
      </header>

      <div class="lg:grid lg:grid-cols-5 lg:gap-8 lg:items-start">
        <!-- 套餐选择 -->
        <section class="lg:col-span-3 space-y-4">
          <!-- 按次包 -->
          <article
            class="rounded-2xl border bg-white p-5 md:p-6 shadow-card transition-colors cursor-pointer"
            :class="selected?.id === 'custom' ? 'border-primary/40 ring-1 ring-primary/20' : 'border-outline-variant'"
            @click="selectPlan(customPlan)"
          >
            <div class="flex items-start justify-between gap-4">
              <div>
                <h2 class="font-bold text-lg">按次生图包</h2>
                <p class="text-sm text-on-surface-variant mt-1">灵活购买，用多少买多少</p>
              </div>
              <p class="text-2xl font-bold text-primary shrink-0">¥{{ formatPrice(customPrice) }}</p>
            </div>

            <div class="mt-5 rounded-xl bg-surface-container-low p-4 space-y-4" @click.stop>
              <div class="flex items-center justify-between gap-3">
                <label class="text-sm font-medium text-on-surface-variant shrink-0" for="quota-input">
                  生图次数
                </label>
                <div class="flex items-center gap-1">
                  <button
                    type="button"
                    class="w-9 h-9 rounded-lg border border-outline-variant flex items-center justify-center hover:bg-white disabled:opacity-40"
                    :disabled="customQuota <= quotaMin"
                    @click="adjustQuota(-1)"
                  >
                    <span class="material-symbols-outlined text-lg">remove</span>
                  </button>
                  <input
                    id="quota-input"
                    v-model="quotaInput"
                    type="number"
                    inputmode="numeric"
                    class="w-16 h-9 text-center font-semibold rounded-lg border border-outline-variant bg-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/30"
                    :min="quotaMin"
                    :max="quotaMax"
                    @blur="commitQuotaInput"
                    @keydown.enter="commitQuotaInput"
                  />
                  <button
                    type="button"
                    class="w-9 h-9 rounded-lg border border-outline-variant flex items-center justify-center hover:bg-white disabled:opacity-40"
                    :disabled="customQuota >= quotaMax"
                    @click="adjustQuota(1)"
                  >
                    <span class="material-symbols-outlined text-lg">add</span>
                  </button>
                  <span class="text-sm text-on-surface-variant ml-1">次</span>
                </div>
              </div>

              <input
                v-model.number="customQuota"
                type="range"
                :min="quotaMin"
                :max="quotaMax"
                step="1"
                class="w-full accent-primary"
                @input="onQuotaSlider"
              />

              <div class="flex flex-wrap gap-2">
                <button
                  v-for="n in quickQuotas"
                  :key="n"
                  type="button"
                  class="px-3 py-1.5 rounded-full text-xs font-medium border transition"
                  :class="
                    customQuota === n
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-outline-variant text-on-surface-variant hover:border-primary/40'
                  "
                  @click="setQuota(n)"
                >
                  {{ n }} 次
                </button>
              </div>

              <p v-if="quotaHint" class="text-xs text-amber-700">{{ quotaHint }}</p>
              <p v-else class="text-xs text-on-surface-variant">
                可输入 {{ quotaMin }}～{{ quotaMax }} 之间的整数
              </p>
            </div>

            <button
              type="button"
              class="mt-5 w-full py-2.5 rounded-lg text-sm font-medium transition"
              :class="
                selected?.id === 'custom'
                  ? 'bg-primary text-on-primary'
                  : 'border border-outline-variant hover:bg-surface-container-low'
              "
              @click.stop="selectPlan(customPlan)"
            >
              {{ selected?.id === 'custom' ? '已选择' : '选择此套餐' }}
            </button>
          </article>

          <!-- 包月 -->
          <article
            class="rounded-2xl border bg-white p-5 md:p-6 shadow-card transition-colors cursor-pointer"
            :class="selected?.id === 'monthly' ? 'border-primary/40 ring-1 ring-primary/20' : 'border-outline-variant'"
            @click="selectPlan(monthlyPlan)"
          >
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="text-xs font-semibold text-primary mb-1">推荐</p>
                <h2 class="font-bold text-lg">{{ monthlyPlan.name }}</h2>
                <p class="text-sm text-on-surface-variant mt-1">{{ monthlyPlan.desc }}</p>
              </div>
              <p class="text-2xl font-bold text-primary shrink-0">¥{{ formatPrice(monthlyPlan.price) }}</p>
            </div>

            <ul class="mt-4 space-y-2 text-sm text-on-surface-variant">
              <li class="flex items-center gap-2">
                <span class="material-symbols-outlined text-base text-primary">check_circle</span>
                每月 {{ monthlyPlan.quota }} 次 GPT 生图
              </li>
              <li class="flex items-center gap-2">
                <span class="material-symbols-outlined text-base text-primary">check_circle</span>
                尊享官方直连通道
              </li>
            </ul>

            <button
              type="button"
              class="mt-5 w-full py-2.5 rounded-lg text-sm font-medium transition"
              :class="
                selected?.id === 'monthly'
                  ? 'bg-primary text-on-primary'
                  : 'border border-outline-variant hover:bg-surface-container-low'
              "
              @click.stop="selectPlan(monthlyPlan)"
            >
              {{ selected?.id === 'monthly' ? '已选择' : '选择此套餐' }}
            </button>
          </article>
        </section>

        <!-- 结账侧栏（略加宽以便展示大尺寸收款码） -->
        <aside class="lg:col-span-2 xl:col-span-2 mt-8 lg:mt-0 min-w-0">
          <div class="lg:sticky lg:top-24 rounded-2xl border border-outline-variant bg-white p-6 shadow-card">
            <h3 class="font-bold text-base mb-4">订单摘要</h3>

            <template v-if="selected">
              <dl class="space-y-3 text-sm">
                <div class="flex justify-between gap-4">
                  <dt class="text-on-surface-variant">套餐</dt>
                  <dd class="font-medium text-right">{{ selected.name }}</dd>
                </div>
                <div v-if="selected.id === 'custom'" class="flex justify-between gap-4">
                  <dt class="text-on-surface-variant">生图次数</dt>
                  <dd class="font-medium">{{ customQuota }} 次</dd>
                </div>
                <div class="flex justify-between gap-4 pt-3 border-t border-outline-variant">
                  <dt class="font-medium">应付金额</dt>
                  <dd class="text-xl font-bold text-primary">¥{{ formatPrice(selected.price) }}</dd>
                </div>
              </dl>

              <button
                v-if="canStartPay"
                type="button"
                class="mt-6 w-full py-3 rounded-xl text-white font-medium inline-flex items-center justify-center gap-2 disabled:opacity-50"
                style="background: #07c160"
                :disabled="paying || !!quotaHint"
                @click="startWechatPay"
              >
                <span class="material-symbols-outlined">qr_code_2</span>
                微信扫码支付
              </button>

              <div v-if="activeOrder" class="mt-5 space-y-3">
                <div
                  v-if="showQr"
                  class="mx-auto w-full rounded-xl border border-outline-variant bg-white p-4 flex items-center justify-center"
                >
                  <img
                    v-if="qrImageSrc"
                    :src="qrImageSrc"
                    alt="微信收款码"
                    class="qr-pay-image w-full h-auto block mx-auto select-none"
                    @error="onQrError"
                  />
                </div>
                <p v-if="showQr" class="text-center text-lg font-bold text-primary">
                  请支付 ¥{{ Number(activeOrder.amount).toFixed(2) }}
                </p>
                <p v-if="showQr" class="text-center text-sm text-on-surface-variant leading-relaxed px-1">
                  扫码后请在微信转账页<strong class="text-on-surface">手动输入 ¥{{ formatPrice(selected?.price) }}</strong>（个人收款码无法自动带金额）
                </p>
                <p v-if="showQr" class="text-center text-xs text-on-surface-variant leading-relaxed px-1">
                  若无法识别：请放大页面后重试，或使用裁切后的纯二维码原图（勿含绿色边框）
                </p>
                <p v-if="showQr && countdownSec > 0" class="text-center text-sm text-amber-700 font-medium">
                  请在 {{ countdownLabel }} 内完成转账
                </p>
                <p v-if="showQr" class="text-center text-xs text-on-surface-variant leading-relaxed">
                  转账后请等待管理员确认收款，套餐将自动开通
                </p>
                <p v-else-if="activeOrder.status === 'paid'" class="text-center text-sm text-secondary font-medium">
                  支付已确认，套餐已开通
                </p>
                <p v-else-if="activeOrder.status === 'expired'" class="text-center text-sm text-red-600">
                  订单已超时，请重新发起支付
                </p>
                <p v-else-if="activeOrder.status === 'rejected'" class="text-center text-sm text-red-600">
                  订单未通过，请重新发起支付
                </p>
              </div>
            </template>

            <p
              v-if="payMsg"
              class="mt-4 text-sm text-center font-medium"
              :class="payOk ? 'text-secondary' : 'text-red-600'"
            >
              {{ payMsg }}
            </p>
          </div>
        </aside>
      </div>
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
const quotaInput = ref('20')
const customPrice = ref(10.0)
const quotaHint = ref('')
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
const quickQuotas = [10, 20, 30, 40, 50]

const customPlan = computed(() => {
  const item = planItems.value.find((p) => p.id === 'custom') || {}
  return {
    id: 'custom',
    name: `AI 生图 ${customQuota.value} 次`,
    price: customPrice.value,
    quota: customQuota.value,
    desc: item.desc || 'GPT 生图 · 10～50 次自选',
    recommended: false,
  }
})

const monthlyPlan = computed(() => {
  const item = planItems.value.find((p) => p.id === 'monthly') || {}
  return {
    id: 'monthly',
    name: item.name || '官方直连包月',
    price: item.price ?? 29.9,
    quota: item.quota ?? 80,
    desc: item.desc || '每月 80 次 · 尊享官方直连通道',
    recommended: true,
  }
})

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

function clampQuota(value) {
  const n = Math.round(Number(value))
  if (Number.isNaN(n)) return null
  return Math.max(quotaMin.value, Math.min(quotaMax.value, n))
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
  selected.value = plan.id === 'custom' ? { ...customPlan.value } : { ...plan }
}

function applyQuota(next) {
  const clamped = clampQuota(next)
  if (clamped === null) {
    quotaHint.value = `请输入 ${quotaMin.value}～${quotaMax.value} 之间的整数`
    return false
  }
  quotaHint.value = ''
  customQuota.value = clamped
  quotaInput.value = String(clamped)
  clearPayState()
  refreshCustomPrice()
  if (selected.value?.id === 'custom') {
    selected.value = { ...customPlan.value }
  }
  return true
}

function setQuota(n) {
  applyQuota(n)
  selectPlan(customPlan.value)
}

function adjustQuota(delta) {
  applyQuota(customQuota.value + delta)
}

function onQuotaSlider() {
  quotaInput.value = String(customQuota.value)
  quotaHint.value = ''
  clearPayState()
  refreshCustomPrice()
  if (selected.value?.id === 'custom') {
    selected.value = { ...customPlan.value }
  }
}

function commitQuotaInput() {
  const raw = quotaInput.value.trim()
  if (!raw) {
    quotaInput.value = String(customQuota.value)
    return
  }
  const clamped = clampQuota(raw)
  if (clamped === null) {
    quotaHint.value = `请输入 ${quotaMin.value}～${quotaMax.value} 之间的整数`
    quotaInput.value = String(customQuota.value)
    return
  }
  applyQuota(clamped)
}

async function refreshCustomPrice() {
  if (quotaHint.value) return
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
      qrImageSrc.value = await QRCode.toDataURL(url, { width: 512, margin: 2, errorCorrectionLevel: 'M' })
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
  const defaultQuota = res.items?.find((p) => p.id === 'custom')?.quota_default ?? 20
  customQuota.value = defaultQuota
  quotaInput.value = String(defaultQuota)
  await refreshCustomPrice()
  selected.value = { ...monthlyPlan.value }
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
  payMsg.value = '收款码加载失败：请将 wechat-pay-qr.png 放到 backend/pay_assets/ 目录，然后重启服务'
  payOk.value = false
}

async function startWechatPay() {
  if (!selected.value || paying.value || quotaHint.value) return
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

<style scoped>
.qr-pay-image {
  width: 100%;
  max-width: 480px;
  min-width: min(100%, 340px);
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
}
</style>
