<template>
  <AdminShell title="数据仪表盘">
    <div v-if="loading" class="text-on-surface-variant">加载中…</div>
    <template v-else-if="data">
      <div v-if="relayQuota?.is_low" class="mb-6 p-4 rounded-xl bg-amber-50 border border-amber-200 text-sm">
        <p class="font-semibold text-amber-900 flex items-center gap-2">
          <span class="material-symbols-outlined">warning</span>
          中转 API 余额不足
        </p>
        <p class="mt-1 text-amber-800">{{ relayQuota.message }}</p>
        <p class="mt-1 text-amber-800">{{ relayQuota.remaining_label }}</p>
        <a
          v-if="relayQuota.recharge_url"
          :href="relayQuota.recharge_url"
          target="_blank"
          rel="noopener"
          class="inline-flex items-center gap-1 mt-2 text-primary font-medium hover:underline"
        >
          前往中转平台充值
          <span class="material-symbols-outlined text-[16px]">open_in_new</span>
        </a>
      </div>

      <div class="grid sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-8">
        <StatCard icon="visibility" label="今日访问" :value="data.visits_today" suffix="次" color="primary" />
        <StatCard icon="calendar_month" label="近 7 日访问" :value="data.visits_7d" suffix="次" color="secondary" />
        <StatCard icon="shopping_cart" label="成交订单" :value="data.orders_paid" suffix="笔" color="amber" />
        <StatCard icon="payments" label="累计成交额" :value="formatMoney(data.revenue_total)" prefix="¥" color="green" />
      </div>

      <div class="grid lg:grid-cols-3 gap-6 mb-8">
        <section class="bg-white rounded-xl border border-outline-variant p-5 shadow-card">
          <div class="flex items-center justify-between mb-3">
            <h2 class="font-semibold text-sm">中转 API 额度</h2>
            <button type="button" class="text-xs text-primary hover:underline" :disabled="relayLoading" @click="loadRelayQuota">
              刷新
            </button>
          </div>
          <p v-if="relayLoading" class="text-xs text-on-surface-variant">查询中…</p>
          <p v-else-if="relayError" class="text-xs text-red-600">{{ relayError }}</p>
          <template v-else-if="relayQuota">
            <p class="text-lg font-bold" :class="relayQuota.is_low ? 'text-amber-700' : 'text-secondary'">
              {{ relayQuota.remaining_label }}
            </p>
            <p class="text-xs text-on-surface-variant mt-2">{{ relayQuota.message }}</p>
            <a
              v-if="relayQuota.recharge_url"
              :href="relayQuota.recharge_url"
              target="_blank"
              rel="noopener"
              class="inline-block mt-3 text-sm text-primary hover:underline"
            >
              充值中转 API →
            </a>
          </template>
        </section>

        <section class="lg:col-span-2 bg-white rounded-xl border border-outline-variant p-5 shadow-card">
          <h2 class="font-semibold text-sm mb-3">
            待支付订单（微信）
            <span v-if="data.orders_pending_confirm" class="ml-2 text-xs bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full">
              {{ data.orders_pending_confirm }} 笔
            </span>
          </h2>
          <p class="text-xs text-on-surface-variant mb-3">
            用户扫码下单后，请对照微信到账通知核对订单号、用户 ID 与金额后确认收款并开通套餐。
            也可在 <router-link to="/admin/users" class="text-primary hover:underline">用户管理</router-link> 直接改为 Pro（补发/赠送）。
          </p>
          <div v-if="!data.pending_payment_orders?.length" class="text-sm text-on-surface-variant py-6 text-center">
            暂无待确认订单
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="o in data.pending_payment_orders"
              :key="o.id"
              class="flex flex-wrap items-center justify-between gap-3 p-3 rounded-lg bg-surface-container-low text-sm"
            >
              <div>
                <p class="font-medium">#{{ o.id }} · 用户 {{ o.user_id }} · {{ o.username }} · ¥{{ o.amount.toFixed(2) }}</p>
                <p class="text-xs text-on-surface-variant mt-0.5">{{ o.plan_name }} · {{ o.payment_channel }}</p>
              </div>
              <div class="flex gap-2">
                <button
                  type="button"
                  class="px-3 py-1.5 rounded-lg bg-primary text-on-primary text-xs font-medium disabled:opacity-50"
                  :disabled="confirmingId === o.id"
                  @click="confirmOrder(o)"
                >
                  确认收款
                </button>
                <button
                  type="button"
                  class="px-3 py-1.5 rounded-lg border border-red-200 text-red-600 text-xs"
                  :disabled="confirmingId === o.id"
                  @click="rejectOrder(o)"
                >
                  拒绝
                </button>
              </div>
            </div>
          </div>
        </section>
      </div>

      <div class="grid lg:grid-cols-3 gap-6 mb-8">
        <section class="lg:col-span-1 bg-white rounded-xl border border-outline-variant p-5 shadow-card">
          <h2 class="font-semibold text-sm mb-4">近 14 日访问趋势</h2>
          <div class="flex items-end gap-1 h-32">
            <div
              v-for="(d, i) in data.visit_chart"
              :key="i"
              class="flex-1 flex flex-col items-center gap-1 min-w-0"
            >
              <div
                class="w-full rounded-t bg-primary/80 min-h-[2px] transition-all"
                :style="{ height: barHeight(d.count) + '%' }"
                :title="`${d.date}: ${d.count}`"
              />
              <span v-if="i % 2 === 0" class="text-[9px] text-on-surface-variant truncate w-full text-center">
                {{ d.date.slice(5) }}
              </span>
            </div>
          </div>
          <p class="text-xs text-on-surface-variant mt-3">近 30 日总访问 {{ data.visits_30d }} 次 · 注册用户 {{ data.users_total }}</p>
        </section>

        <section class="lg:col-span-2 bg-white rounded-xl border border-outline-variant p-5 shadow-card">
          <div class="flex items-center justify-between mb-4">
            <h2 class="font-semibold text-sm">近期购买订单</h2>
            <span class="text-xs text-on-surface-variant">共 {{ data.orders_total }} 笔</span>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="text-left text-on-surface-variant border-b border-outline-variant">
                  <th class="pb-2 pr-3 font-medium">订单</th>
                  <th class="pb-2 pr-3 font-medium">用户</th>
                  <th class="pb-2 pr-3 font-medium">套餐</th>
                  <th class="pb-2 pr-3 font-medium">金额</th>
                  <th class="pb-2 pr-3 font-medium">状态</th>
                  <th class="pb-2 font-medium">时间</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!data.recent_orders.length">
                  <td colspan="6" class="py-8 text-center text-on-surface-variant">暂无订单</td>
                </tr>
                <tr
                  v-for="o in data.recent_orders"
                  :key="o.id"
                  class="border-b border-outline-variant/50 hover:bg-surface-container-low"
                >
                  <td class="py-2.5 pr-3 font-mono text-xs">#{{ o.id }}</td>
                  <td class="py-2.5 pr-3">{{ o.username }}</td>
                  <td class="py-2.5 pr-3">{{ o.plan_name }}</td>
                  <td class="py-2.5 pr-3 font-medium">¥{{ o.amount.toFixed(2) }}</td>
                  <td class="py-2.5 pr-3">
                    <span class="text-xs px-2 py-0.5 rounded-full" :class="statusClass(o.status)">{{ statusLabel(o.status) }}</span>
                  </td>
                  <td class="py-2.5 text-xs text-on-surface-variant whitespace-nowrap">{{ formatTime(o.created_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </template>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>
  </AdminShell>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api/client'
import AdminShell from '../../components/AdminShell.vue'
import StatCard from '../../components/admin/StatCard.vue'

const data = ref(null)
const loading = ref(true)
const error = ref('')
const maxVisit = ref(1)
const relayQuota = ref(null)
const relayLoading = ref(false)
const relayError = ref('')
const confirmingId = ref(null)

onMounted(async () => {
  await Promise.all([loadDashboard(), loadRelayQuota()])
})

async function loadDashboard() {
  loading.value = true
  error.value = ''
  try {
    data.value = await api.getAdminDashboard()
    maxVisit.value = Math.max(1, ...data.value.visit_chart.map((d) => d.count))
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function loadRelayQuota() {
  relayLoading.value = true
  relayError.value = ''
  try {
    relayQuota.value = await api.getRelayQuota()
  } catch (e) {
    relayError.value = e.message
  } finally {
    relayLoading.value = false
  }
}

async function confirmOrder(o) {
  if (!confirm(`确认已收到 #${o.id} 的 ¥${o.amount.toFixed(2)} 微信转账？\n确认后将开通用户套餐。`)) return
  confirmingId.value = o.id
  try {
    await api.confirmAdminOrder(o.id, '微信到账已核对')
    await loadDashboard()
  } catch (e) {
    alert(e.message)
  } finally {
    confirmingId.value = null
  }
}

async function rejectOrder(o) {
  confirmingId.value = o.id
  try {
    await api.rejectAdminOrder(o.id, '未收到对应款项')
    await loadDashboard()
  } catch (e) {
    alert(e.message)
  } finally {
    confirmingId.value = null
  }
}

function statusLabel(s) {
  const map = { paid: '已支付', pending: '待支付', claimed: '待确认', rejected: '已拒绝', failed: '失败' }
  return map[s] || s
}

function statusClass(s) {
  if (s === 'paid') return 'bg-secondary/15 text-secondary'
  if (s === 'claimed') return 'bg-amber-100 text-amber-800'
  if (s === 'rejected') return 'bg-red-100 text-red-700'
  return 'bg-surface-container-high text-on-surface-variant'
}

function barHeight(count) {
  return Math.max(4, (count / maxVisit.value) * 100)
}

function formatMoney(n) {
  return Number(n).toFixed(2)
}

function formatTime(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
</script>
