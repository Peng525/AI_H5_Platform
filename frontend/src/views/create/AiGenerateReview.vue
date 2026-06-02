<template>
  <div class="min-h-screen bg-surface-container-low flex flex-col">
    <header class="h-14 border-b border-outline-variant bg-white flex items-center justify-between px-4 sm:px-6 shrink-0">
      <button type="button" class="text-sm text-on-surface-variant hover:text-primary inline-flex items-center gap-1" @click="router.push('/create/generate')">
        <span class="material-symbols-outlined text-[18px]">arrow_back</span>
        上一步
      </button>
      <h1 class="text-base font-semibold">提示编辑器</h1>
      <UserMenu />
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
        <div class="p-4 border-b border-outline-variant bg-white shrink-0 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 class="text-sm font-semibold">内容</h2>
            <p class="text-xs text-on-surface-variant mt-1">
              {{ contentMode === 'free' ? '完整提示词，生成时由 AI 自行分页' : '逐页编辑，生成时一页对应一段内容' }}
            </p>
          </div>
          <div class="inline-flex rounded-lg border border-outline-variant p-0.5 bg-surface-container-low text-xs">
            <button
              type="button"
              class="px-3 py-1.5 rounded-md transition"
              :class="contentMode === 'free' ? 'bg-white shadow-sm text-primary font-medium' : 'text-on-surface-variant'"
              @click="switchToFree"
            >
              自由形式
            </button>
            <button
              type="button"
              class="px-3 py-1.5 rounded-md transition"
              :class="contentMode === 'per_page' ? 'bg-white shadow-sm text-primary font-medium' : 'text-on-surface-variant'"
              @click="switchToPerPage"
            >
              逐张卡片
            </button>
          </div>
        </div>

        <textarea
          v-if="contentMode === 'free'"
          v-model="extraContent"
          class="flex-1 m-4 rounded-xl border border-outline-variant bg-white p-4 text-sm resize-none min-h-[240px] lg:min-h-0"
          :placeholder="draft.topic"
        />

        <div v-else class="flex-1 min-h-0 flex flex-col mx-4 mb-4 mt-2 gap-2">
          <div class="shrink-0 flex gap-1.5 overflow-x-auto pb-1 scrollbar-thin">
            <button
              v-for="(_, i) in pageContents"
              :key="i"
              type="button"
              class="shrink-0 px-3 py-1.5 rounded-lg border text-xs font-medium transition whitespace-nowrap"
              :class="activePageIndex === i
                ? 'border-primary bg-primary/10 text-primary'
                : pageContents[i]?.trim()
                  ? 'border-outline-variant bg-white text-on-surface hover:border-primary/40'
                  : 'border-outline-variant/60 bg-white text-on-surface-variant hover:border-primary/40'"
              @click="activePageIndex = i"
            >
              页面 {{ i + 1 }}
            </button>
          </div>
          <div class="flex-1 min-h-0 rounded-xl border border-outline-variant bg-white flex flex-col">
            <textarea
              v-model="pageContents[activePageIndex]"
              class="flex-1 min-h-0 w-full p-4 text-sm resize-none border-0 rounded-xl focus:ring-0 focus:outline-none leading-relaxed"
              :placeholder="`第 ${activePageIndex + 1} 页内容…`"
            />
          </div>
        </div>
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
        <button type="button" class="w-9 h-9 rounded-lg border border-outline-variant hover:bg-surface-container-low" @click="decreasePageCount">−</button>
        <span class="text-sm tabular-nums min-w-[72px] text-center">{{ pageCount }} 张卡片</span>
        <button type="button" class="w-9 h-9 rounded-lg border border-outline-variant hover:bg-surface-container-low" @click="increasePageCount">+</button>
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

    <CardSplitModeDialog
      :open="splitDialogOpen"
      @auto="onSplitAuto"
      @manual="onSplitManual"
      @cancel="onSplitCancel"
    />

    <ConfirmDialog
      :open="truncateDialogOpen"
      title="减少页数"
      message="减少页数将丢弃末尾页面的内容，是否继续？"
      confirm-text="继续"
      cancel-text="取消"
      @cancel="truncateDialogOpen = false"
      @confirm="confirmDecreasePageCount"
    />
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../../api/client'
import CardSplitModeDialog from '../../components/create/CardSplitModeDialog.vue'
import ConfirmDialog from '../../components/ConfirmDialog.vue'
import UserMenu from '../../components/create/UserMenu.vue'
import { useToast } from '../../composables/useToast.js'
import {
  applyProjectSettingsLocal,
  clearDraft,
  loadDraft,
  requireDeckDraft,
  saveDraft,
  syncPageContents,
} from '../../composables/useAiCreateDraft.js'
import { splitContentIntoPages } from '../../utils/splitContentIntoPages.js'

const router = useRouter()
const { success: toastSuccess } = useToast()
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
const contentMode = ref('free')
const cardSplitMode = ref(null)
const pageContents = ref([])
const activePageIndex = ref(0)
const splitDialogOpen = ref(false)
const truncateDialogOpen = ref(false)
const pendingPageCount = ref(null)
const generating = ref(false)
const error = ref('')

function sourceTextForSplit() {
  return (extraContent.value || draft.value.topic || '').trim()
}

function clampActivePage() {
  if (activePageIndex.value >= pageContents.value.length) {
    activePageIndex.value = Math.max(0, pageContents.value.length - 1)
  }
}

function switchToFree() {
  if (contentMode.value === 'free') return
  const merged = pageContents.value.filter((p) => p.trim()).join('\n\n')
  if (merged) extraContent.value = merged
  contentMode.value = 'free'
  cardSplitMode.value = null
}

function switchToPerPage() {
  if (contentMode.value === 'per_page') return
  if (cardSplitMode.value) {
    contentMode.value = 'per_page'
    pageContents.value = syncPageContents(pageContents.value, pageCount.value)
    return
  }
  splitDialogOpen.value = true
}

function onSplitAuto() {
  splitDialogOpen.value = false
  const source = sourceTextForSplit()
  pageContents.value = splitContentIntoPages(source, pageCount.value)
  contentMode.value = 'per_page'
  cardSplitMode.value = 'auto'
  activePageIndex.value = 0
  toastSuccess(`已按标题/序号分为 ${pageCount.value} 页，可在各页中微调`)
}

function onSplitManual() {
  splitDialogOpen.value = false
  pageContents.value = syncPageContents([], pageCount.value)
  contentMode.value = 'per_page'
  cardSplitMode.value = 'manual'
  activePageIndex.value = 0
}

function onSplitCancel() {
  splitDialogOpen.value = false
}

function decreasePageCount() {
  if (pageCount.value <= 1) return
  const next = pageCount.value - 1
  if (contentMode.value === 'per_page') {
    const tail = pageContents.value.slice(next)
    if (tail.some((p) => p.trim())) {
      pendingPageCount.value = next
      truncateDialogOpen.value = true
      return
    }
    pageContents.value = syncPageContents(pageContents.value, next)
    clampActivePage()
  }
  pageCount.value = next
}

function confirmDecreasePageCount() {
  truncateDialogOpen.value = false
  if (pendingPageCount.value != null) {
    pageCount.value = pendingPageCount.value
    pageContents.value = syncPageContents(pageContents.value, pageCount.value)
    clampActivePage()
    pendingPageCount.value = null
  }
}

function increasePageCount() {
  if (pageCount.value >= 30) return
  pageCount.value += 1
  if (contentMode.value === 'per_page') {
    pageContents.value = syncPageContents(pageContents.value, pageCount.value)
  }
}

watch(pageCount, (n) => {
  if (contentMode.value === 'per_page') {
    pageContents.value = syncPageContents(pageContents.value, n)
    clampActivePage()
  }
})

onMounted(async () => {
  const d = requireDeckDraft(router)
  if (!d) return
  if (!d.topic?.trim()) {
    router.replace('/create/generate')
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
  contentMode.value = d.contentMode || 'free'
  cardSplitMode.value = d.cardSplitMode || null
  pageContents.value = syncPageContents(d.pageContents || [], pageCount.value)
})

async function generate() {
  if (contentMode.value === 'per_page') {
    const hasAny = pageContents.value.some((p) => p.trim())
    if (!hasAny) {
      error.value = '请至少填写一页内容'
      return
    }
  }

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
    contentMode: contentMode.value,
    cardSplitMode: cardSplitMode.value,
    pageContents: pageContents.value,
  })
  try {
    const body = {
      topic: draft.value.topic,
      page_count: pageCount.value,
      audience: audience.value,
      tone: tone.value,
      text_density: textDensity.value,
      language: language.value,
      viewport_mode: draft.value.viewportMode || 'auto',
      background_preset: draft.value.background || 'classic_white',
      extra_instructions: extraInstructions.value,
      content_mode: contentMode.value,
    }
    if (contentMode.value === 'per_page') {
      body.page_contents = syncPageContents(pageContents.value, pageCount.value)
      body.extra_content = body.page_contents.filter(Boolean).join('\n\n')
    } else {
      body.extra_content = extraContent.value
      body.page_contents = []
    }
    const project = await api.generateAiDeck(body)
    applyProjectSettingsLocal(project.id, project.settings || {})
    clearDraft()
    router.push(`/editor/${project.id}`)
  } catch (e) {
    error.value = e.message || '生成失败'
    generating.value = false
  }
}
</script>
