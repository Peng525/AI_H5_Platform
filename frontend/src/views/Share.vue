<template>
  <div class="fixed inset-0 bg-black flex flex-col text-white">
    <div v-if="loading" class="m-auto">加载分享演示…</div>
    <div v-else-if="error" class="m-auto text-red-400">{{ error }}</div>
    <template v-else>
      <div class="flex-1 flex items-center justify-center p-8">
        <div class="max-w-4xl w-full rounded-2xl p-12 bg-gradient-to-br from-[#005daa] to-[#0075d5]">
          <p class="text-sm opacity-70 mb-2">{{ index + 1 }} / {{ slides.length }}</p>
          <h1 class="text-4xl font-bold mb-4">{{ current.title }}</h1>
          <p v-if="current.subtitle" class="text-xl opacity-90 mb-6">{{ current.subtitle }}</p>
          <ul v-if="current.bullets?.length" class="space-y-3 text-lg">
            <li v-for="(b, i) in current.bullets" :key="i">• {{ b }}</li>
          </ul>
        </div>
      </div>
      <div class="flex justify-center gap-8 py-4 bg-black/50">
        <button :disabled="index <= 0" @click="index--">上一页</button>
        <button :disabled="index >= slides.length - 1" @click="index++">下一页</button>
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

onMounted(async () => {
  try {
    project.value = await api.sharePreview(route.params.slug)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>
