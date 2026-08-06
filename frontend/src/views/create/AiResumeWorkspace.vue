<template>

  <div class="h-dvh flex flex-col bg-surface-container-low overflow-hidden">

    <header class="h-14 border-b border-outline-variant bg-white flex items-center justify-between px-4 sm:px-8 shrink-0 gap-3">

      <CreatePageHeaderNav>

        <input

          v-model="title"

          class="text-base font-semibold border-0 bg-transparent min-w-0 max-w-[10rem] sm:max-w-xs focus:outline-none"

          :disabled="generating"

          @blur="saveTitle"

        />

      </CreatePageHeaderNav>

      <span class="hidden md:inline text-xs text-on-surface-variant flex-1 text-center truncate px-2">

        {{ templateTitle }}

      </span>

      <label v-if="visualTemplateOptions.length" class="hidden sm:flex items-center gap-1.5 text-xs text-on-surface-variant shrink-0">

        模板

        <select

          v-model="selectedTemplateId"

          class="text-sm border border-outline-variant rounded-lg px-2 py-1 bg-white max-w-[8rem]"

          :disabled="generating || templateSwitching"

          @change="onTemplateChange"

        >

          <option v-for="opt in visualTemplateOptions" :key="opt.id" :value="opt.id">{{ opt.title }}</option>

        </select>

      </label>

      <div class="flex items-center gap-2 shrink-0 ml-auto">

        <button

          type="button"

          class="text-sm px-3 py-1.5 rounded-lg border border-outline-variant disabled:opacity-50"

          :disabled="generating"

          @click="saveResume"

        >

          保存

        </button>

        <div class="relative">

          <button

            type="button"

            class="text-sm px-3 py-1.5 rounded-lg border border-outline-variant disabled:opacity-50"

            :disabled="generating"

            @click="exportOpen = !exportOpen"

          >

            导出 ▼

          </button>

          <div v-if="exportOpen" class="absolute right-0 mt-1 bg-white border rounded-lg shadow-lg z-10 py-1 min-w-[8rem]">

            <button type="button" class="block w-full text-left px-4 py-2 text-sm hover:bg-surface-container-low" @click="doExport('pdf')">PDF</button>

            <button type="button" class="block w-full text-left px-4 py-2 text-sm hover:bg-surface-container-low" @click="doExport('docx')">Word</button>

          </div>

        </div>

        <UserMenu />

      </div>

    </header>



    <div

      v-if="generating"

      class="shrink-0 px-4 py-2 bg-primary/10 border-b border-primary/20 text-sm text-primary flex items-center gap-2"

      role="status"

    >

      <span class="material-symbols-outlined text-[18px] animate-spin">progress_activity</span>

      <span>{{ generatingStatusText }}</span>

    </div>



    <p v-if="error" class="shrink-0 px-4 py-2 bg-red-50 text-red-700 text-sm">{{ error }}</p>



    <div
      class="resume-workspace-grid flex-1 min-h-0 grid grid-cols-1 overflow-visible"
      :class="{ 'has-advice': mode === 'optimize' }"
      :style="workspaceGridStyle"
    >

      <ResumeChatAside

        :messages="messages"

        :generating="generating"

        :collapsed="chatCollapsed"

        @update:collapsed="onChatCollapsed"

        @submit="onOptimize"

      />

      <ResumeEditorPanel

        v-if="!generating"

        ref="editorRef"

        :structured="structured"

        :visual-document="visualDocument"

        :public-id="publicId"

        @update:structured="structured = $event"

        @update:visual-document="visualDocument = $event"

      />

      <div

        v-else

        class="h-full min-h-[12rem] bg-surface-container-low"

        aria-hidden="true"

      />

      <ResumeAdviceSidebar

        v-if="mode === 'optimize'"

        :advice="advice"

        :next-steps="nextSteps"

        :generating="generating"

      />

    </div>



    <DeckGenerateOverlay

      :open="generating"

      :estimated-seconds="60"

      title="正在生成简历…"

      :subtitle="generateOverlaySubtitle"

      footer-hint="生成完成后将展示 AI 填充的简历内容"

    />

  </div>

</template>



<script setup>

import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

import { useRoute, useRouter } from 'vue-router'

import CreatePageHeaderNav from '../../components/create/CreatePageHeaderNav.vue'

import DeckGenerateOverlay from '../../components/create/DeckGenerateOverlay.vue'

import UserMenu from '../../components/create/UserMenu.vue'

import ResumeAdviceSidebar from '../../components/resume/ResumeAdviceSidebar.vue'

import ResumeChatAside from '../../components/resume/ResumeChatAside.vue'

import ResumeEditorPanel from '../../components/resume/ResumeEditorPanel.vue'

import { api } from '../../api/client.js'

import { defaultStructured, defaultVisualDocument } from '../../utils/resumeBind.js'

import { normalizeTemplateId, TEMPLATE_OPTIONS } from '../../utils/resumeTemplateRegistry.js'

import { isQuotaExceeded } from '../../composables/useResumeErrors.js'

import {

  clearPendingGenerate,

  loadPendingGenerate,

} from '../../composables/useResumePendingGenerate.js'

import { useToast } from '../../composables/useToast.js'



const CHAT_COLLAPSED_KEY = 'resume_chat_collapsed'



const route = useRoute()

const router = useRouter()

const toast = useToast()



const publicId = ref(route.params.publicId)

const title = ref('我的简历')

const structured = ref(defaultStructured())

const visualDocument = ref(defaultVisualDocument())

const messages = ref([])

const advice = ref({})

const nextSteps = ref([])

const generating = ref(false)

const error = ref('')

const exportOpen = ref(false)

const editorRef = ref(null)

const chatCollapsed = ref(false)

const visualTemplateOptions = ref(TEMPLATE_OPTIONS)

const selectedTemplateId = ref('template1')

const templateSwitching = ref(false)

const activeGenerateTemplateId = ref('')

const generateElapsed = ref(0)



let generateElapsedTimer = null



const mode = computed(() => (route.query.mode === 'edit' ? 'edit' : 'optimize'))



const templateTitle = computed(() => {

  const id = normalizeTemplateId(visualDocument.value?.template_id)

  return visualTemplateOptions.value.find((t) => t.id === id)?.title || id

})



const activeGenerateTemplateTitle = computed(() => {

  const id = normalizeTemplateId(activeGenerateTemplateId.value || visualDocument.value?.template_id)

  return visualTemplateOptions.value.find((t) => t.id === id)?.title || id

})



const generateOverlaySubtitle = computed(() => {

  const tpl = activeGenerateTemplateTitle.value

  return tpl

    ? `AI 正在解析简历与 JD，并写入模板「${tpl}」，请稍候…`

    : 'AI 正在解析简历与 JD，请稍候…'

})



const generatingStatusText = computed(() => {

  const s = generateElapsed.value

  const elapsed = s < 60 ? `${s} 秒` : `${Math.floor(s / 60)} 分 ${s % 60} 秒`

  return `生成中 · 已等待 ${elapsed}`

})



const workspaceGridStyle = computed(() => ({

  '--resume-chat-col': chatCollapsed.value ? '3rem' : '320px',

}))



watch(generating, (isGenerating) => {

  if (generateElapsedTimer) {

    clearInterval(generateElapsedTimer)

    generateElapsedTimer = null

  }

  if (!isGenerating) {

    generateElapsed.value = 0

    return

  }

  generateElapsed.value = 0

  generateElapsedTimer = setInterval(() => {

    generateElapsed.value += 1

  }, 1000)

})



function onChatCollapsed(val) {

  chatCollapsed.value = val

  try {

    sessionStorage.setItem(CHAT_COLLAPSED_KEY, val ? '1' : '0')

  } catch {

    /* ignore */

  }

}



async function load() {

  error.value = ''

  try {

    const data = await api.getResume(publicId.value)

    title.value = data.title || '我的简历'

    structured.value = { ...defaultStructured(), ...(data.structured || {}) }

    visualDocument.value = { ...defaultVisualDocument(), ...(data.visual_document || {}) }

    selectedTemplateId.value = normalizeTemplateId(visualDocument.value.template_id)

    advice.value = data.sidecar?.advice || {}

    nextSteps.value = data.sidecar?.next_steps || []

    const msgRes = await api.getResumeMessages(publicId.value)

    messages.value = msgRes.items || []

  } catch (e) {

    error.value = e.message || '加载失败'

  }

}



async function resolveGeneratePayload() {

  const pending = loadPendingGenerate(publicId.value) || {}

  if (pending.template_id) return pending

  if (route.query.generating !== '1') return pending

  try {

    const data = await api.getResume(publicId.value)

    const tid = normalizeTemplateId(data.visual_document?.template_id)

    if (tid) return { ...pending, template_id: tid }

  } catch {

    /* ignore */

  }

  return pending

}



async function runPendingGenerate() {

  const pending = await resolveGeneratePayload()

  if (!pending.template_id && !loadPendingGenerate(publicId.value) && route.query.generating !== '1') {

    return

  }



  if (!pending.template_id) {

    error.value = '请选择简历模板'

    generating.value = false

    clearPendingGenerate(publicId.value)

    if (route.query.generating === '1') {

      router.replace({

        path: route.path,

        query: { mode: route.query.mode || 'optimize' },

      })

    }

    return

  }



  generating.value = true

  activeGenerateTemplateId.value = pending.template_id

  error.value = ''

  const promptText = (pending.prompt || '').trim()

  if (promptText) {

    messages.value = [{ role: 'user', content: promptText }]

  }



  try {

    await api.generateResume(publicId.value, {

      template_id: pending.template_id,

      prompt: promptText || undefined,

      file_id: pending.file_id || undefined,

      jd_file_id: pending.jd_file_id || undefined,

      prompt_template_id: pending.prompt_template_id || undefined,

      industry_id: pending.industry_id || undefined,

    })

    await load()

    toast.show('生成完成', { type: 'success' })

  } catch (e) {

    error.value = e.message || '生成失败'

    if (isQuotaExceeded(e)) {

      router.push('/upgrade')

    }

  } finally {

    generating.value = false

    activeGenerateTemplateId.value = ''

    clearPendingGenerate(publicId.value)

    if (route.query.generating === '1') {

      router.replace({

        path: route.path,

        query: { mode: route.query.mode || 'optimize' },

      })

    }

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

    await api.updateResume(publicId.value, {

      title: title.value,

      structured: structured.value,

      visual_document: visualDocument.value,

    })

    toast.show('已保存', { type: 'success' })

  } catch (e) {

    toast.show(e.message || '保存失败', { type: 'error' })

  }

}



async function onOptimize(prompt) {

  generating.value = true

  activeGenerateTemplateId.value = selectedTemplateId.value

  error.value = ''

  messages.value = [...messages.value, { role: 'user', content: prompt }]

  try {

    const data = await api.optimizeResume(publicId.value, { prompt })

    structured.value = { ...defaultStructured(), ...(data.structured || {}) }

    visualDocument.value = { ...defaultVisualDocument(), ...(data.visual_document || {}) }

    advice.value = data.sidecar?.advice || {}

    nextSteps.value = data.sidecar?.next_steps || []

    const msgRes = await api.getResumeMessages(publicId.value)

    messages.value = msgRes.items || []

    toast.show('优化完成', { type: 'success' })

  } catch (e) {

    error.value = e.message || '优化失败'

    if (isQuotaExceeded(e)) {

      router.push('/upgrade')

    }

  } finally {

    generating.value = false

    activeGenerateTemplateId.value = ''

  }

}



async function onTemplateChange() {

  if (!selectedTemplateId.value) return

  templateSwitching.value = true

  try {

    visualDocument.value = {

      ...visualDocument.value,

      template_id: selectedTemplateId.value,

    }

    await api.updateResume(publicId.value, {

      structured: structured.value,

      visual_document: visualDocument.value,

    })

    toast.show('模板已切换', { type: 'success' })

  } catch (e) {

    toast.show(e.message || '切换失败', { type: 'error' })

    selectedTemplateId.value = normalizeTemplateId(visualDocument.value?.template_id)

  } finally {

    templateSwitching.value = false

  }

}



async function loadTemplateOptions() {

  try {

    const data = await api.listResumeVisualTemplates()

    if (data.items?.length) {

      visualTemplateOptions.value = data.items.map((t) => ({ id: t.id, title: t.title }))

    }

  } catch {

    /* keep defaults */

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



onMounted(async () => {

  try {

    chatCollapsed.value = sessionStorage.getItem(CHAT_COLLAPSED_KEY) === '1'

  } catch {

    /* ignore */

  }



  const pending = loadPendingGenerate(publicId.value)

  const shouldGenerate = !!(pending || route.query.generating === '1')

  if (shouldGenerate) {

    generating.value = true

    activeGenerateTemplateId.value = pending?.template_id || ''

  }



  await loadTemplateOptions()



  if (shouldGenerate) {

    await runPendingGenerate()

  } else {

    await load()

  }

})



onUnmounted(() => {

  if (generateElapsedTimer) clearInterval(generateElapsedTimer)

})

</script>

<style scoped>
@media (min-width: 1024px) {
  .resume-workspace-grid {
    grid-template-columns: var(--resume-chat-col, 320px) minmax(0, 1fr);
    transition: grid-template-columns 280ms cubic-bezier(0.4, 0, 0.2, 1);
  }
  .resume-workspace-grid.has-advice {
    grid-template-columns: var(--resume-chat-col, 320px) minmax(0, 1fr) 280px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .resume-workspace-grid {
    transition: none;
  }
}
</style>

