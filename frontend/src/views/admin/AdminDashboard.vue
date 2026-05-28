<template>
  <AdminShell title="数据仪表盘">
    <div v-if="loading" class="text-on-surface-variant">加载中…</div>
    <template v-else-if="data">
      <!-- 统计卡片 -->
      <div class="grid sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-8">
        <StatCard icon="visibility" label="今日访问" :value="data.visits_today" suffix="次" color="primary" />
        <StatCard icon="calendar_month" label="近 7 日访问" :value="data.visits_7d" suffix="次" color="secondary" />
        <StatCard icon="shopping_cart" label="成交订单" :value="data.orders_paid" suffix="笔" color="amber" />
        <StatCard icon="payments" label="累计成交额" :value="formatMoney(data.revenue_total)" prefix="¥" color="green" />
      </div>

      <div class="grid lg:grid-cols-3 gap-6 mb-8">
        <!-- 访问趋势 -->
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

        <!-- 订单概览 -->
        <section class="lg:col-span-2 bg-white rounded-xl border border-outline-variant p-5 shadow-card">
          <div class="flex items-center justify-between mb-4">
            <h2 class="font-semibold text-sm">近期购买订单</h2>
            <span class="text-xs text-on-surface-variant">共 {{ data.orders_total }} 笔</span>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="text-left text-on-surface-variant border-b border-outline-variant">
                  <th class="pb-2 pr-3 font-medium">用户 ID</th>
                  <th class="pb-2 pr-3 font-medium">用户名称</th>
                  <th class="pb-2 pr-3 font-medium">购买类型</th>
                  <th class="pb-2 pr-3 font-medium">成交金额</th>
                  <th class="pb-2 pr-3 font-medium">剩余次数</th>
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
                  <td class="py-2.5 pr-3 font-mono text-xs">{{ o.user_id }}</td>
                  <td class="py-2.5 pr-3">{{ o.username }}</td>
                  <td class="py-2.5 pr-3">
                    <span class="px-2 py-0.5 rounded-full text-xs bg-primary/10 text-primary">{{ o.plan_name }}</span>
                  </td>
                  <td class="py-2.5 pr-3 font-medium">¥{{ o.amount.toFixed(2) }}</td>
                  <td class="py-2.5 pr-3">{{ o.quota_remaining === 9999 ? '无限' : o.quota_remaining }}</td>
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

onMounted(async () => {
  try {
    data.value = await api.getAdminDashboard()
    maxVisit.value = Math.max(1, ...data.value.visit_chart.map((d) => d.count))
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

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
