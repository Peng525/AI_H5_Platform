<template>
  <button
    v-if="returnPath"
    type="button"
    class="px-2.5 py-1.5 rounded-lg border border-outline-variant bg-white text-sm font-medium text-on-surface-variant hover:border-primary/40 hover:text-primary inline-flex items-center gap-1 shrink-0 whitespace-nowrap transition-colors"
    @click="router.push(returnPath)"
  >
    <span class="material-symbols-outlined text-[18px]">arrow_back</span>
    返回生成结果
  </button>
</template>

<script setup>
import { computed, onActivated, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getReturnToResultPath } from '../../composables/useAiCreateDraft.js'

const router = useRouter()
const route = useRoute()

const navigationEpoch = ref(0)

function refreshReturnPath() {
  navigationEpoch.value += 1
}

watch(() => route.fullPath, refreshReturnPath)
onActivated(refreshReturnPath)

const returnPath = computed(() => {
  navigationEpoch.value
  return getReturnToResultPath()
})
</script>
