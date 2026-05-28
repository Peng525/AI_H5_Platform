<template>
  <header
    class="h-16 border-b border-outline-variant bg-surface flex items-center justify-between px-4 md:px-6 shrink-0 z-50"
  >
    <div class="flex items-center gap-3 md:gap-4 min-w-0">
      <router-link to="/templates" class="text-base md:text-lg font-bold text-primary shrink-0">
        AI智能H5演示平台
      </router-link>
      <span class="hidden lg:block h-5 w-px bg-outline-variant" />
      <nav class="hidden lg:flex items-center gap-1 text-sm">
        <router-link
          v-for="link in navLinks"
          :key="link.to"
          :to="link.to"
          class="px-3 py-1.5 rounded-lg transition-colors"
          :class="isActive(link.match) ? 'bg-primary/10 text-primary font-medium' : 'text-on-surface-variant hover:bg-surface-container-high'"
        >
          {{ link.label }}
        </router-link>
      </nav>
      <span v-if="pageTitle" class="hidden md:block h-5 w-px bg-outline-variant" />
      <span v-if="pageTitle" class="truncate text-sm font-medium text-on-surface max-w-[140px] md:max-w-xs">
        {{ pageTitle }}
      </span>
    </div>

    <div class="flex items-center gap-2 shrink-0">
      <span
        v-if="showQuota"
        class="hidden sm:inline-flex items-center gap-1 text-xs text-on-surface-variant bg-surface-container-low px-2 py-1 rounded-full"
      >
        配额 {{ quota.remaining }}/{{ quota.total }}
      </span>
      <router-link
        v-if="user?.tier !== 'pro'"
        to="/upgrade"
        class="hidden sm:inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium bg-amber-50 text-amber-800 border border-amber-200"
      >
        <span class="material-symbols-outlined text-[14px]">stars</span>
        升级
      </router-link>

      <slot name="actions" />

      <router-link
        v-if="projectId"
        :to="`/preview/${projectId}`"
        class="px-3 py-2 rounded-lg border border-outline-variant text-sm hover:bg-surface-container-high"
      >
        预览
      </router-link>
      <router-link
        v-if="projectId"
        :to="`/publish/${projectId}`"
        class="px-3 py-2 rounded-lg bg-primary text-on-primary text-sm font-medium shadow-card flex items-center gap-1"
      >
        <span class="material-symbols-outlined text-[18px]">ios_share</span>
        <span class="hidden sm:inline">导出/分享</span>
      </router-link>

      <div ref="menuRef" class="relative">
        <button
          class="flex items-center gap-1 px-2 py-1.5 rounded-lg hover:bg-surface-container-high text-sm"
          @click="menuOpen = !menuOpen"
        >
          <span class="w-7 h-7 rounded-full bg-primary text-on-primary flex items-center justify-center text-xs font-bold">
            {{ avatarLetter }}
          </span>
          <span class="material-symbols-outlined text-[18px] text-on-surface-variant hidden sm:block">expand_more</span>
        </button>
        <div
          v-if="menuOpen"
          class="absolute right-0 top-full mt-1 w-44 bg-white border border-outline-variant rounded-lg shadow-lg py-1 z-50"
        >
          <p class="px-3 py-2 text-xs text-on-surface-variant border-b border-outline-variant truncate">
            {{ user?.username || user?.email || '用户' }}
          </p>
          <router-link
            to="/dashboard"
            class="block px-3 py-2 text-sm hover:bg-surface-container-low lg:hidden"
            @click="menuOpen = false"
          >
            我的项目
          </router-link>
          <router-link
            v-if="isAdmin"
            to="/admin"
            class="block px-3 py-2 text-sm hover:bg-surface-container-low lg:hidden"
            @click="menuOpen = false"
          >
            管理控制台
          </router-link>
          <button
            class="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50"
            @click="openLogout"
          >
            退出登录
          </button>
        </div>
      </div>
    </div>

    <LogoutDialog
      :open="logoutOpen"
      @cancel="logoutOpen = false"
      @confirm="onLogoutConfirm"
    />
  </header>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api/client'
import LogoutDialog from './LogoutDialog.vue'
import { useAuth } from '../composables/useAuth'

defineProps({
  pageTitle: { type: String, default: '' },
  projectId: { type: [String, Number], default: null },
  showQuota: { type: Boolean, default: true },
})

const route = useRoute()
const router = useRouter()
const { user, logout, isAdmin, refreshProfile, performLogout } = useAuth()
const menuOpen = ref(false)
const logoutOpen = ref(false)
const menuRef = ref(null)
const quota = ref({ remaining: 5, total: 5 })

const navLinks = computed(() => {
  const links = [
    { label: '探索模板', to: '/templates', match: '/templates' },
    { label: '我的项目', to: '/dashboard', match: '/dashboard' },
  ]
  if (isAdmin.value) {
    links.push({ label: '管理控制台', to: '/admin', match: '/admin' })
  }
  return links
})

const avatarLetter = computed(() => {
  const name = user.value?.username || user.value?.email || 'U'
  return name.charAt(0).toUpperCase()
})

function isActive(match) {
  return route.path.startsWith(match)
}

function openLogout() {
  menuOpen.value = false
  logoutOpen.value = true
}

function onLogoutConfirm(keepRemember) {
  logoutOpen.value = false
  performLogout(router, keepRemember)
}

function onClickOutside(e) {
  if (menuRef.value && !menuRef.value.contains(e.target)) menuOpen.value = false
}

onMounted(async () => {
  document.addEventListener('click', onClickOutside)
  await refreshProfile()
  try {
    const q = await api.getQuota(user.value?.user_id)
    quota.value = { remaining: q.quota_remaining, total: q.quota_total }
  } catch {
    /* 忽略配额加载失败 */
  }
})

onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>
