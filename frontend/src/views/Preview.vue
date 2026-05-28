<template>
  <div class="fixed inset-0 bg-black z-50 flex flex-col" tabindex="0" @keydown="onKey">
    <div v-if="loading" class="text-white m-auto flex flex-col items-center gap-3">
      <div class="w-10 h-10 border-4 border-white/30 border-t-white rounded-full animate-spin" />
      加载演示…
    </div>
    <div v-else-if="error" class="text-red-400 m-auto text-center px-6">
      <p>{{ error }}</p>
      <router-link :to="`/editor/${$route.params.id}`" class="text-white underline mt-4 inline-block">返回编辑器</router-link>
    </div>
    <template v-else>
      <div class="absolute top-4 right-4 z-10">
        <button
          class="px-3 py-1.5 rounded-lg bg-white/10 text-white text-xs border border-white/20 hover:bg-white/20"
          @click="phoneMode = !phoneMode"
        >
          {{ phoneMode ? '全屏模式' : '手机框模式' }}
        </button>
      </div>

      <div class="flex-1 flex items-center justify-center p-4 md:p-8">
        <div
          v-if="phoneMode"
          class="w-[375px] max-h-[90vh] bg-gray-900 rounded-[2rem] p-2 shadow-2xl flex flex-col"
        >
          <div class="h-6 flex justify-center"><div class="w-24 h-4 bg-gray-800 rounded-full" /></div>
          <div class="flex-1 rounded-[1.5rem] overflow-hidden p-6 text-white transition-all duration-500 min-h-[560px]" :class="slideClass">
            <p class="text-xs opacity-70 mb-2">{{ index + 1 }} / {{ slides.length }}</p>
            <h1 class="text-2xl font-bold mb-3">{{ current.title }}</h1>
            <p v-if="current.subtitle" class="text-base opacity-90 mb-4">{{ current.subtitle }}</p>
            <ul v-if="current.bullets?.length" class="space-y-2 text-sm">
              <li v-for="(b, i) in current.bullets" :key="i" class="flex gap-2"><span class="opacity-60">•</span>{{ b }}</li>
            </ul>
          </div>
        </div>
        <div v-else class="max-w-4xl w-full min-h-[60vh] rounded-2xl p-8 md:p-12 text-white transition-all duration-500" :class="slideClass">
          <p class="text-sm opacity-70 mb-2">{{ index + 1 }} / {{ slides.length }}</p>
          <h1 class="text-4xl font-bold mb-4">{{ current.title }}</h1>
          <p v-if="current.subtitle" class="text-xl opacity-90 mb-6">{{ current.subtitle }}</p>
          <ul v-if="current.bullets?.length" class="space-y-3 text-lg">
            <li v-for="(b, i) in current.bullets" :key="i" class="flex gap-2"><span class="opacity-60">•</span>{{ b }}</li>
          </ul>
        </div>
      </div>

      <div class="flex justify-between items-center px-6 py-4 bg-black/50 text-white text-sm">
        <button :disabled="index <= 0" class="disabled:opacity-30 px-3 py-1" @click="prev">上一页</button>
        <span class="truncate max-w-[40%] text-center">{{ project?.title }}</span>
        <div class="flex items-center gap-3">
          <button :disabled="index >= slides.length - 1" class="disabled:opacity-30 px-3 py-1" @click="next">下一页</button>
          <router-link :to="`/editor/${$route.params.id}`" class="underline opacity-80 hover:opacity-100">退出</router-link>
        </div>
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
const phoneMode = ref(false)

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
