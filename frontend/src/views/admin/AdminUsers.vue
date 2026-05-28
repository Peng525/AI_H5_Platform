<template>
  <AdminShell title="用户管理">
    <div class="flex flex-wrap items-center gap-3 mb-6">
      <input
        v-model="search"
        class="border border-outline-variant rounded-lg px-3 py-2 text-sm flex-1 min-w-[200px] max-w-sm"
        placeholder="搜索用户名…"
        @keyup.enter="loadUsers"
      />
      <button class="px-4 py-2 bg-primary text-on-primary rounded-lg text-sm" @click="loadUsers">搜索</button>
      <button
        class="px-4 py-2 border border-primary text-primary rounded-lg text-sm flex items-center gap-1 ml-auto"
        @click="openCreate"
      >
        <span class="material-symbols-outlined text-[18px]">person_add</span>
        创建账号
      </button>
    </div>

    <p class="text-xs text-on-surface-variant mb-4">
      收款后也可在此直接将用户改为 Pro 会员，无需走订单（适合补发或赠送）。
    </p>

    <div v-if="loading" class="text-on-surface-variant">加载中…</div>
    <div v-else class="bg-white rounded-xl border border-outline-variant shadow-card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-surface-container-low">
            <tr class="text-left text-on-surface-variant">
              <th class="px-4 py-3 font-medium">ID</th>
              <th class="px-4 py-3 font-medium">用户名</th>
              <th class="px-4 py-3 font-medium">会员类型</th>
              <th class="px-4 py-3 font-medium">已用 / 配额</th>
              <th class="px-4 py-3 font-medium">剩余次数</th>
              <th class="px-4 py-3 font-medium">注册时间</th>
              <th class="px-4 py-3 font-medium">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id" class="border-t border-outline-variant/50 hover:bg-surface-container-low/50">
              <td class="px-4 py-3 font-mono text-xs">{{ u.id }}</td>
              <td class="px-4 py-3">{{ u.username }}</td>
              <td class="px-4 py-3">
                <span
                  class="px-2 py-0.5 rounded-full text-xs"
                  :class="u.tier === 'pro' ? 'bg-amber-100 text-amber-800' : 'bg-surface-container-high text-on-surface-variant'"
                >
                  {{ u.tier === 'pro' ? 'Pro 会员' : '免费用户' }}
                </span>
              </td>
              <td class="px-4 py-3">{{ u.quota_used }} / {{ u.quota_total === 9999 ? '∞' : u.quota_total }}</td>
              <td class="px-4 py-3 font-medium">{{ u.quota_remaining === 9999 ? '无限' : u.quota_remaining }}</td>
              <td class="px-4 py-3 text-xs text-on-surface-variant">{{ formatTime(u.created_at) }}</td>
              <td class="px-4 py-3">
                <button class="text-primary text-xs hover:underline" @click="openEdit(u)">编辑</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 创建/编辑弹窗 -->
    <div v-if="modalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40" @click.self="modalOpen = false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
        <h3 class="font-bold text-lg mb-4">{{ editing ? '编辑用户' : '创建账号' }}</h3>
        <form class="space-y-4" @submit.prevent="submitForm">
          <label v-if="!editing" class="block text-sm">
            <span class="text-on-surface-variant text-xs">邮箱</span>
            <input v-model="form.username" type="email" required class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" />
          </label>
          <p v-if="editing" class="text-xs text-on-surface-variant bg-surface-container-low rounded-lg p-3">
            收款后也可在此直接改为 Pro，无需走订单确认。
          </p>
          <label class="block text-sm">
            <span class="text-on-surface-variant text-xs">{{ editing ? '新密码（留空不修改）' : '密码' }}</span>
            <input v-model="form.password" type="password" :required="!editing" minlength="6" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" />
          </label>
          <label class="block text-sm">
            <span class="text-on-surface-variant text-xs">会员类型</span>
            <select v-model="form.tier" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2">
              <option value="free">免费用户</option>
              <option value="pro">Pro 会员</option>
            </select>
          </label>
          <label v-if="form.tier === 'free'" class="block text-sm">
            <span class="text-on-surface-variant text-xs">API 配额上限</span>
            <input v-model.number="form.quota_limit" type="number" min="0" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" placeholder="留空使用系统默认" />
          </label>
          <label v-if="editing && form.tier === 'free'" class="block text-sm">
            <span class="text-on-surface-variant text-xs">已使用次数</span>
            <input v-model.number="form.quota_used" type="number" min="0" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" />
          </label>
          <p v-if="formError" class="text-red-600 text-sm">{{ formError }}</p>
          <div class="flex gap-2 pt-2">
            <button type="button" class="flex-1 py-2 border border-outline-variant rounded-lg text-sm" @click="modalOpen = false">取消</button>
            <button type="submit" class="flex-1 py-2 bg-primary text-on-primary rounded-lg text-sm" :disabled="saving">
              {{ saving ? '保存中…' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </AdminShell>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api/client'
import AdminShell from '../../components/AdminShell.vue'

const users = ref([])
const loading = ref(true)
const search = ref('')
const modalOpen = ref(false)
const editing = ref(null)
const saving = ref(false)
const formError = ref('')
const form = ref({ username: '', password: '', tier: 'free', quota_limit: null, quota_used: 0 })

onMounted(loadUsers)

async function loadUsers() {
  loading.value = true
  try {
    users.value = await api.listAdminUsers(search.value)
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editing.value = null
  form.value = { username: '', password: '', tier: 'free', quota_limit: 5, quota_used: 0 }
  formError.value = ''
  modalOpen.value = true
}

function openEdit(u) {
  editing.value = u
  form.value = {
    username: u.username,
    password: '',
    tier: u.tier,
    quota_limit: u.quota_total === 9999 ? null : u.quota_total,
    quota_used: u.quota_used,
  }
  formError.value = ''
  modalOpen.value = true
}

async function submitForm() {
  saving.value = true
  formError.value = ''
  try {
    if (editing.value) {
      const body = {
        tier: form.value.tier,
        free_quota_used: form.value.quota_used,
      }
      if (form.value.tier === 'free' && form.value.quota_limit != null) {
        body.quota_limit = form.value.quota_limit
      }
      if (form.value.password) body.password = form.value.password
      await api.updateAdminUser(editing.value.id, body)
    } else {
      await api.createAdminUser({
        username: form.value.username,
        password: form.value.password,
        tier: form.value.tier,
        quota_limit: form.value.tier === 'free' ? form.value.quota_limit : null,
      })
    }
    modalOpen.value = false
    await loadUsers()
  } catch (e) {
    formError.value = e.message
  } finally {
    saving.value = false
  }
}

function formatTime(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('zh-CN', { hour12: false })
}
</script>
