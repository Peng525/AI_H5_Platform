<template>
  <div :class="tokens.page" class="items-center justify-center px-12">
    <h1 :class="tokens.coverTitle">{{ structured.title || '谢谢' }}</h1>
    <p v-if="contact" class="text-lg text-primary mt-4">{{ contact }}</p>
    <div class="w-20 h-0.5 bg-primary mt-8" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { slideTokens as tokens } from '../tokens.js'

const props = defineProps({ structured: { type: Object, required: true } })
const contact = computed(
  () => props.structured.contact || props.structured.modules?.[0]?.contact || props.structured.subtitle || ''
)
</script>
