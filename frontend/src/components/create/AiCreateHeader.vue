<template>
  <header class="h-14 border-b border-white/60 bg-white/70 backdrop-blur flex items-center justify-between px-4 sm:px-8 shrink-0 gap-3">
    <!-- entry: 左上导航 -->
    <div v-if="variant === 'entry'" class="flex items-center shrink-0 min-w-0">
      <nav class="flex flex-wrap items-center gap-1 text-sm">
        <router-link
          to="/create/generate"
          class="px-2.5 py-1 rounded-lg transition-colors whitespace-nowrap"
          :class="isActive('/create/generate') ? 'text-primary font-medium bg-primary/10' : 'text-on-surface-variant hover:text-primary'"
        >
          主页
        </router-link>
        <router-link
          to="/dashboard"
          class="px-2.5 py-1 rounded-lg transition-colors whitespace-nowrap"
          :class="isActive('/dashboard') ? 'text-primary font-medium bg-primary/10' : 'text-on-surface-variant hover:text-primary'"
        >
          我的工作台
        </router-link>
      </nav>
    </div>

    <!-- step: 上一步 / 返回 -->
    <div v-else class="flex items-center gap-2 min-w-0 shrink-0">
      <button
        v-if="showBack"
        type="button"
        class="inline-flex items-center gap-1 text-sm text-on-surface-variant hover:text-primary shrink-0"
        @click="$emit('back')"
      >
        <span class="material-symbols-outlined text-[18px]">arrow_back</span>
        {{ backLabel }}
      </button>
      <router-link
        v-else
        to="/dashboard"
        class="inline-flex items-center gap-1 text-sm text-on-surface-variant hover:text-primary shrink-0"
      >
        <span class="material-symbols-outlined text-[18px]">arrow_back</span>
        我的工作台
      </router-link>
    </div>

    <!-- entry: 居中欢迎语 -->
    <h1
      v-if="variant === 'entry'"
      class="hidden sm:block flex-1 text-center text-sm sm:text-base font-semibold text-on-surface truncate px-2"
    >
      欢迎来到 AI H5 平台
    </h1>

    <div v-else-if="variant === 'step'" class="flex-1 hidden sm:block" />

    <!-- 右上用户菜单（entry / step 共用） -->
    <UserMenu v-if="variant === 'entry' || variant === 'step'" />
    <div v-else class="w-8 shrink-0" />
  </header>
</template>

<script setup>
import { useRoute } from 'vue-router'
import UserMenu from './UserMenu.vue'

defineProps({
  variant: { type: String, default: 'step', validator: (v) => ['entry', 'step'].includes(v) },
  showBack: { type: Boolean, default: false },
  backLabel: { type: String, default: '上一步' },
})

defineEmits(['back'])

const route = useRoute()

function isActive(prefix) {
  return route.path.startsWith(prefix)
}
</script>
