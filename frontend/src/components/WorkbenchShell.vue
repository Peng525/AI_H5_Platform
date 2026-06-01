<template>
  <div class="h-screen bg-surface-container-low flex overflow-hidden">
    <!-- Icon rail -->
    <aside
      class="hidden sm:flex w-14 h-full bg-surface border-r border-outline-variant flex-col items-center py-3 gap-1 shrink-0"
    >
      <router-link
        v-for="item in iconNav"
        :key="item.to"
        :to="item.to"
        class="w-10 h-10 rounded-lg flex items-center justify-center transition-colors"
        :class="isActive(item.match) ? 'bg-primary/10 text-primary' : 'text-on-surface-variant hover:bg-surface-container-high'"
        :title="item.label"
      >
        <span class="material-symbols-outlined text-[22px]">{{ item.icon }}</span>
      </router-link>
    </aside>

    <!-- Secondary panel -->
    <aside
      class="w-52 h-full bg-surface border-r border-outline-variant flex flex-col shrink-0"
      :class="mobileNavOpen ? 'fixed inset-y-0 left-0 z-40 sm:relative sm:z-auto' : 'hidden sm:flex'"
    >
      <div class="p-4 border-b border-outline-variant shrink-0">
        <div class="flex items-center gap-2.5 min-w-0">
          <span class="w-9 h-9 shrink-0 rounded-full bg-primary text-on-primary flex items-center justify-center text-sm font-bold">
            {{ avatarLetter }}
          </span>
          <div class="min-w-0">
            <p class="text-sm font-semibold truncate" :title="displayName">{{ displayName }}</p>
            <p class="text-[11px] text-on-surface-variant truncate">
              {{ tierLabel }} · 配额 {{ quotaFailed ? '—' : `${quota.remaining}/${quota.total}` }}
            </p>
          </div>
        </div>
      </div>

      <nav class="flex-1 min-h-0 overflow-y-auto p-3 space-y-1">
        <router-link
          v-for="item in sectionNav"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm transition-colors"
          :class="isActive(item.match) ? 'bg-primary/10 text-primary font-medium' : 'text-on-surface-variant hover:bg-surface-container-high'"
          @click="mobileNavOpen = false"
        >
          <span class="material-symbols-outlined text-[20px]">{{ item.icon }}</span>
          {{ item.label }}
        </router-link>
        <router-link
          v-if="isAdmin"
          to="/admin"
          class="flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm text-on-surface-variant hover:bg-surface-container-high"
          @click="mobileNavOpen = false"
        >
          <span class="material-symbols-outlined text-[20px]">admin_panel_settings</span>
          管理控制台
        </router-link>
      </nav>

      <div class="p-3 border-t border-outline-variant space-y-1 shrink-0">
        <router-link
          to="/help"
          class="block px-3 py-2 rounded-lg text-sm text-on-surface-variant hover:bg-surface-container-high"
          @click="mobileNavOpen = false"
        >
          使用帮助
        </router-link>
        <router-link
          v-if="showUpgradeLink"
          to="/upgrade"
          class="block px-3 py-2 rounded-lg text-sm text-amber-800 hover:bg-amber-50"
          @click="mobileNavOpen = false"
        >
          升级会员
        </router-link>
        <button
          type="button"
          class="w-full text-left px-3 py-2 rounded-lg text-sm text-red-600 hover:bg-red-50"
          @click="openLogout"
        >
          退出登录
        </button>
      </div>
    </aside>

    <div
      v-if="mobileNavOpen"
      class="fixed inset-0 bg-black/30 z-30 sm:hidden"
      @click="mobileNavOpen = false"
    />

    <!-- Main -->
    <div class="flex-1 flex flex-col min-h-0 min-w-0">
      <header class="h-14 border-b border-outline-variant bg-white flex items-center justify-between gap-3 px-4 sm:px-6 shrink-0">
        <div class="flex items-center gap-2 min-w-0">
          <button
            type="button"
            class="sm:hidden w-9 h-9 rounded-lg hover:bg-surface-container-high flex items-center justify-center shrink-0"
            aria-label="打开菜单"
            @click="mobileNavOpen = true"
          >
            <span class="material-symbols-outlined text-[22px]">menu</span>
          </button>
          <h1 class="text-lg font-semibold truncate">{{ pageTitle }}</h1>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <router-link
            to="/create/generate"
            class="inline-flex items-center gap-1 px-3 sm:px-4 py-2 rounded-lg bg-primary text-on-primary text-sm font-medium shadow-card hover:bg-primary-container transition whitespace-nowrap"
          >
            <span class="material-symbols-outlined text-[18px]">add</span>
            新建演示
          </router-link>
          <select
            v-model="importDevice"
            class="hidden sm:block border border-outline-variant rounded-lg px-2 py-2 text-xs bg-white"
            aria-label="导入尺寸"
          >
            <option value="mobile">移动端</option>
            <option value="web">网页版</option>
          </select>
          <div class="relative">
            <button
              type="button"
              class="inline-flex items-center gap-1 px-3 sm:px-4 py-2 rounded-lg border border-outline-variant text-sm font-medium hover:bg-surface-container-high transition whitespace-nowrap disabled:opacity-50"
              :disabled="importing"
              @click="triggerImport"
            >
              <span class="material-symbols-outlined text-[18px]">upload</span>
              {{ importing ? '导入中…' : '导入 PPT' }}
            </button>
            <input
              ref="fileInputRef"
              type="file"
              accept=".pptx,application/vnd.openxmlformats-officedocument.presentationml.presentation"
              class="hidden"
              @change="onFileSelected"
            />
          </div>
        </div>
      </header>

      <p v-if="importError" class="mx-4 sm:mx-6 mt-3 text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
        {{ importError }}
      </p>

      <main class="flex-1 overflow-y-auto">
        <router-view />
      </main>
    </div>

    <ConfirmDialog
      :open="logoutOpen"
      title="退出登录"
      message="确定要退出当前账号吗？退出后将返回登录页。"
      confirm-text="退出登录"
      cancel-text="取消"
      @cancel="logoutOpen = false"
      @confirm="onLogoutConfirm"
    />

  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api/client'
import ConfirmDialog from './ConfirmDialog.vue'
import { useAuth } from '../composables/useAuth'

const route = useRoute()
const router = useRouter()
const { user, isAdmin, refreshProfile, performLogout } = useAuth()

const mobileNavOpen = ref(false)
const logoutOpen = ref(false)
const importing = ref(false)
const importError = ref('')
const fileInputRef = ref(null)
const importDevice = ref('mobile')
const quota = ref({ remaining: 5, total: 5 })
const quotaFailed = ref(false)

const displayName = computed(() => user.value?.username || user.value?.email || '用户')
const avatarLetter = computed(() => displayName.value.charAt(0).toUpperCase())
const tierLabel = computed(() => (user.value?.tier === 'pro' ? '专业版' : '免费版'))
const showUpgradeLink = computed(() => user.value?.tier !== 'pro')
const pageTitle = computed(() => route.meta.title || '我的工作台')
const iconNav = [
  { label: '首页', to: '/dashboard', match: '/dashboard', icon: 'home' },
  { label: '模板库', to: '/templates', match: '/templates', icon: 'dashboard_customize' },
]

const sectionNav = [
  { label: '首页', to: '/dashboard', match: '/dashboard', icon: 'home' },
  { label: '模板库', to: '/templates', match: '/templates', icon: 'dashboard_customize' },
]

function isActive(match) {
  return route.path.startsWith(match)
}

function openLogout() {
  mobileNavOpen.value = false
  logoutOpen.value = true
}

function onLogoutConfirm() {
  logoutOpen.value = false
  performLogout(router)
}

function triggerImport() {
  importError.value = ''
  fileInputRef.value?.click()
}

async function onFileSelected(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  if (!file.name.toLowerCase().endsWith('.pptx')) {
    importError.value = '请选择 .pptx 格式的 PowerPoint 文件'
    return
  }
  importing.value = true
  importError.value = ''
  try {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('device', importDevice.value)
    const project = await api.importProjectPptx(fd)
    router.push(`/editor/${project.id}`)
  } catch (err) {
    importError.value = err.message || '导入失败'
  } finally {
    importing.value = false
  }
}

onMounted(async () => {
  if (!user.value?.username) {
    await refreshProfile()
  }
  try {
    const q = await api.getQuota()
    quota.value = { remaining: q.quota_remaining, total: q.quota_total }
    quotaFailed.value = false
  } catch {
    quotaFailed.value = true
  }
})
</script>
