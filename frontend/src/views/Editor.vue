<template>
  <div v-if="loading" class="p-10 text-center text-on-surface-variant">加载编辑器…</div>
  <div v-else-if="error" class="p-10 text-center text-red-600">{{ error }}</div>
  <div v-else class="flex h-[calc(100vh-8rem)] min-h-[500px]">
    <aside class="w-56 border-r border-outline-variant bg-surface-container-low p-3 overflow-y-auto shrink-0">
      <p class="text-xs font-semibold text-on-surface-variant mb-2">页面</p>
      <button
        v-for="(s, i) in project.slides"
        :key="s.id"
        class="w-full text-left px-3 py-2 rounded-lg text-sm mb-1 truncate"
        :class="current?.id === s.id ? 'bg-primary text-on-primary' : 'hover:bg-surface-container-high'"
        @click="current = s"
      >
        {{ i + 1 }}. {{ s.title || '未命名' }}
      </button>
    </aside>

    <section class="flex-1 flex flex-col p-6 overflow-hidden">
      <div class="flex items-center justify-between mb-4 shrink-0">
        <input
          v-model="project.title"
          class="text-xl font-bold bg-transparent border-b border-transparent hover:border-outline-variant focus:border-primary outline-none"
          @blur="saveProject"
        />
        <div class="flex gap-2">
          <router-link
            :to="`/preview/${project.id}`"
            class="px-4 py-2 rounded-lg border border-outline-variant text-sm"
          >
            预览
          </router-link>
          <button class="px-4 py-2 rounded-lg bg-primary text-on-primary text-sm" @click="copyShare">
            复制分享链接
          </button>
        </div>
      </div>

      <div v-if="current" class="flex-1 overflow-y-auto bg-white rounded-xl border border-outline-variant p-8 shadow-card">
        <label class="block mb-3">
          <span class="text-sm text-on-surface-variant">标题</span>
          <input v-model="current.title" class="w-full mt-1 border rounded-lg px-3 py-2" @blur="saveSlide" />
        </label>
        <label class="block mb-3">
          <span class="text-sm text-on-surface-variant">副标题</span>
          <input v-model="current.subtitle" class="w-full mt-1 border rounded-lg px-3 py-2" @blur="saveSlide" />
        </label>
        <label class="block mb-3">
          <span class="text-sm text-on-surface-variant">要点（每行一条）</span>
          <textarea
            :value="bulletsText"
            rows="5"
            class="w-full mt-1 border rounded-lg px-3 py-2"
            @change="updateBullets"
          />
        </label>

        <div class="mt-6 pt-6 border-t border-outline-variant">
          <p class="text-sm font-semibold mb-2">AI 单页改写（模板：单页改写）</p>
          <div class="flex gap-2">
            <input
              v-model="instruction"
              class="flex-1 border rounded-lg px-3 py-2 text-sm"
              placeholder="例如：把要点改成三个数据结论"
            />
            <button
              class="px-4 py-2 rounded-lg bg-secondary text-white text-sm disabled:opacity-50"
              :disabled="aiLoading"
              @click="rewritePage"
            >
              {{ aiLoading ? '改写中…' : '改写' }}
            </button>
          </div>
          <p v-if="aiError" class="text-red-600 text-sm mt-2">{{ aiError }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/client'

const route = useRoute()
const project = ref(null)
const current = ref(null)
const loading = ref(true)
const error = ref('')
const instruction = ref('')
const aiLoading = ref(false)
const aiError = ref('')

const bulletsText = computed(() => (current.value?.bullets || []).join('\n'))

onMounted(load)

watch(() => route.params.id, load)

async function load() {
  loading.value = true
  error.value = ''
  try {
    project.value = await api.getProject(Number(route.params.id))
    current.value = project.value.slides?.[0] || null
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function saveProject() {
  await api.updateProject(project.value.id, { title: project.value.title })
}

async function saveSlide() {
  if (!current.value) return
  try {
    const updated = await api.updateSlide(project.value.id, current.value.id, {
      title: current.value.title,
      subtitle: current.value.subtitle,
      bullets: current.value.bullets,
    })
    const idx = project.value.slides.findIndex((x) => x.id === updated.id)
    if (idx >= 0) project.value.slides[idx] = updated
    current.value = updated
  } catch (e) {
    console.error(e)
  }
}

function updateBullets(e) {
  if (!current.value) return
  current.value.bullets = e.target.value.split('\n').filter(Boolean)
  saveSlide()
}

async function rewritePage() {
  if (!instruction.value.trim()) return
  aiLoading.value = true
  aiError.value = ''
  try {
    const updated = await api.generatePage(project.value.id, current.value.id, {
      instruction: instruction.value,
      tier: 'free',
    })
    const idx = project.value.slides.findIndex((x) => x.id === updated.id)
    if (idx >= 0) project.value.slides[idx] = updated
    current.value = updated
    instruction.value = ''
  } catch (e) {
    aiError.value = e.message
  } finally {
    aiLoading.value = false
  }
}

function copyShare() {
  const slug = project.value.share_slug
  if (!slug) {
    alert('暂无分享链接')
    return
  }
  const url = `${window.location.origin}/s/${slug}`
  navigator.clipboard.writeText(url).then(() => alert('已复制：' + url))
}
</script>
