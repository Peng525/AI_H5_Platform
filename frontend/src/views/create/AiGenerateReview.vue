<template>
  <div class="min-h-screen bg-surface-container-low flex flex-col">
    <header class="h-14 border-b border-outline-variant bg-white flex items-center justify-between px-4 sm:px-6 shrink-0">
      <button type="button" class="text-sm text-on-surface-variant hover:text-primary inline-flex items-center gap-1" @click="router.push('/create/generate/prompt')">
        <span class="material-symbols-outlined text-[18px]">arrow_back</span>
        上一步
      </button>
      <h1 class="text-base font-semibold">提示编辑器</h1>
      <span class="text-xs text-on-surface-variant">{{ quotaText ? `配额 ${quotaText}` : '' }}</span>
    </header>

    <div class="lg:hidden flex gap-1 p-2 bg-white border-b border-outline-variant">
      <button
        v-for="tab in mobileTabs"
        :key="tab.id"
        type="button"
        class="flex-1 py-2 rounded-lg text-sm"
        :class="mobileTab === tab.id ? 'bg-primary/10 text-primary font-medium' : 'text-on-surface-variant'"
        @click="mobileTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="flex-1 grid lg:grid-cols-[260px_1fr_240px] gap-0 min-h-0 overflow-hidden">
      <aside class="bg-white border-r border-outline-variant p-4 overflow-y-auto space-y-4" :class="mobileTab !== 'settings' && 'hidden lg:block'">
        <h2 class="text-sm font-semibold">设置</h2>
        <div>
          <p class="text-xs font-medium text-on-surface-variant mb-2">文本量</p>
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="d in densityOptions"
              :key="d"
              type="button"
              class="px-2 py-2 rounded-lg border text-xs"
              :class="textDensity === d ? 'border-primary bg-primary/5 text-primary' : 'border-outline-variant'"
              @click="textDensity = d"
            >
              {{ d }}
            </button>
          </div>
        </div>
        <label class="block text-sm">
          <span class="text-xs font-medium text-on-surface-variant">写给…</span>
          <input v-model="audience" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 text-sm" placeholder="例如：企业管理层" />
        </label>
        <label class="block text-sm">
          <span class="text-xs font-medium text-on-surface-variant">语气</span>
          <input v-model="tone" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 text-sm" />
        </label>
        <label class="block text-sm">
          <span class="text-xs font-medium text-on-surface-variant">语言</span>
          <select v-model="language" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 text-sm bg-white">
            <option value="简体中文">简体中文</option>
            <option value="English">English</option>
          </select>
        </label>
      </aside>

      <section class="flex flex-col min-h-0 bg-surface-container-low" :class="mobileTab !== 'content' && 'hidden lg:flex'">
        <div class="p-4 border-b border-outline-variant bg-white shrink-0">
          <h2 class="text-sm font-semibold">内容</h2>
          <p class="text-xs text-on-surface-variant mt-1">可在此扩写大纲或补充要点</p>
        </div>
        <textarea
          v-model="extraContent"
          class="flex-1 m-4 rounded-xl border border-outline-variant bg-white p-4 text-sm resize-none min-h-[240px] lg:min-h-0"
          :placeholder="draft.topic"
        />
      </section>

      <aside class="bg-white border-l border-outline-variant p-4 overflow-y-auto space-y-4" :class="mobileTab !== 'tips' && 'hidden lg:block'">
        <h2 class="text-sm font-semibold">说明</h2>
        <label class="block text-sm">
          <span class="text-xs font-medium text-on-surface-variant">附加说明</span>
          <textarea v-model="extraInstructions" rows="4" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 text-sm resize-none" placeholder="可选" />
        </label>
        <p class="text-xs text-on-surface-variant leading-relaxed">
          点击「生成」后，AI 将根据您的提示词与设置创建完整演示结构，并进入编辑器继续排版与配图。
        </p>
      </aside>
    </div>

    <footer class="shrink-0 border-t border-outline-variant bg-white px-4 sm:px-6 py-4 flex flex-wrap items-center justify-between gap-3">
      <div class="flex items-center gap-2">
        <button type="button" class="w-9 h-9 rounded-lg border border-outline-variant hover:bg-surface-container-low" @click="pageCount = Math.max(1, pageCount - 1)">−</button>
        <span class="text-sm tabular-nums min-w-[72px] text-center">{{ pageCount }} 张卡片</span>
        <button type="button" class="w-9 h-9 rounded-lg border border-outline-variant hover:bg-surface-container-low" @click="pageCount = Math.min(30, pageCount + 1)">+</button>
      </div>
      <p v-if="error" class="text-sm text-red-600 flex-1">{{ error }}</p>
      <button
        type="button"
        class="px-8 py-2.5 rounded-xl bg-primary text-on-primary font-medium inline-flex items-center gap-2 disabled:opacity-50"
        :disabled="generating"
        @click="generate"
      >
        <span class="material-symbols-outlined text-[18px]">auto_awesome</span>
        {{ generating ? '生成中…' : '生成' }}
      </button>
    </footer>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../../api/client'
import { applyProjectSettingsLocal, clearDraft, loadDraft, requireDeckDraft, saveDraft } from '../../composables/useAiCreateDraft.js'

const router = useRouter()
const draft = ref(loadDraft())
const mobileTab = ref('content')
const mobileTabs = [
  { id: 'settings', label: '设置' },
  { id: 'content', label: '内容' },
  { id: 'tips', label: '说明' },
]
const densityOptions = ['简约', '精炼', '详细', '繁琐']

const pageCount = ref(10)
const textDensity = ref('精炼')
const audience = ref('')
const tone = ref('专业、清晰、具说服力')
const language = ref('简体中文')
const extraContent = ref('')
const extraInstructions = ref('')
const generating = ref(false)
const error = ref('')
const quotaText = ref('')

onMounted(async () => {
  const d = requireDeckDraft(router)
  if (!d) return
  if (!d.topic?.trim()) {
    router.replace('/create/generate/prompt')
    return
  }
  draft.value = d
  pageCount.value = d.pageCount || 10
  textDensity.value = d.textDensity || '精炼'
  audience.value = d.audience || ''
  tone.value = d.tone || '专业、清晰、具说服力'
  language.value = d.language || '简体中文'
  extraContent.value = d.extraContent || d.topic || ''
  extraInstructions.value = d.extraInstructions || ''
  try {
    const q = await api.getQuota()
    quotaText.value = `${q.quota_remaining}/${q.quota_total}`
  } catch {
    quotaText.value = ''
  }
})

async function generate() {
  generating.value = true
  error.value = ''
  saveDraft({
    pageCount: pageCount.value,
    textDensity: textDensity.value,
    audience: audience.value,
    tone: tone.value,
    language: language.value,
    extraContent: extraContent.value,
    extraInstructions: extraInstructions.value,
  })
  try {
    const project = await api.generateAiDeck({
      topic: draft.value.topic,
      page_count: pageCount.value,
      audience: audience.value,
      tone: tone.value,
      text_density: textDensity.value,
      language: language.value,
      viewport_mode: draft.value.viewportMode || 'auto',
      background_preset: draft.value.background || 'classic_white',
      extra_content: extraContent.value,
      extra_instructions: extraInstructions.value,
    })
    applyProjectSettingsLocal(project.id, project.settings || {})
    clearDraft()
    router.push(`/editor/${project.id}`)
  } catch (e) {
    error.value = e.message || '生成失败'
    generating.value = false
  }
}
</script>
