<template>
  <div :class="tokens.page">
    <div :class="tokens.headerBar" class="text-center">
      <h2 :class="tokens.pageTitle">{{ structured.title || '流程' }}</h2>
    </div>
    <div class="flex-1 grid grid-cols-3 gap-6 px-8 py-8 items-start">
      <div v-for="(step, i) in steps" :key="i" class="text-center space-y-3">
        <div :class="tokens.stepCircle">{{ i + 1 }}</div>
        <p class="text-sm font-medium text-on-surface">{{ step.title || step.body }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { slideTokens as tokens } from '../tokens.js'

const props = defineProps({ structured: { type: Object, required: true } })
const steps = computed(() => {
  const s = [...(props.structured.modules || [])]
  while (s.length < 3) s.push({ title: `步骤 ${s.length + 1}` })
  return s.slice(0, 3)
})
</script>
