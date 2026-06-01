<template>
  <div class="h-screen bg-surface-container-low flex overflow-hidden">
    <!-- 侧边栏：固定视口高度，底部操作始终贴底 -->
    <aside class="w-56 h-full bg-surface border-r border-outline-variant flex flex-col shrink-0">
      <div class="p-4 border-b border-outline-variant shrink-0">
        <div class="flex items-center gap-2">
          <div class="w-9 h-9 rounded-lg bg-primary text-on-primary flex items-center justify-center font-bold text-sm">
            AD
          </div>
          <p class="text-sm font-bold">管理控制台</p>
        </div>
      </div>

      <nav class="flex-1 min-h-0 overflow-y-auto p-3 space-y-1">
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
    </aside>

    <!-- 主内容 -->
    <div class="flex-1 flex flex-col min-h-0 min-w-0">
      <header class="h-14 border-b border-outline-variant bg-white flex items-center justify-between px-6 shrink-0">
        <h1 class="text-lg font-semibold">{{ title }}</h1>
        <div ref="menuRef" class="relative">
          <button
            type="button"
            class="flex items-center gap-1.5 max-w-[12rem] pl-1 pr-2 py-1 rounded-lg hover:bg-surface-container-high text-sm min-w-0"
            :title="displayName"
            @click="menuOpen = !menuOpen"
          >
            <span class="w-7 h-7 shrink-0 rounded-full bg-primary text-on-primary flex items-center justify-center text-xs font-bold">
              {{ avatarLetter }}
            </span>
            <span class="truncate text-sm text-on-surface font-medium min-w-0">{{ displayName }}</span>
            <span
              class="shrink-0 text-[10px] text-on-surface-variant transition-transform"
              :class="menuOpen ? 'rotate-180' : ''"
              aria-hidden="true"
            >▼</span>
          </button>
          <div
            v-if="menuOpen"
            class="absolute right-0 top-full mt-1 w-52 bg-white border border-outline-variant rounded-lg shadow-lg py-1 z-50"
          >
            <p class="px-3 py-2 text-xs text-on-surface-variant border-b border-outline-variant truncate">
              {{ displayName }}
            </p>
            <router-link
              to="/settings"
              class="block px-3 py-2 text-sm hover:bg-surface-container-low"
              @click="menuOpen = false"
            >
              系统设置
            </router-link>
            <button
              type="button"
              class="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50"
              @click="openLogout"
            >
              退出登录
            </button>
          </div>
        </div>
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
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ConfirmDialog from './ConfirmDialog.vue'
import { useAuth } from '../composables/useAuth'

defineProps({
  title: { type: String, default: '仪表盘' },
})

const route = useRoute()
const router = useRouter()
const { user, refreshProfile, performLogout } = useAuth()
const logoutOpen = ref(false)
const menuOpen = ref(false)
const menuRef = ref(null)

const displayName = computed(() => user.value?.username || user.value?.email || '管理员')
const avatarLetter = computed(() => displayName.value.charAt(0).toUpperCase())

const navItems = [
  { label: '数据仪表盘', to: '/admin', match: '/admin', icon: 'dashboard' },
  { label: '用户管理', to: '/admin/users', match: '/admin/users', icon: 'group' },
  { label: 'H5 模板', to: '/admin/templates', match: '/admin/templates', icon: 'dashboard_customize' },
  { label: '版式管理', to: '/admin/layouts', match: '/admin/layouts', icon: 'view_quilt' },
  { label: '文稿提示词', to: '/admin/prompts', match: '/admin/prompts', icon: 'description' },
  { label: '生图提示词', to: '/admin/image-prompts', match: '/admin/image-prompts', icon: 'psychology' },
  { label: '系统设置', to: '/settings', match: '/settings', icon: 'settings' },
]

function isActive(match) {
  if (match === '/admin') return route.path === '/admin'
  return route.path.startsWith(match)
}

function openLogout() {
  menuOpen.value = false
  logoutOpen.value = true
}

function onLogoutConfirm() {
  logoutOpen.value = false
  performLogout(router)
}

function onClickOutside(e) {
  if (menuRef.value && !menuRef.value.contains(e.target)) menuOpen.value = false
}

onMounted(async () => {
  document.addEventListener('click', onClickOutside)
  if (!user.value?.username) {
    await refreshProfile()
  }
})

onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>
