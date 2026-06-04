<template>
  <div :class="tokens.page">
    <div :class="tokens.headerBar">
      <div class="w-1 h-12 bg-primary rounded absolute left-8 top-1/2 -translate-y-1/2" />
      <h2 :class="tokens.pageTitle" class="pl-4">{{ structured.title || '章节' }}</h2>
      <p v-if="structured.headline" :class="tokens.headline" class="mt-3 pl-4">{{ structured.headline }}</p>
    </div>
    <div class="flex-1 px-8 py-6 flex items-start">
      <p :class="tokens.body">{{ bodyText }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { slideTokens as tokens } from '../tokens.js'

const props = defineProps({ structured: { type: Object, required: true } })
const bodyText = computed(
  () => props.structured.modules?.[0]?.body || props.structured.subtitle || ''
)
</script>
