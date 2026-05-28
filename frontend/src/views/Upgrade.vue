<template>
  <div class="min-h-screen bg-background">
    <EditorTopBar project-title="套餐升级" />
    <div class="max-w-5xl mx-auto p-8">
      <h1 class="text-2xl font-bold text-center mb-2">升级套餐</h1>
      <p class="text-center text-on-surface-variant mb-8">解锁官方高速 API 与 Pro 模型</p>
      <div class="grid md:grid-cols-3 gap-6">
        <article
          v-for="p in plans"
          :key="p.id"
          class="bg-white rounded-xl border p-6 shadow-card relative"
          :class="p.recommended ? 'border-primary border-2' : 'border-outline-variant'"
        >
          <span v-if="p.recommended" class="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-on-primary text-xs px-3 py-1 rounded-full">推荐</span>
          <h3 class="font-bold text-lg">{{ p.name }}</h3>
          <p class="text-3xl font-bold mt-2">¥{{ p.price }}</p>
          <p class="text-sm text-on-surface-variant mt-2">{{ p.desc }}</p>
          <button class="mt-6 w-full py-2 border border-outline-variant rounded-lg text-sm" @click="mockPay(p)">
            选择套餐
          </button>
        </article>
      </div>
      <div class="mt-12 text-center">
        <p class="font-medium mb-4">请扫码支付</p>
        <div class="flex justify-center gap-8">
          <div class="w-32 h-32 bg-surface-container-low border rounded-lg flex items-center justify-center text-xs text-on-surface-variant">微信支付</div>
          <div class="w-32 h-32 bg-surface-container-low border rounded-lg flex items-center justify-center text-xs text-on-surface-variant">支付宝</div>
        </div>
        <p class="text-xs text-on-surface-variant mt-4">演示环境：点击套餐即模拟支付成功</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api/client'
import EditorTopBar from '../components/EditorTopBar.vue'

const plans = ref([])

onMounted(async () => {
  const res = await api.getPlans()
  plans.value = res.items
})

function mockPay(plan) {
  alert(`演示：已选择「${plan.name}」，正式版将对接微信/支付宝`)
}
</script>
