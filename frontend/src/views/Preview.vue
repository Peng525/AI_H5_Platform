<template>
  <div class="fixed inset-0 bg-black z-50 flex flex-col" tabindex="0" @keydown="onKey">
    <div v-if="loading" class="text-white m-auto">加载演示…</div>
    <div v-else-if="error" class="text-red-400 m-auto">{{ error }}</div>
    <template v-else>
      <div class="flex-1 flex items-center justify-center p-8">
        <div
          class="max-w-4xl w-full min-h-[60vh] rounded-2xl p-12 text-white transition-all duration-500"
          :class="slideClass"
        >
          <p class="text-sm opacity-70 mb-2">{{ index + 1 }} / {{ slides.length }}</p>
          <h1 class="text-4xl font-bold mb-4">{{ current.title }}</h1>
          <p v-if="current.subtitle" class="text-xl opacity-90 mb-6">{{ current.subtitle }}</p>
          <ul v-if="current.bullets?.length" class="space-y-3 text-lg">
            <li v-for="(b, i) in current.bullets" :key="i" class="flex gap-2">
              <span class="opacity-60">•</span>{{ b }}
            </li>
          </ul>
        </div>
      </div>
      <div class="flex justify-between items-center px-6 py-4 bg-black/50 text-white text-sm">
        <button :disabled="index <= 0" class="disabled:opacity-30" @click="prev">上一页</button>
        <span>{{ project?.title }}</span>
        <button :disabled="index >= slides.length - 1" class="disabled:opacity-30" @click="next">
          下一页
        </button>
        <router-link :to="`/editor/${$route.params.id}`" class="ml-4 underline">退出</router-link>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/client'

const route = useRoute()
const project = ref(null)
const index = ref(0)
const loading = ref(true)
const error = ref('')

const slides = computed(() => project.value?.slides || [])
const current = computed(() => slides.value[index.value] || {})
const slideClass = computed(() => {
  const themes = [
    'bg-gradient-to-br from-[#005daa] to-[#0075d5]',
    'bg-gradient-to-br from-[#006d33] to-[#45e17c]',
  ]
  return themes[index.value % themes.length]
})

onMounted(async () => {
  try {
    project.value = await api.getProject(Number(route.params.id))
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

function prev() {
  if (index.value > 0) index.value--
}
function next() {
  if (index.value < slides.value.length - 1) index.value++
}
function onKey(e) {
  if (e.key === 'ArrowRight' || e.key === ' ') next()
  if (e.key === 'ArrowLeft') prev()
}
</script>
