<template>
  <div class="h-full overflow-y-auto p-6 bg-surface-container-low">
    <article class="max-w-2xl mx-auto bg-white rounded-xl border border-outline-variant shadow-card p-6 space-y-6">
      <header v-if="basics.name || basics.email">
        <h1 class="text-2xl font-bold">{{ basics.name || '未命名' }}</h1>
        <p class="text-sm text-on-surface-variant mt-1">{{ contactLine }}</p>
        <p v-if="basics.summary" class="text-sm mt-3 leading-relaxed">{{ basics.summary }}</p>
      </header>

      <section v-if="experience.length">
        <h2 class="text-sm font-semibold text-primary mb-2">工作经历</h2>
        <div v-for="(job, i) in experience" :key="i" class="mb-4">
          <p class="font-medium text-sm">{{ job.company }} · {{ job.title }}</p>
          <p class="text-xs text-on-surface-variant">{{ job.period }}</p>
          <ul class="mt-1 list-disc list-inside text-sm space-y-1">
            <li v-for="(b, j) in job.bullets || []" :key="j">{{ b }}</li>
          </ul>
        </div>
      </section>

      <section v-if="education.length">
        <h2 class="text-sm font-semibold text-primary mb-2">教育背景</h2>
        <p v-for="(ed, i) in education" :key="i" class="text-sm">{{ ed.school }} — {{ ed.degree }} ({{ ed.period }})</p>
      </section>

      <section v-if="skills.length">
        <h2 class="text-sm font-semibold text-primary mb-2">技能</h2>
        <p class="text-sm">{{ skills.join(' · ') }}</p>
      </section>
    </article>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  structured: { type: Object, default: () => ({}) },
})

const basics = computed(() => props.structured?.basics || {})
const experience = computed(() => props.structured?.experience || [])
const education = computed(() => props.structured?.education || [])
const skills = computed(() => props.structured?.skills || [])
const contactLine = computed(() => [basics.value.phone, basics.value.email].filter(Boolean).join(' · '))
</script>
