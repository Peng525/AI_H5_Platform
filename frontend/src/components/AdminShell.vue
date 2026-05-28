<template>
  <div class="min-h-screen bg-surface-container-low flex">
    <!-- 侧边栏 -->
    <aside class="w-56 bg-surface border-r border-outline-variant flex flex-col shrink-0">
      <div class="p-4 border-b border-outline-variant">
        <div class="flex items-center gap-2">
          <div class="w-9 h-9 rounded-lg bg-primary text-on-primary flex items-center justify-center font-bold text-sm">
            AD
          </div>
          <div>
            <p class="text-sm font-bold">管理控制台</p>
            <p class="text-[10px] text-on-surface-variant truncate max-w-[120px]">{{ user?.username }}</p>
          </div>
        </div>
      </div>

      <nav class="flex-1 p-3 space-y-1">
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm transition-colors"
          :class="isActive(item.match) ? 'bg-primary/10 text-primary font-medium' : 'text-on-surface-variant hover:bg-surface-container-high'"
        >
          <span class="material-symbols-outlined text-[20px]">{{ item.icon }}</span>
          {{ item.label }}
        </router-link>
      </nav>

      <div class="p-3 border-t border-outline-variant space-y-1">
        <router-link
          to="/templates"
          class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-on-surface-variant hover:bg-surface-container-high"
        >
          <span class="material-symbols-outlined text-[20px]">storefront</span>
          返回用户端
        </router-link>
        <button
          type="button"
          class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-red-600 hover:bg-red-50"
          @click="logoutOpen = true"
        >
          <span class="material-symbols-outlined text-[20px]">logout</span>
          退出登录
        </button>
      </div>
    </aside>

    <!-- 主内容 -->
    <div class="flex-1 flex flex-col min-w-0">
      <header class="h-14 border-b border-outline-variant bg-white flex items-center px-6 shrink-0">
        <h1 class="text-lg font-semibold">{{ title }}</h1>
      </header>
      <main class="flex-1 overflow-y-auto p-6">
        <slot />
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
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ConfirmDialog from './ConfirmDialog.vue'
import { useAuth } from '../composables/useAuth'

defineProps({
  title: { type: String, default: '仪表盘' },
})

const route = useRoute()
const router = useRouter()
const { user, performLogout } = useAuth()
const logoutOpen = ref(false)

const navItems = [
  { label: '数据仪表盘', to: '/admin', match: '/admin', icon: 'dashboard' },
  { label: '用户管理', to: '/admin/users', match: '/admin/users', icon: 'group' },
  { label: 'H5 模板', to: '/admin/templates', match: '/admin/templates', icon: 'dashboard_customize' },
  { label: '提示词模板', to: '/admin/prompts', match: '/admin/prompts', icon: 'psychology' },
  { label: '系统设置', to: '/settings', match: '/settings', icon: 'settings' },
]

function isActive(match) {
  if (match === '/admin') return route.path === '/admin'
  return route.path.startsWith(match)
}

function onLogoutConfirm() {
  logoutOpen.value = false
  performLogout(router)
}
</script>
