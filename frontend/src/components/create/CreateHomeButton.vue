<template>
  <router-link
    to="/create/generate"
    class="inline-flex items-center justify-center w-9 h-9 rounded-lg border transition-colors shrink-0"
    :class="
      isHomeActive
        ? 'border-primary text-primary bg-primary/8'
        : 'border-outline-variant text-on-surface-variant hover:border-primary/40 hover:text-primary bg-white'
    "
    aria-label="主页"
    @click="onNavigateHome"
  >
    <span class="material-symbols-outlined text-[20px]">home</span>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  getLastGenerateResultPublicId,
  markReturnToResult,
  PENDING_RESULT_PUBLIC_ID,
} from '../../composables/useAiCreateDraft.js'

const route = useRoute()

const isHomeActive = computed(() => route.path === '/create/generate' || route.path === '/create/generate/')

function onNavigateHome() {
  if (route.name === 'ai-generate-result') {
    const publicId = String(route.params.publicId || '').trim()
    if (!publicId || publicId === PENDING_RESULT_PUBLIC_ID) return
    markReturnToResult(publicId)
    return
  }
  if (route.name === 'ai-generate-review') {
    const lastId = getLastGenerateResultPublicId()
    if (lastId) markReturnToResult(lastId)
  }
}
</script>
