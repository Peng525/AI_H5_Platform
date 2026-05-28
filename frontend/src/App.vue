<template>
  <div class="min-h-screen flex flex-col">
    <header
      v-if="!isShare"
      class="h-16 border-b border-outline-variant bg-surface flex items-center justify-between px-6 md:px-10 shrink-0"
    >
      <div class="flex items-center gap-4">
        <router-link to="/" class="text-lg font-bold text-primary">AI智能H5演示平台</router-link>
        <nav class="hidden md:flex gap-4 text-sm text-on-surface-variant">
          <router-link to="/" class="hover:text-primary" active-class="text-primary font-semibold"
            >项目</router-link
          >
          <router-link to="/create" class="hover:text-primary" active-class="text-primary font-semibold"
            >创建</router-link
          >
          <router-link to="/settings" class="hover:text-primary" active-class="text-primary font-semibold"
            >设置</router-link
          >
        </nav>
      </div>
    </header>
    <main class="flex-1">
      <router-view />
    </main>
    <footer
      v-if="!isShare"
      class="text-center text-xs text-on-surface-variant py-3 border-t border-outline-variant"
    >
      智能 H5 演示平台 · 本地 / Docker 部署 · 大模型通道 auto
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isShare = computed(() => route.name === 'share')
</script>
