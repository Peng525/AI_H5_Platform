<template>
  <div class="h-dvh flex flex-col bg-surface-container-low overflow-hidden">
    <header class="h-14 border-b border-outline-variant bg-white flex items-center px-4 gap-3 shrink-0">
      <CreatePageHeaderNav>
        <input
          v-model="title"
          class="text-base font-semibold border-0 bg-transparent min-w-0 flex-1 focus:outline-none"
          @blur="saveTitle"
        />
      </CreatePageHeaderNav>
      <button type="button" class="text-sm px-3 py-1.5 rounded-lg border border-outline-variant" @click="saveResume">
        保存
      </button>
      <div class="relative">
        <button type="button" class="text-sm px-3 py-1.5 rounded-lg border border-outline-variant" @click="exportOpen = !exportOpen">
          导出 ▼
        </button>
        <div v-if="exportOpen" class="absolute right-0 mt-1 bg-white border rounded-lg shadow-lg z-10 py-1 min-w-[8rem]">
          <button type="button" class="block w-full text-left px-4 py-2 text-sm hover:bg-surface-container-low" @click="doExport('pdf')">PDF</button>
          <button type="button" class="block w-full text-left px-4 py-2 text-sm hover:bg-surface-container-low" @click="doExport('docx')">Word</button>
        </div>
      </div>
      <UserMenu />
    </header>

    <p v-if="error" class="shrink-0 px-4 py-2 bg-red-50 text-red-700 text-sm">{{ error }}</p>

    <div class="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-[320px_1fr_280px]">
      <ResumeChatPanel :messages="messages" :generating="generating" @submit="onOptimize" />
      <ResumePreviewPanel :structured="structured" />
      <ResumeAdviceSidebar :advice="advice" :next-steps="nextSteps" :generating="generating" />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CreatePageHeaderNav from '../../components/create/CreatePageHeaderNav.vue'
import UserMenu from '../../components/create/UserMenu.vue'
import ResumeAdviceSidebar from '../../components/resume/ResumeAdviceSidebar.vue'
import ResumeChatPanel from '../../components/resume/ResumeChatPanel.vue'
import ResumePreviewPanel from '../../components/resume/ResumePreviewPanel.vue'
import { api } from '../../api/client.js'
import { useToast } from '../../composables/useToast.js'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const publicId = ref(route.params.publicId)
const title = ref('我的简历')
const structured = ref({})
const messages = ref([])
const advice = ref({})
const nextSteps = ref([])
const generating = ref(false)
const error = ref('')
const exportOpen = ref(false)

async function load() {
  error.value = ''
  try {
    const data = await api.getResume(publicId.value)
    title.value = data.title || '我的简历'
    structured.value = data.structured || {}
    advice.value = data.sidecar?.advice || {}
    nextSteps.value = data.sidecar?.next_steps || []
    const msgRes = await api.getResumeMessages(publicId.value)
    messages.value = msgRes.items || []
  } catch (e) {
    error.value = e.message || '加载失败'
  }
}

async function saveTitle() {
  try {
    await api.updateResume(publicId.value, { title: title.value })
  } catch {
    /* ignore */
  }
}

async function saveResume() {
  try {
    await api.updateResume(publicId.value, { title: title.value, structured: structured.value })
    toast.show('已保存', { type: 'success' })
  } catch (e) {
    toast.show(e.message || '保存失败', { type: 'error' })
  }
}

async function onOptimize(prompt) {
  generating.value = true
  error.value = ''
  messages.value = [...messages.value, { role: 'user', content: prompt }]
  try {
    const data = await api.optimizeResume(publicId.value, { prompt })
    structured.value = data.structured || {}
    advice.value = data.sidecar?.advice || {}
    nextSteps.value = data.sidecar?.next_steps || []
    const msgRes = await api.getResumeMessages(publicId.value)
    messages.value = msgRes.items || []
    toast.show('优化完成', { type: 'success' })
  } catch (e) {
    error.value = e.message || '优化失败'
    if (String(e.message).includes('402') || String(e.message).includes('配额')) {
      router.push('/upgrade')
    }
  } finally {
    generating.value = false
  }
}

async function doExport(format) {
  exportOpen.value = false
  try {
    await api.exportResume(publicId.value, format)
    toast.show('导出已开始', { type: 'success' })
  } catch (e) {
    toast.show(e.message || '导出失败', { type: 'error' })
  }
}

onMounted(load)
</script>
