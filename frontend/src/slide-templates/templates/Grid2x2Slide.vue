<template>
  <div :class="tokens.page">
    <div :class="tokens.headerBar">
      <h2 :class="tokens.pageTitle">{{ structured.title }}</h2>
      <p v-if="structured.headline" :class="tokens.headline" class="mt-2">{{ structured.headline }}</p>
    </div>
    <div :class="tokens.grid2">
      <ModuleCard v-for="(mod, i) in modules" :key="i" :mod="mod" muted />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { slideTokens as tokens } from '../tokens.js'
import ModuleCard from './ModuleCard.vue'

const props = defineProps({ structured: { type: Object, required: true } })
const modules = computed(() => {
  const m = [...(props.structured.modules || [])]
  while (m.length < 4) m.push({ title: '模块', body: '内容', icon: 'circle' })
  return m.slice(0, 4)
})
</script>
