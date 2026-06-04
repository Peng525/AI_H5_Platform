<template>
  <div :class="tokens.page">
    <div :class="tokens.headerBar">
      <h2 :class="tokens.pageTitle">{{ structured.title }}</h2>
    </div>
    <div :class="tokens.cardsRow" :style="{ gridTemplateColumns: `repeat(${modules.length}, 1fr)` }">
      <ModuleCard v-for="(mod, i) in modules" :key="i" :mod="mod" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { slideTokens as tokens } from '../tokens.js'
import ModuleCard from './ModuleCard.vue'

const props = defineProps({ structured: { type: Object, required: true } })
const modules = computed(() => (props.structured.modules || []).slice(0, 4))
</script>
