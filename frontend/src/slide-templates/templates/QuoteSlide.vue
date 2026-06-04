<template>
  <div :class="tokens.page" class="items-center justify-center px-12">
    <p :class="tokens.quote">{{ quoteText }}</p>
    <p v-if="authorText" :class="tokens.quoteAuthor">{{ authorText }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { slideTokens as tokens } from '../tokens.js'

const props = defineProps({ structured: { type: Object, required: true } })
const quoteText = computed(
  () => props.structured.quote || props.structured.modules?.[0]?.quote || props.structured.headline || ''
)
const authorText = computed(
  () => props.structured.author || props.structured.modules?.[0]?.author || ''
)
</script>
