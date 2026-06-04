<template>
  <div :class="muted ? tokens.cardMuted : tokens.card">
    <span v-if="mod.icon" class="material-symbols-outlined text-[28px] text-primary">{{ mod.icon }}</span>
    <p v-if="mod.title" :class="tokens.cardTitle">{{ mod.title }}</p>
    <p v-if="mod.body" :class="tokens.cardBody">{{ mod.body }}</p>
    <p v-if="mod.emphasis" class="text-sm font-semibold text-primary">{{ mod.emphasis }}</p>
  </div>
</template>

<script setup>
import { slideTokens as tokens } from '../tokens.js'

defineProps({
  mod: { type: Object, default: () => ({}) },
  muted: { type: Boolean, default: false },
})
</script>
