<template>
  <div class="h-screen flex flex-col bg-background overflow-hidden">
    <EditorTopBar :project-title="project?.title" :project-id="projectId" />
    <div class="flex flex-1 min-h-0">
      <aside class="w-52 border-r border-outline-variant bg-surface-container-low flex flex-col shrink-0 overflow-y-auto">
        <p class="p-3 text-xs font-semibold text-on-surface-variant">页面</p>
        <button
          v-for="(s, i) in project?.slides || []"
          :key="s.id"
          class="mx-2 mb-2 p-2 rounded-lg text-left text-sm border"
          :class="current?.id === s.id ? 'border-primary bg-white' : 'border-transparent hover:bg-white'"
          @click="current = s"
        >
          <div class="font-medium truncate">{{ i + 1 }}. {{ s.title || '未命名' }}</div>
        </button>
      </aside>

      <main class="flex-1 flex flex-col items-center justify-center p-6 bg-surface-container overflow-y-auto">
        <div v-if="current" class="w-[320px] min-h-[560px] bg-white rounded-[2rem] shadow-2xl border-8 border-gray-900 overflow-hidden">
          <div class="h-8 bg-gray-900" />
          <div class="p-6 bg-gradient-to-br from-primary to-primary-container text-white min-h-[480px]">
            <span class="text-xs opacity-80">第 {{ slideIndex + 1 }} 页</span>
            <h2 class="text-xl font-bold mt-2">{{ current.title }}</h2>
            <p v-if="current.subtitle" class="text-sm mt-2 opacity-90">{{ current.subtitle }}</p>
            <ul v-if="current.bullets?.length" class="mt-4 space-y-2 text-sm">
              <li v-for="(b, j) in current.bullets" :key="j">• {{ b }}</li>
            </ul>
          </div>
        </div>
        <p v-else class="text-on-surface-variant">加载中…</p>
      </main>

      <AiPanel
        :loading="aiLoading"
        :quota-remaining="quota.remaining"
        :quota-total="quota.total"
        @generate="onGenerate"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/client'
import { useAuth } from '../composables/useAuth'
import AiPanel from '../components/AiPanel.vue'
import EditorTopBar from '../components/EditorTopBar.vue'

const route = useRoute()
const { user } = useAuth()
const projectId = computed(() => route.params.id)
const project = ref(null)
const current = ref(null)
const aiLoading = ref(false)
const quota = ref({ remaining: 5, total: 5 })

const slideIndex = computed(() => {
  if (!project.value?.slides || !current.value) return 0
  return project.value.slides.findIndex((s) => s.id === current.value.id)
})

async function load() {
  project.value = await api.getProject(Number(projectId.value))
  current.value = project.value.slides?.[0] || null
  const q = await api.getQuota(user.value?.user_id)
  quota.value = { remaining: q.quota_remaining, total: q.quota_total }
}

onMounted(load)
watch(() => route.params.id, load)

async function onGenerate({ prompt, channelTier, channel }) {
  if (!prompt?.trim() || !current.value) return
  aiLoading.value = true
  try {
    const updated = await api.generatePage(
      project.value.id,
      current.value.id,
      { instruction: prompt, tier: channelTier, channel: channel || undefined },
      user.value?.user_id
    )
    const idx = project.value.slides.findIndex((s) => s.id === updated.id)
    if (idx >= 0) project.value.slides[idx] = updated
    current.value = updated
    const q = await api.getQuota(user.value?.user_id)
    quota.value = { remaining: q.quota_remaining, total: q.quota_total }
  } catch (e) {
    alert(e.message)
  } finally {
    aiLoading.value = false
  }
}
</script>
