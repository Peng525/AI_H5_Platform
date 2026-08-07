<template>
  <AdminShell title="AI 生成记录">
    <div class="flex flex-wrap items-center gap-3 mb-6">
      <input
        v-model="search"
        class="border border-outline-variant rounded-lg px-3 py-2 text-sm flex-1 min-w-[200px] max-w-sm"
        placeholder="搜索用户名…"
        @keyup.enter="loadLogs"
      />
      <button class="px-4 py-2 bg-primary text-on-primary rounded-lg text-sm" @click="loadLogs">搜索</button>
    </div>

    <p class="text-xs text-on-surface-variant mb-4">
      展示用户 AI 全量生成与配图调用记录，含模型与耗时。用户端生成结果页不再显示此类信息。
    </p>

    <PageLoading v-if="loading" />
    <div v-else class="bg-white rounded-xl border border-outline-variant shadow-card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-surface-container-low">
            <tr class="text-left text-on-surface-variant">
              <th class="px-4 py-3 font-medium">用户</th>
              <th class="px-4 py-3 font-medium">类型</th>
              <th class="px-4 py-3 font-medium">模型</th>
              <th class="px-4 py-3 font-medium">耗时</th>
              <th class="px-4 py-3 font-medium">Token (输入/输出)</th>
              <th class="px-4 py-3 font-medium">通道</th>
              <th class="px-4 py-3 font-medium">状态</th>
              <th class="px-4 py-3 font-medium">时间</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in items"
              :key="row.id"
              class="border-t border-outline-variant/50 hover:bg-surface-container-low/50"
            >
              <td class="px-4 py-3">{{ row.username || '—' }}</td>
              <td class="px-4 py-3 text-xs">{{ templateLabel(row.template_id) }}</td>
              <td class="px-4 py-3 font-mono text-xs">{{ row.model || '—' }}</td>
              <td class="px-4 py-3">{{ formatDuration(row.duration_ms) }}</td>
              <td class="px-4 py-3 font-mono text-xs">
                <span v-if="row.prompt_tokens || row.completion_tokens">
                  {{ fmtK(row.prompt_tokens) }} / {{ fmtK(row.completion_tokens) }}
                  <span class="text-on-surface-variant ml-1">({{ fmtK((row.prompt_tokens || 0) + (row.completion_tokens || 0)) }})</span>
                </span>
                <span v-else class="text-on-surface-variant/50">—</span>
              </td>
              <td class="px-4 py-3 text-xs">{{ row.channel || '—' }}</td>
              <td class="px-4 py-3">
                <span
                  class="px-2 py-0.5 rounded-full text-xs"
                  :class="row.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                >
                  {{ row.success ? '成功' : '失败' }}
                </span>
              </td>
              <td class="px-4 py-3 text-xs text-on-surface-variant whitespace-nowrap">{{ formatTime(row.created_at) }}</td>
            </tr>
            <tr v-if="!items.length">
              <td colspan="8" class="px-4 py-8 text-center text-on-surface-variant text-sm">暂无记录</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="total > pageSize" class="px-4 py-3 border-t border-outline-variant/50 flex items-center justify-between text-xs text-on-surface-variant">
        <span>共 {{ total }} 条</span>
        <div class="flex items-center gap-2">
          <button
            type="button"
            class="px-3 py-1 border border-outline-variant rounded-lg disabled:opacity-40"
            :disabled="page <= 1"
            @click="goPage(page - 1)"
          >
            上一页
          </button>
          <span>{{ page }} / {{ totalPages }}</span>
          <button
            type="button"
            class="px-3 py-1 border border-outline-variant rounded-lg disabled:opacity-40"
            :disabled="page >= totalPages"
            @click="goPage(page + 1)"
          >
            下一页
          </button>
        </div>
      </div>
    </div>
  </AdminShell>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import AdminShell from '../../components/AdminShell.vue'
import PageLoading from '../../components/PageLoading.vue'
import { api } from '../../api/client'
import { formatDuration } from '../../utils/formatDuration.js'

const loading = ref(true)
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 50
const search = ref('')

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

function fmtK(n) {
  if (!n) return '0'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return String(n)
}

function templateLabel(id) {
  if (id === 'full_deck') return '全量生成'
  if (id === 'orchestrated_deck') return '编排生成'
  if (id === 'single_slide') return '单页改写'
  if (id === 'image_gen') return '配图/生图'
  return id || '—'
}

function formatTime(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('zh-CN', { hour12: false })
  } catch {
    return iso
  }
}

async function loadLogs() {
  loading.value = true
  try {
    const data = await api.listAdminGenerationLogs({
      page: page.value,
      page_size: pageSize,
      username: search.value.trim(),
    })
    items.value = data.items || []
    total.value = data.total || 0
  } catch (e) {
    items.value = []
    total.value = 0
    console.error(e)
  } finally {
    loading.value = false
  }
}

function goPage(p) {
  page.value = p
  loadLogs()
}

onMounted(loadLogs)
</script>
