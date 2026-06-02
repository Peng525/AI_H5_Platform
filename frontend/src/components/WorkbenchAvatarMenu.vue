<template>
  <div ref="menuRef" class="relative">
    <button
      type="button"
      class="w-10 h-10 rounded-full bg-primary text-on-primary flex items-center justify-center text-xs font-bold hover:ring-2 hover:ring-white/30 transition"
      :title="displayName"
      @click="menuOpen = !menuOpen"
    >
      {{ avatarLetter }}
    </button>
    <div
      v-if="menuOpen"
      class="absolute left-full bottom-0 ml-2 w-44 bg-white border border-outline-variant rounded-lg shadow-lg py-1 z-50"
    >
      <p class="px-3 py-2 text-xs text-on-surface-variant border-b border-outline-variant truncate">
        {{ displayName }}
      </p>
      <router-link
        to="/help"
        class="block px-3 py-2 text-sm hover:bg-surface-container-low"
        @click="menuOpen = false"
      >
        使用帮助
      </router-link>
      <router-link
        v-if="showUpgradeLink"
        to="/upgrade"
        class="block px-3 py-2 text-sm text-amber-800 hover:bg-amber-50"
        @click="menuOpen = false"
      >
        升级会员
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
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import ConfirmDialog from './ConfirmDialog.vue'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { user, refreshProfile, performLogout } = useAuth()
const menuOpen = ref(false)
const logoutOpen = ref(false)
const menuRef = ref(null)

const displayName = computed(() => user.value?.username || user.value?.email || '用户')
const avatarLetter = computed(() => displayName.value.charAt(0).toUpperCase())
const showUpgradeLink = computed(() => user.value?.tier !== 'pro')

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
  if (!user.value?.username) await refreshProfile()
})

onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>
