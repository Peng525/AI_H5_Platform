<template>
  <div :class="tokens.page">
    <div v-if="structured.title" :class="tokens.headerBar">
      <h2 :class="tokens.pageTitle">{{ structured.title }}</h2>
    </div>
    <div :class="tokens.splitRow">
      <div class="relative z-10 flex flex-col gap-4 pr-2">
        <h3 class="text-xl font-semibold text-on-surface">{{ left.title }}</h3>
        <p :class="tokens.body">{{ left.body }}</p>
      </div>
      <div :class="tokens.chartPlaceholder" aria-hidden="true">
        <span class="material-symbols-outlined text-[48px] text-on-surface-variant/60">analytics</span>
        <span class="text-sm text-on-surface-variant">图表占位</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { slideTokens as tokens } from '../tokens.js'

const props = defineProps({ structured: { type: Object, required: true } })
const left = computed(() => {
  const m = props.structured.modules?.[0]
  return {
    title: m?.title || props.structured.title || '说明',
    body: m?.body || props.structured.subtitle || '',
  }
})
</script>
