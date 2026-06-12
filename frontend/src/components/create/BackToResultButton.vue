<template>
  <button
    v-if="returnPath"
    type="button"
    class="text-sm text-on-surface-variant hover:text-primary inline-flex items-center gap-1 shrink-0 whitespace-nowrap"
    @click="router.push(returnPath)"
  >
    <span class="material-symbols-outlined text-[18px]">arrow_back</span>
    返回生成结果
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { getReturnToResultPath } from '../../composables/useAiCreateDraft.js'

const router = useRouter()

const returnPath = computed(() => getReturnToResultPath())
</script>
