<template>
  <div class="flex items-center gap-2 shrink-0">
    <span
      class="hidden sm:block text-xs text-on-surface-variant whitespace-nowrap"
      :title="quotaFailed ? '配额加载失败' : undefined"
    >
      {{ tierLabel }} · 配额 {{ quotaText }}
    </span>
    <div ref="menuRef" class="relative">
      <button
        type="button"
        class="flex items-center gap-1.5 pl-1 pr-2 py-1 rounded-lg hover:bg-white/80 text-sm min-w-0"
        :title="displayName"
        @click="menuOpen = !menuOpen"
      >
        <span class="w-8 h-8 shrink-0 rounded-full bg-primary text-on-primary flex items-center justify-center text-xs font-bold">
          {{ avatarLetter }}
        </span>
        <span class="truncate text-xs sm:text-sm text-on-surface font-medium max-w-[6rem] sm:max-w-[8rem] hidden min-[420px]:inline">
          {{ displayName }}
        </span>
        <span class="material-symbols-outlined text-[16px] text-on-surface-variant">expand_more</span>
      </button>
      <div
        v-if="menuOpen"
        class="absolute right-0 top-full mt-1 w-44 bg-white border border-outline-variant rounded-lg shadow-lg py-1 z-50"
      >
        <p class="px-3 py-2 text-xs text-on-surface-variant border-b border-outline-variant truncate sm:hidden">
          {{ displayName }}
        </p>
        <p class="px-3 py-2 text-xs text-on-surface-variant border-b border-outline-variant sm:hidden">
          {{ tierLabel }} · 配额 {{ quotaText }}
        </p>
        <router-link
          to="/help"
          class="block px-3 py-2 text-sm hover:bg-surface-container-low"
          @click="menuOpen = false"
        >
          使用帮助
        </router-link>
        <button
          type="button"
          class="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50"
          @click="openLogout"
        >
          退出登录
        </button>
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
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import ConfirmDialog from '../ConfirmDialog.vue'
import { useAuth } from '../../composables/useAuth'
import { useQuota } from '../../composables/useQuota'

const router = useRouter()
const { user, performLogout } = useAuth()
const { tierLabel, quotaText, quotaFailed } = useQuota()
const menuOpen = ref(false)
const logoutOpen = ref(false)
const menuRef = ref(null)

const displayName = computed(() => user.value?.username || user.value?.email || '用户')
const avatarLetter = computed(() => displayName.value.charAt(0).toUpperCase())

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

onMounted(() => {
  document.addEventListener('click', onClickOutside)
})

onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>
