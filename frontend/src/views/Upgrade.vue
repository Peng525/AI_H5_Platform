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
          @click="selected = p"
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
            @click.stop="selected = p"
          >
            选择套餐
          </button>
        </article>
      </div>

      <div v-if="selected" class="mt-12 bg-white rounded-2xl border border-outline-variant p-8 shadow-card">
        <p class="font-medium text-center mb-2">已选择「{{ selected.name }}」</p>
        <p class="text-center text-2xl font-bold text-primary mb-6">应付 ¥{{ selected.price }}</p>

        <div class="flex flex-col md:flex-row justify-center items-start gap-10">
          <div class="text-center mx-auto md:mx-0">
            <button
              class="px-8 py-3 rounded-lg text-white font-medium flex items-center gap-2 mx-auto disabled:opacity-50"
              style="background: #07C160"
              :disabled="paying"
              @click="startWechatPay"
            >
              <span class="material-symbols-outlined">qr_code_2</span>
              微信扫码支付
            </button>
            <div v-if="activeOrder" class="mt-4 space-y-3">
              <div class="w-44 h-44 mx-auto border rounded-xl overflow-hidden bg-white p-2">
                <img :src="activeOrder.qr_code_url" alt="微信收款码" class="w-full h-full object-contain" @error="onQrError" />
              </div>
              <p class="text-xs text-on-surface-variant max-w-[200px] mx-auto">
                订单号 #{{ activeOrder.order_id }} · 请支付 <strong class="text-primary">¥{{ activeOrder.amount.toFixed(2) }}</strong>
              </p>
              <p v-if="activeOrder.status === 'pending'" class="text-xs text-amber-700">扫码转账后，点击下方「我已支付」</p>
              <p v-else-if="activeOrder.status === 'claimed'" class="text-xs text-secondary">已提交，等待管理员确认（请留意微信到账提醒）</p>
              <p v-else-if="activeOrder.status === 'paid'" class="text-xs text-secondary">支付已确认，套餐已开通</p>
              <label v-if="activeOrder.status === 'pending'" class="block text-left text-xs max-w-[220px] mx-auto">
                <span class="font-medium">付款备注（选填）</span>
                <input v-model="payRemark" class="mt-1 w-full border rounded-lg px-2 py-1.5" placeholder="如微信昵称后四位" />
              </label>
              <button
                v-if="activeOrder.status === 'pending'"
                type="button"
                class="w-full max-w-[220px] py-2 rounded-lg bg-primary text-on-primary text-sm font-medium"
                :disabled="claiming"
                @click="claimPaid"
              >
                我已支付
              </button>
            </div>
          </div>

          <div class="flex-1 max-w-sm text-sm text-on-surface-variant space-y-2 border-t md:border-t-0 md:border-l border-outline-variant pt-6 md:pt-0 md:pl-8">
            <p class="font-medium text-on-surface">如何确保收到款？</p>
            <ol class="list-decimal list-inside space-y-1.5">
              <li>用户扫码支付后点击「我已支付」</li>
              <li>您的微信会收到到账通知</li>
              <li>管理员在控制台核对金额与订单号后「确认收款」</li>
              <li>确认后用户套餐自动开通</li>
            </ol>
            <p class="text-xs pt-2">管理员收到微信提醒后，请同时检查「中转 API 额度」是否需充值。</p>
          </div>
        </div>

        <div class="mt-8 text-center border-t border-outline-variant pt-6">
          <button
            class="px-6 py-2.5 rounded-lg border-2 border-dashed border-outline-variant text-on-surface-variant text-sm hover:bg-surface-container-low disabled:opacity-50"
            :disabled="paying"
            @click="pay('demo')"
          >
            演示：跳过支付（开发测试）
          </button>
        </div>
      </div>

      <p v-if="payMsg" class="mt-6 text-center font-medium" :class="payOk ? 'text-secondary' : 'text-red-600'">{{ payMsg }}</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api/client'
import { useAuth } from '../composables/useAuth'
import AppShell from '../components/AppShell.vue'

const { updateUser } = useAuth()
const plans = ref([])
const selected = ref(null)
const payMsg = ref('')
const payOk = ref(false)
const paying = ref(false)
const claiming = ref(false)
const activeOrder = ref(null)
const payRemark = ref('')

onMounted(async () => {
  const res = await api.getPlans()
  plans.value = res.items
  selected.value = res.items.find((p) => p.recommended) || res.items[0]
})

function onQrError() {
  payMsg.value = '收款码图片加载失败，请将微信收款码放到 backend/static/wechat-pay-qr.png'
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
      payment_channel: 'wechat',
    })
    activeOrder.value = res
    payRemark.value = ''
  } catch (e) {
    payOk.value = false
    payMsg.value = e.message
  } finally {
    paying.value = false
  }
}

async function claimPaid() {
  if (!activeOrder.value || claiming.value) return
  claiming.value = true
  payMsg.value = ''
  try {
    const order = await api.claimOrderPaid(activeOrder.value.order_id, payRemark.value)
    activeOrder.value = { ...activeOrder.value, status: order.status }
    payOk.value = true
    payMsg.value = '已提交付款申报，请等待管理员在微信到账后确认'
  } catch (e) {
    payOk.value = false
    payMsg.value = e.message
  } finally {
    claiming.value = false
  }
}

async function pay(channel) {
  if (!selected.value || paying.value) return
  paying.value = true
  payMsg.value = ''
  payOk.value = false
  try {
    const res = await api.createOrder({
      plan_id: selected.value.id,
      payment_channel: channel,
    })
    updateUser({
      tier: res.tier,
      quota_total: res.quota_total,
      quota_remaining: res.quota_remaining,
    })
    payOk.value = true
    payMsg.value = res.message
    activeOrder.value = null
  } catch (e) {
    payOk.value = false
    payMsg.value = e.message
  } finally {
    paying.value = false
  }
}
</script>
