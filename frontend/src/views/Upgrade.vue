<template>
  <div class="min-h-screen bg-background">
    <AppShell page-title="套餐升级" :show-quota="false" />
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
          <ul class="mt-4 space-y-2 text-sm text-on-surface-variant">
            <li class="flex items-center gap-2">
              <span class="material-symbols-outlined text-secondary text-[16px]">check</span>
              {{ p.quota === -1 ? '无限次' : p.quota + ' 次' }} AI 生成
            </li>
            <li class="flex items-center gap-2">
              <span class="material-symbols-outlined text-secondary text-[16px]">check</span>
              Gemini 3 Pro 模型
            </li>
            <li class="flex items-center gap-2">
              <span class="material-symbols-outlined text-secondary text-[16px]">check</span>
              官方 API 直连
            </li>
          </ul>
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
        <p class="font-medium text-center mb-6">已选择「{{ selected.name }}」· ¥{{ selected.price }}</p>
        <div class="flex flex-col md:flex-row justify-center items-center gap-8">
          <div class="text-center">
            <button
              class="px-8 py-3 rounded-lg text-white font-medium flex items-center gap-2 mx-auto"
              style="background: #07C160"
              @click="mockPay('wechat')"
            >
              <span class="material-symbols-outlined">qr_code_2</span>
              微信支付
            </button>
            <div class="w-36 h-36 mt-4 mx-auto bg-surface-container-low border rounded-lg flex items-center justify-center">
              <span class="text-xs text-on-surface-variant">微信扫码</span>
            </div>
          </div>
          <div class="text-center">
            <button
              class="px-8 py-3 rounded-lg bg-primary text-on-primary font-medium flex items-center gap-2 mx-auto"
              @click="mockPay('alipay')"
            >
              <span class="material-symbols-outlined">payments</span>
              支付宝
            </button>
            <div class="w-36 h-36 mt-4 mx-auto bg-surface-container-low border rounded-lg flex items-center justify-center">
              <span class="text-xs text-on-surface-variant">支付宝扫码</span>
            </div>
          </div>
        </div>
        <div class="mt-8 text-center">
          <button
            class="px-6 py-2.5 rounded-lg border-2 border-dashed border-primary text-primary text-sm font-medium hover:bg-primary/5"
            @click="mockPay('demo')"
          >
            演示：模拟支付成功
          </button>
          <p class="text-xs text-on-surface-variant mt-3">正式版将对接微信/支付宝支付回调</p>
        </div>
      </div>

      <p v-if="payMsg" class="mt-6 text-center text-secondary font-medium">{{ payMsg }}</p>
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

onMounted(async () => {
  const res = await api.getPlans()
  plans.value = res.items
  selected.value = res.items.find((p) => p.recommended) || res.items[0]
})

async function mockPay(channel) {
  if (!selected.value) return
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
    const names = { wechat: '微信', alipay: '支付宝', demo: '演示' }
    payMsg.value = `${names[channel] || '演示'}：${res.message}`
  } catch (e) {
    payMsg.value = e.message
  }
}
</script>
