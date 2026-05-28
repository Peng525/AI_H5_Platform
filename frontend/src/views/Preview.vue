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
      <div class="absolute top-4 right-4 z-10 flex gap-2">
        <select
          v-model="viewportId"
          class="text-xs rounded-lg bg-white/10 text-white border border-white/20 px-2 py-1.5 max-w-[140px]"
        >
          <optgroup label="手机">
            <option v-for="v in mobileViewports" :key="v.id" :value="v.id">{{ v.label }}</option>
          </optgroup>
          <optgroup label="网页">
            <option v-for="v in webViewports" :key="v.id" :value="v.id">{{ v.label }}</option>
          </optgroup>
        </select>
        <button
          type="button"
          class="px-3 py-1.5 rounded-lg bg-white/10 text-white text-xs border border-white/20 hover:bg-white/20"
          @click="phoneFrame = !phoneFrame"
        >
          {{ phoneFrame ? '无边框' : '设备边框' }}
        </button>
      </div>

      <div v-if="scrollEffect === 'page'" class="flex-1 flex items-center justify-center p-4 overflow-hidden">
        <div :class="frameWrapClass" :style="frameStyle">
          <Transition :name="transitionName" mode="out-in">
            <div :key="index" class="w-full h-full p-6 text-white flex flex-col justify-center rounded-xl" :class="slideClass">
              <p class="text-sm opacity-70 mb-2">{{ index + 1 }} / {{ slides.length }}</p>
              <h1 :class="viewport.device === 'web' ? 'text-4xl' : 'text-2xl'" class="font-bold mb-3">{{ current.title }}</h1>
              <p v-if="current.subtitle" class="opacity-90 mb-4">{{ current.subtitle }}</p>
              <ul v-if="current.bullets?.length" class="space-y-2">
                <li v-for="(b, i) in current.bullets" :key="i">• {{ b }}</li>
              </ul>
            </div>
          </Transition>
        </div>
      </div>

      <div
        v-else-if="scrollEffect === 'vertical' || scrollEffect === 'snap'"
        class="flex-1 overflow-y-auto"
        :class="scrollEffect === 'snap' ? 'snap-y snap-mandatory' : ''"
      >
        <div
          v-for="(s, i) in slides"
          :key="s.id"
          class="min-h-full flex items-center justify-center p-4"
          :class="scrollEffect === 'snap' ? 'snap-start' : ''"
        >
          <div class="w-full max-w-lg rounded-2xl p-8 text-white" :class="themeClass(i)">
            <p class="text-sm opacity-70 mb-2">{{ i + 1 }} / {{ slides.length }}</p>
            <h1 class="text-2xl font-bold mb-3">{{ s.title }}</h1>
            <p v-if="s.subtitle" class="opacity-90 mb-4">{{ s.subtitle }}</p>
            <ul v-if="s.bullets?.length" class="space-y-2">
              <li v-for="(b, j) in s.bullets" :key="j">• {{ b }}</li>
            </ul>
          </div>
        </div>
      </div>

      <div v-else class="flex-1 overflow-x-auto flex snap-x snap-mandatory">
        <div v-for="(s, i) in slides" :key="s.id" class="min-w-full h-full flex items-center justify-center p-4 snap-center shrink-0">
          <div class="w-full max-w-lg rounded-2xl p-8 text-white" :class="themeClass(i)">
            <p class="text-sm opacity-70 mb-2">{{ i + 1 }} / {{ slides.length }}</p>
            <h1 class="text-2xl font-bold mb-3">{{ s.title }}</h1>
            <ul v-if="s.bullets?.length" class="space-y-2">
              <li v-for="(b, j) in s.bullets" :key="j">• {{ b }}</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="flex justify-between items-center px-6 py-4 bg-black/50 text-white text-sm shrink-0">
        <button type="button" :disabled="index <= 0 || scrollEffect !== 'page'" class="disabled:opacity-30 px-3 py-1" @click="prev">上一页</button>
        <span class="text-xs text-center">{{ scrollLabel }} · {{ index + 1 }}/{{ slides.length }}</span>
        <div class="flex items-center gap-3">
          <button type="button" :disabled="index >= slides.length - 1 || scrollEffect !== 'page'" class="disabled:opacity-30 px-3 py-1" @click="next">下一页</button>
          <router-link :to="`/editor/${$route.params.id}`" class="underline opacity-80">退出</router-link>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/client'
import { VIEWPORT_PRESETS, getViewportPreset, SCROLL_EFFECTS } from '../constants/editorPresets'
import { getSlideAnimation } from '../utils/slideAnimation'

const route = useRoute()
const project = ref(null)
const index = ref(0)
const loading = ref(true)
const error = ref('')
const phoneFrame = ref(true)
const viewportId = ref('mobile-375')
const scrollEffect = ref('page')

const mobileViewports = VIEWPORT_PRESETS.filter((v) => v.device === 'mobile')
const webViewports = VIEWPORT_PRESETS.filter((v) => v.device === 'web')

const slides = computed(() => project.value?.slides || [])
const current = computed(() => slides.value[index.value] || {})
const viewport = computed(() => getViewportPreset(viewportId.value))

const transitionName = computed(() => {
  const anim = getSlideAnimation(current.value)
  const map = {
    fade: 'slide-fade',
    'slide-left': 'slide-left',
    'slide-right': 'slide-right',
    'slide-up': 'slide-up',
    zoom: 'slide-zoom',
    flip: 'slide-flip',
    none: 'slide-none',
  }
  return map[anim] || 'slide-fade'
})

const scrollLabel = computed(() => SCROLL_EFFECTS.find((s) => s.id === scrollEffect.value)?.label || '翻页')

function themeClass(i) {
  return i % 2 === 0
    ? 'bg-gradient-to-br from-[#005daa] to-[#0075d5]'
    : 'bg-gradient-to-br from-[#006d33] to-[#45e17c]'
}

const slideClass = computed(() => themeClass(index.value))

const frameWrapClass = computed(() => {
  if (!phoneFrame.value) return 'w-full max-w-4xl overflow-hidden shadow-2xl'
  return viewport.value.device === 'mobile'
    ? 'bg-gray-900 rounded-[2rem] p-2 shadow-2xl overflow-hidden'
    : 'bg-gray-200 rounded-lg p-1 shadow-2xl border border-gray-400 overflow-hidden'
})

const frameStyle = computed(() => {
  const scale = Math.min(1, 420 / viewport.value.width, 720 / viewport.value.height)
  return {
    width: Math.round(viewport.value.width * scale) + 'px',
    minHeight: Math.round(viewport.value.height * scale) + 'px',
  }
})

function loadProjectSettings() {
  try {
    const raw = localStorage.getItem(`ai_h5_project_settings_${route.params.id}`)
    if (raw) {
      const s = JSON.parse(raw)
      if (s.viewportId) viewportId.value = s.viewportId
      if (s.scrollEffect) scrollEffect.value = s.scrollEffect
    }
  } catch { /* ignore */ }
}

onMounted(async () => {
  loadProjectSettings()
  try {
    project.value = await api.getProject(Number(route.params.id))
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

watch(viewportId, (id) => {
  try {
    const key = `ai_h5_project_settings_${route.params.id}`
    const s = JSON.parse(localStorage.getItem(key) || '{}')
    s.viewportId = id
    localStorage.setItem(key, JSON.stringify(s))
  } catch { /* ignore */ }
})

function prev() {
  if (index.value > 0) index.value--
}
function next() {
  if (index.value < slides.value.length - 1) index.value++
}
function onKey(e) {
  if (scrollEffect.value !== 'page') return
  if (e.key === 'ArrowRight' || e.key === ' ') next()
  if (e.key === 'ArrowLeft') prev()
}
</script>
