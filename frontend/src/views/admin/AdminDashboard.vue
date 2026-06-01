<template>
  <AdminShell title="数据仪表盘">
    <div v-if="dashboardLoading" class="mb-6">
      <PageLoading />
    </div>
    <div v-else-if="dashboardError" class="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
      仪表盘数据加载失败：{{ dashboardError }}
      <button type="button" class="ml-3 underline" @click="loadDashboard">重试</button>
    </div>

    <template v-if="data">
      <div class="grid sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
        <StatCard icon="visibility" label="今日访问" :value="data.visits_today" suffix="次" color="primary" />
        <StatCard icon="calendar_month" label="近 7 日访问" :value="data.visits_7d" suffix="次" color="secondary" />
        <StatCard icon="shopping_cart" label="成交订单" :value="data.orders_paid" suffix="笔" color="amber" />
        <StatCard icon="payments" label="累计成交额" :value="formatMoney(data.revenue_total)" prefix="¥" color="green" />
      </div>

      <div class="grid lg:grid-cols-2 gap-6 mb-6">
        <section class="bg-white rounded-xl border border-outline-variant p-5 shadow-card">
          <h2 class="font-semibold text-sm mb-3">中转 API 充值</h2>
          <p class="text-xs text-on-surface-variant mb-4">
            推理令牌无法自动读取余额，请登录中转平台控制台查看并充值。
          </p>
          <a
            v-if="relayLink?.recharge_url"
            :href="relayLink.recharge_url"
            target="_blank"
            rel="noopener"
            class="inline-flex items-center gap-1 text-sm text-primary font-medium hover:underline"
          >
            前往中转平台钱包
            <span class="material-symbols-outlined text-[16px]">open_in_new</span>
          </a>
          <p v-else class="text-sm text-on-surface-variant">{{ relayLink?.message || '未配置中转充值链接' }}</p>
        </section>

        <section class="bg-white rounded-xl border border-outline-variant p-5 shadow-card">
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
          <div v-else class="space-y-3 max-h-48 overflow-y-auto">
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

      <section class="bg-white rounded-xl border border-outline-variant p-5 shadow-card mb-6">
        <h2 class="font-semibold text-sm mb-4">近 14 日访问趋势</h2>
        <VisitTrendChart
          :chart="data.visit_chart"
          :summary="`近 30 日总访问 ${data.visits_30d} 次 · 注册用户 ${data.users_total}`"
        />
      </section>
    </template>

    <section class="bg-white rounded-xl border border-outline-variant p-5 shadow-card">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
          <h2 class="font-semibold text-sm">近期购买订单</h2>
          <div class="flex flex-wrap items-center gap-2">
            <div class="inline-flex rounded-lg border border-outline-variant p-0.5 bg-surface-container-low">
              <button
                v-for="tab in orderTabs"
                :key="tab.id"
                type="button"
                class="px-3 py-1 text-xs rounded-md transition-colors"
                :class="orderFilter === tab.id ? 'bg-white text-primary font-medium shadow-sm' : 'text-on-surface-variant hover:text-on-surface'"
                @click="setOrderFilter(tab.id)"
              >
                {{ tab.label }}
              </button>
            </div>
            <button
              v-if="orderFilter === 'expired'"
              type="button"
              class="px-3 py-1.5 text-xs rounded-lg border border-red-200 text-red-600 hover:bg-red-50 disabled:opacity-50"
              :disabled="!orders.length || deletingExpired"
              @click="promptDeleteExpired"
            >
              一键删除已超时（{{ orders.length }} 笔）
            </button>
            <span class="text-xs text-on-surface-variant whitespace-nowrap">共 {{ orders.length }} 笔</span>
          </div>
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
              <tr v-if="ordersLoading">
                <td colspan="6" class="py-8 text-center text-on-surface-variant">加载中…</td>
              </tr>
              <tr v-else-if="!orders.length">
                <td colspan="6" class="py-8 text-center text-on-surface-variant">暂无订单</td>
              </tr>
              <tr
                v-for="o in orders"
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

    <ConfirmDialog
      :open="!!confirmDialog"
      :title="confirmDialog?.title || '确认'"
      :message="confirmDialog?.message || ''"
      :confirm-text="confirmDialog?.confirmText || '确定'"
      :cancel-text="confirmDialog?.cancelText || '取消'"
      :danger="confirmDialog?.danger"
      :loading="!!confirmingId || deletingExpired"
      @confirm="onConfirmDialog"
      @cancel="confirmDialog = null"
    />
  </AdminShell>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api/client'
import AdminShell from '../../components/AdminShell.vue'
import StatCard from '../../components/admin/StatCard.vue'
import VisitTrendChart from '../../components/admin/VisitTrendChart.vue'
import ConfirmDialog from '../../components/ConfirmDialog.vue'
import PageLoading from '../../components/PageLoading.vue'
import { useToast } from '../../composables/useToast.js'

const { error: toastError, success: toastSuccess } = useToast()

const data = ref(null)
const dashboardLoading = ref(true)
const dashboardError = ref('')
const relayLink = ref(null)
const confirmingId = ref(null)
const deletingExpired = ref(false)
const confirmDialog = ref(null)
const orders = ref([])
const ordersLoading = ref(false)
const orderFilter = ref('all')

const orderTabs = [
  { id: 'all', label: '全部' },
  { id: 'paid', label: '已支付' },
  { id: 'expired', label: '已超时' },
]

onMounted(async () => {
  await Promise.all([loadDashboard(), loadRelayLink(), loadOrders()])
})

async function loadOrders() {
  ordersLoading.value = true
  try {
    const params = { limit: 50 }
    if (orderFilter.value !== 'all') params.status = orderFilter.value
    orders.value = await api.listAdminOrders(params)
  } catch (e) {
    toastError(e.message || '加载订单失败')
    orders.value = []
  } finally {
    ordersLoading.value = false
  }
}

function setOrderFilter(id) {
  if (orderFilter.value === id) return
  orderFilter.value = id
  loadOrders()
}

function promptDeleteExpired() {
  if (!orders.value.length) return
  confirmDialog.value = {
    title: '删除已超时订单',
    message: `确定删除全部 ${orders.value.length} 笔已超时订单？此操作不可撤销。`,
    confirmText: '全部删除',
    cancelText: '取消',
    danger: true,
    action: 'deleteExpired',
  }
}

async function loadDashboard() {
  dashboardLoading.value = true
  dashboardError.value = ''
  try {
    data.value = await api.getAdminDashboard()
  } catch (e) {
    dashboardError.value = e.message || '加载失败'
  } finally {
    dashboardLoading.value = false
  }
}

async function loadRelayLink() {
  try {
    relayLink.value = await api.getRelayLink()
  } catch {
    relayLink.value = null
  }
}

async function confirmOrder(o) {
  confirmDialog.value = {
    title: '确认收款',
    message: `确认已收到 #${o.id} 的 ¥${o.amount.toFixed(2)} 微信转账？确认后将开通用户套餐。`,
    confirmText: '确认收款',
    order: o,
    action: 'confirm',
  }
}

async function rejectOrder(o) {
  confirmDialog.value = {
    title: '拒绝订单',
    message: `确定拒绝订单 #${o.id}（¥${o.amount.toFixed(2)}）？用户将不会获得套餐。`,
    confirmText: '拒绝订单',
    cancelText: '取消',
    danger: true,
    order: o,
    action: 'reject',
  }
}

async function onConfirmDialog() {
  const dlg = confirmDialog.value
  if (!dlg) return

  if (dlg.action === 'deleteExpired') {
    deletingExpired.value = true
    try {
      const res = await api.deleteExpiredAdminOrders()
      toastSuccess(`已删除 ${res.deleted} 笔已超时订单`)
      confirmDialog.value = null
      await Promise.all([loadDashboard(), loadOrders()])
    } catch (e) {
      toastError(e.message)
    } finally {
      deletingExpired.value = false
    }
    return
  }

  if (!dlg.order) return
  const o = dlg.order
  confirmingId.value = o.id
  try {
    if (dlg.action === 'confirm') {
      await api.confirmAdminOrder(o.id, '微信到账已核对')
      toastSuccess('已确认收款并开通套餐')
    } else {
      await api.rejectAdminOrder(o.id, '未收到对应款项')
      toastSuccess('已拒绝该订单')
    }
    confirmDialog.value = null
    await Promise.all([loadDashboard(), loadOrders()])
  } catch (e) {
    toastError(e.message)
  } finally {
    confirmingId.value = null
  }
}

function statusLabel(s) {
  const map = { paid: '已支付', pending: '待支付', claimed: '待确认', rejected: '已拒绝', failed: '失败', expired: '已超时' }
  return map[s] || s
}

function statusClass(s) {
  if (s === 'paid') return 'bg-secondary/15 text-secondary'
  if (s === 'claimed') return 'bg-amber-100 text-amber-800'
  if (s === 'rejected') return 'bg-red-100 text-red-700'
  return 'bg-surface-container-high text-on-surface-variant'
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
