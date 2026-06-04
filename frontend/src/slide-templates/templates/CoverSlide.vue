<template>
  <div :class="tokens.page" class="items-center justify-center px-12">
    <div class="w-24 h-1 bg-primary rounded mb-8" />
    <h1 :class="tokens.coverTitle">{{ structured.title || '演示标题' }}</h1>
    <p v-if="structured.subtitle" :class="tokens.coverSubtitle">{{ structured.subtitle }}</p>
  </div>
</template>

<script setup>
import { slideTokens as tokens } from '../tokens.js'
defineProps({ structured: { type: Object, required: true } })
</script>
