<template>
  <header
    class="min-h-14 sm:h-16 border-b border-outline-variant bg-surface flex items-center justify-between gap-2 px-3 sm:px-4 md:px-6 shrink-0 z-50"
  >
    <div class="flex items-center gap-2 sm:gap-3 md:gap-4 min-w-0 flex-1">
      <router-link
        :to="logoTo"
        class="text-sm sm:text-base md:text-lg font-bold text-primary truncate min-w-0"
        title="AI智能H5演示平台"
      >
        <span class="sm:hidden">AI H5</span>
        <span class="hidden sm:inline">AI智能H5演示平台</span>
      </router-link>
      <span class="hidden lg:block h-5 w-px bg-outline-variant" />
      <nav class="hidden lg:flex items-center gap-1 text-sm">
        <router-link
          v-for="link in navLinks"
          :key="link.to"
          :to="link.to"
          class="px-3 py-1.5 rounded-lg transition-colors"
          :class="isActive(link.match) ? 'bg-primary/10 text-primary font-medium' : 'text-on-surface-variant hover:bg-surface-container-high'"
          :aria-current="isActive(link.match) ? 'page' : undefined"
        >
          {{ link.label }}
        </router-link>
      </nav>
    </div>

    <div class="flex items-center gap-1.5 sm:gap-2 shrink-0">
      <span
        v-if="showQuotaBar"
        class="hidden md:inline-flex items-center gap-1 text-xs text-on-surface-variant bg-surface-container-low px-2 py-1 rounded-full whitespace-nowrap"
        :title="quotaFailed ? '配额加载失败' : undefined"
      >
        配额 {{ quotaFailed ? '—' : `${quota.remaining}/${quota.total}` }}
      </span>
      <router-link
        v-if="showUpgradeLink"
        to="/upgrade"
        class="hidden sm:inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium bg-amber-50 text-amber-800 border border-amber-200"
      >
        升级会员
      </router-link>

      <slot name="actions" />

      <button
        v-if="projectId"
        type="button"
        class="px-2 py-1.5 sm:px-3 sm:py-2 rounded-lg border border-outline-variant text-xs sm:text-sm hover:bg-surface-container-high whitespace-nowrap"
        @click="goPreview"
      >
        预览
      </button>
      <router-link
        v-if="projectId && !hidePublish"
        :to="`/publish/${projectId}`"
        class="px-2 py-1.5 sm:px-3 sm:py-2 rounded-lg bg-primary text-on-primary text-xs sm:text-sm font-medium shadow-card whitespace-nowrap"
      >
        发布分享
      </router-link>

      <div ref="menuRef" class="relative">
        <button
          type="button"
          class="flex items-center gap-1 sm:gap-1.5 max-w-[5.5rem] sm:max-w-[9.5rem] md:max-w-[12rem] pl-1 pr-1.5 sm:pr-2 py-1 rounded-lg hover:bg-surface-container-high text-sm min-w-0"
          :title="displayName"
          @click="menuOpen = !menuOpen"
        >
          <span class="w-7 h-7 shrink-0 rounded-full bg-primary text-on-primary flex items-center justify-center text-xs font-bold">
            {{ avatarLetter }}
          </span>
          <span class="truncate text-xs sm:text-sm text-on-surface font-medium min-w-0 hidden min-[420px]:inline">{{ displayName }}</span>
          <span
            class="shrink-0 text-[10px] text-on-surface-variant transition-transform"
            :class="menuOpen ? 'rotate-180' : ''"
            aria-hidden="true"
          >▼</span>
        </button>
        <div
          v-if="menuOpen"
          class="absolute right-0 top-full mt-1 w-48 sm:w-52 bg-white border border-outline-variant rounded-lg shadow-lg py-1 z-50"
        >
          <p v-if="showQuotaBar" class="px-3 py-2 text-xs text-on-surface-variant border-b border-outline-variant md:hidden">
            配额 {{ quotaFailed ? '—' : `${quota.remaining}/${quota.total}` }}
          </p>
          <p class="px-3 py-2 text-xs text-on-surface-variant border-b border-outline-variant truncate">
            {{ displayName }}
          </p>
          <router-link
            v-if="navMode === 'user'"
            to="/dashboard"
            class="block px-3 py-2 text-sm hover:bg-surface-container-low"
            @click="menuOpen = false"
          >
            我的工作台
          </router-link>
          <router-link
            to="/help"
            class="block px-3 py-2 text-sm hover:bg-surface-container-low"
            @click="menuOpen = false"
          >
            使用帮助
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

    <ConfirmDialog
      :open="logoutOpen"
      title="退出登录"
      message="确定要退出当前账号吗？退出后将返回登录页。"
      confirm-text="退出登录"
      cancel-text="取消"
      @cancel="logoutOpen = false"
      @confirm="onLogoutConfirm"
    />
  </header>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api/client'
import ConfirmDialog from './ConfirmDialog.vue'
import { useAuth } from '../composables/useAuth'
import { flushCanvasSave } from '../composables/useEditorCanvasSave'

const props = defineProps({
  projectId: { type: [String, Number], default: null },
  showQuota: { type: Boolean, default: true },
  hidePublish: { type: Boolean, default: false },
  /** user = 用户端导航；admin = 管理/模板编辑场景 */
  navMode: { type: String, default: 'user', validator: (v) => ['user', 'admin'].includes(v) },
})

const route = useRoute()
const router = useRouter()
const { user, isAdmin, refreshProfile, performLogout } = useAuth()
const menuOpen = ref(false)
const logoutOpen = ref(false)
const menuRef = ref(null)
const quota = ref({ remaining: 5, total: 5 })
const quotaFailed = ref(false)

const logoTo = computed(() => (props.navMode === 'admin' ? '/admin' : '/dashboard'))

const showQuotaBar = computed(() => props.showQuota && props.navMode !== 'admin')

const showUpgradeLink = computed(() => props.navMode !== 'admin' && user.value?.tier !== 'pro')

const navLinks = computed(() => {
  if (props.navMode === 'admin') {
    return [{ label: '管理控制台', to: '/admin', match: '/admin' }]
  }
  if (isAdmin.value) {
    return [{ label: '管理控制台', to: '/admin', match: '/admin' }]
  }
  return []
})

const displayName = computed(() => user.value?.username || user.value?.email || '用户')

const avatarLetter = computed(() => displayName.value.charAt(0).toUpperCase())

function isActive(match) {
  return route.path.startsWith(match)
}

function openLogout() {
  menuOpen.value = false
  logoutOpen.value = true
}

async function goPreview() {
  await flushCanvasSave()
  router.push({
    path: `/preview/${props.projectId}`,
    query: { returnTo: route.fullPath },
  })
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
  try {
    const q = await api.getQuota()
    quota.value = { remaining: q.quota_remaining, total: q.quota_total }
    quotaFailed.value = false
  } catch {
    quotaFailed.value = true
  }
})

onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>
