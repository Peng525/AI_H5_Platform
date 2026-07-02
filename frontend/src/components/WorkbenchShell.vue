<template>
  <div class="h-screen bg-surface-container-low flex overflow-hidden">
    <!-- Dark icon rail -->
    <aside
      class="hidden sm:flex w-16 h-full bg-[#1e293b] flex-col items-center py-3 shrink-0"
    >
      <router-link
        v-for="item in iconNav"
        :key="item.to"
        :to="item.to"
        class="w-12 h-12 rounded-lg flex items-center justify-center transition-colors mb-2"
        :class="isActive(item.match) ? 'bg-white/15 text-white' : 'text-slate-400 hover:bg-white/10 hover:text-white'"
        :title="item.label"
      >
        <span class="material-symbols-outlined text-[26px]">{{ item.icon }}</span>
      </router-link>
      <div class="flex-1" />
      <WorkbenchAvatarMenu />
    </aside>

    <!-- Secondary workspace panel -->
    <aside
      class="w-52 h-full bg-surface border-r border-outline-variant flex flex-col shrink-0"
      :class="mobileNavOpen ? 'fixed inset-y-0 left-0 z-40 sm:relative sm:z-auto flex' : 'hidden sm:flex'"
    >
      <div class="p-4 border-b border-outline-variant shrink-0">
        <p class="text-base font-semibold truncate" :title="displayName">{{ displayName }}</p>
        <p class="text-xs text-on-surface-variant truncate mt-0.5">
          {{ tierLabel }} · 配额 {{ quotaFailed ? '—' : `${quota.remaining}/${quota.total}` }}
        </p>
      </div>

      <div v-if="showUpgradeLink" class="px-3 pt-3 shrink-0">
        <router-link
          to="/upgrade"
          class="block text-center text-xs font-medium py-2 px-3 rounded-lg border border-violet-300/60 bg-violet-50 text-violet-800 hover:bg-violet-100 transition"
          @click="mobileNavOpen = false"
        >
          升级获取更多 AI 配额
        </router-link>
      </div>

      <nav class="flex-1 min-h-0 overflow-y-auto p-3 space-y-1">
        <template v-if="isDashboard">
          <button
            type="button"
            class="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm bg-primary text-on-primary font-medium"
            @click="goDashboard"
          >
            <span class="material-symbols-outlined text-[20px]">folder</span>
            全部项目
          </button>
        </template>
        <template v-else-if="isTemplates">
          <button
            type="button"
            class="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm bg-primary text-on-primary font-medium"
            @click="goTemplates"
          >
            <span class="material-symbols-outlined text-[20px]">dashboard_customize</span>
            探索模板
          </button>
        </template>
        <template v-else-if="isResumes">
          <button
            type="button"
            class="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm bg-primary text-on-primary font-medium"
            @click="goResumes"
          >
            <span class="material-symbols-outlined text-[20px]">description</span>
            全部简历
          </button>
        </template>
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

      <div class="p-3 border-t border-outline-variant shrink-0 sm:hidden space-y-1">
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
          @click="openMobileLogout"
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

    <!-- Main column -->
    <div class="flex-1 flex flex-col min-h-0 min-w-0 bg-white">
      <header class="h-14 border-b border-outline-variant bg-white flex items-center px-4 shrink-0 sm:hidden">
        <button
          type="button"
          class="w-9 h-9 rounded-lg hover:bg-surface-container-high flex items-center justify-center shrink-0"
          aria-label="打开菜单"
          @click="mobileNavOpen = true"
        >
          <span class="material-symbols-outlined text-[22px]">menu</span>
        </button>
      </header>

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
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ConfirmDialog from './ConfirmDialog.vue'
import WorkbenchAvatarMenu from './WorkbenchAvatarMenu.vue'
import { useAuth } from '../composables/useAuth'
import { useQuota } from '../composables/useQuota'

const route = useRoute()
const router = useRouter()
const { user, isAdmin, performLogout } = useAuth()
const { quota, quotaFailed, tierLabel } = useQuota()

const mobileNavOpen = ref(false)
const logoutOpen = ref(false)
const displayName = computed(() => user.value?.username || user.value?.email || '用户')
const showUpgradeLink = computed(() => user.value?.tier !== 'pro')
const isDashboard = computed(() => route.path.startsWith('/dashboard') && !route.path.startsWith('/dashboard/resumes'))
const isTemplates = computed(() => route.path.startsWith('/templates'))
const isResumes = computed(() => route.path.startsWith('/dashboard/resumes'))

const iconNav = [
  { label: '主页', to: '/create/generate', match: '/create/generate', icon: 'home' },
  { label: '工作台', to: '/dashboard', match: '/dashboard', icon: 'dashboard' },
  { label: '模板库', to: '/templates', match: '/templates', icon: 'dashboard_customize' },
  { label: '个人简历', to: '/dashboard/resumes', match: '/dashboard/resumes', icon: 'description' },
]

function isActive(match) {
  return route.path.startsWith(match)
}

function goDashboard() {
  mobileNavOpen.value = false
  if (!isDashboard.value) router.push('/dashboard')
}

function goTemplates() {
  mobileNavOpen.value = false
  if (!isTemplates.value) router.push('/templates')
}

function goResumes() {
  mobileNavOpen.value = false
  if (!isResumes.value) router.push('/dashboard/resumes')
}

function openMobileLogout() {
  mobileNavOpen.value = false
  logoutOpen.value = true
}

function onLogoutConfirm() {
  logoutOpen.value = false
  performLogout(router)
}
</script>
