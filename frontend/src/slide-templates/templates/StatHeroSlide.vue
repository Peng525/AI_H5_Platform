<template>
  <div :class="tokens.page" class="items-center justify-center text-center px-12">
    <h2 v-if="structured.title" class="text-xl font-semibold text-on-surface mb-6">{{ structured.title }}</h2>
    <p :class="tokens.statNumber">{{ stat }}</p>
    <p :class="tokens.statDesc">{{ desc }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { slideTokens as tokens } from '../tokens.js'

const props = defineProps({ structured: { type: Object, required: true } })
const stat = computed(() => props.structured.modules?.[0]?.stat || props.structured.headline || '—')
const desc = computed(
  () => props.structured.modules?.[0]?.desc || props.structured.modules?.[0]?.body || props.structured.subtitle || ''
)
</script>
