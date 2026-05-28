<template>
  <div class="fixed inset-0 bg-black flex flex-col text-white">
    <div v-if="loading" class="m-auto flex flex-col items-center gap-3">
      <div class="w-10 h-10 border-4 border-white/30 border-t-white rounded-full animate-spin" />
      加载分享演示…
    </div>
    <div v-else-if="error" class="m-auto text-center px-6">
      <span class="material-symbols-outlined text-5xl text-red-400 mb-4">error_outline</span>
      <p class="text-red-400 text-lg">{{ error }}</p>
      <p class="text-white/60 text-sm mt-2">链接可能已失效或演示已被删除</p>
    </div>
    <template v-else>
      <div class="flex-1 flex items-center justify-center p-4 md:p-8">
        <div class="max-w-4xl w-full rounded-2xl p-8 md:p-12 bg-gradient-to-br from-[#005daa] to-[#0075d5] shadow-2xl">
          <p class="text-sm opacity-70 mb-2">{{ index + 1 }} / {{ slides.length }}</p>
          <h1 class="text-2xl md:text-4xl font-bold mb-4">{{ current.title }}</h1>
          <p v-if="current.subtitle" class="text-lg md:text-xl opacity-90 mb-6">{{ current.subtitle }}</p>
          <ul v-if="current.bullets?.length" class="space-y-3 text-base md:text-lg">
            <li v-for="(b, i) in current.bullets" :key="i">• {{ b }}</li>
          </ul>
        </div>
      </div>
      <div class="flex justify-center gap-8 py-4 bg-black/50">
        <button :disabled="index <= 0" class="disabled:opacity-30 px-4 py-1" @click="index--">上一页</button>
        <button :disabled="index >= slides.length - 1" class="disabled:opacity-30 px-4 py-1" @click="index++">下一页</button>
      </div>
      <footer class="py-3 text-center text-xs text-white/40 border-t border-white/10">
        AI智能H5演示平台 · 分享预览
      </footer>
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
    error.value = e.message || '无法加载分享内容'
  } finally {
    loading.value = false
  }
})
</script>
