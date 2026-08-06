<template>
  <div class="h-dvh overflow-hidden bg-surface-container-low flex flex-col">
    <header class="h-14 border-b border-outline-variant bg-white flex items-center px-4 sm:px-8 shrink-0 gap-3">
      <CreatePageHeaderNav>
        <h1 class="text-base font-semibold truncate min-w-0">提示词编辑器</h1>
      </CreatePageHeaderNav>

      <div class="flex-1 min-w-0" aria-hidden="true" />

      <UserMenu />
    </header>

    <div class="review-editor-grid flex-1 gap-0 min-h-0 overflow-x-auto overflow-y-hidden">
      <aside class="min-h-0 bg-white border-r border-outline-variant p-4 overflow-y-auto space-y-4">
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
          <textarea
            v-model="audience"
            rows="3"
            class="sidebar-field mt-1 w-full"
            placeholder="例如：企业管理层"
          />
        </label>
        <label class="block text-sm">
          <span class="text-xs font-medium text-on-surface-variant">语气</span>
          <textarea v-model="tone" rows="3" class="sidebar-field mt-1 w-full" />
        </label>
        <label v-if="!draft.pptTemplateId" class="block text-sm">
          <span class="text-xs font-medium text-on-surface-variant">演示主题</span>
          <select v-model="themeId" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 text-sm bg-white">
            <option v-for="opt in themeOptions" :key="opt.id" :value="opt.id">{{ opt.label }}</option>
          </select>
        </label>
        <label class="block text-sm">
          <span class="text-xs font-medium text-on-surface-variant">语言</span>
          <select v-model="language" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 text-sm bg-white">
            <option value="简体中文">简体中文</option>
            <option value="English">English</option>
          </select>
        </label>
        <div>
          <p class="text-xs font-medium text-on-surface-variant mb-2">页数</p>
          <div class="flex items-center gap-2">
            <button type="button" class="w-9 h-9 rounded-lg border border-outline-variant hover:bg-surface-container-low text-lg leading-none" @click="decreasePageCount">−</button>
            <span class="text-sm tabular-nums flex-1 text-center">{{ pageCount }} 张卡片</span>
            <button type="button" class="w-9 h-9 rounded-lg border border-outline-variant hover:bg-surface-container-low text-lg leading-none" @click="increasePageCount">+</button>
          </div>
        </div>
      </aside>

      <section class="flex flex-col min-h-0 overflow-hidden bg-surface-container-low">
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

        <div v-else class="flex-1 min-h-0 overflow-y-auto mx-4 mb-4 mt-2 space-y-4">
          <article
            v-for="(_, i) in pageContents"
            :key="i"
            class="rounded-xl border border-outline-variant bg-white overflow-hidden shrink-0"
          >
            <header class="px-4 py-2.5 border-b border-outline-variant bg-surface-container-low/60">
              <h3 class="text-xs font-semibold text-on-surface">页面 {{ i + 1 }}</h3>
            </header>
            <textarea
              v-model="pageContents[i]"
              class="review-page-textarea w-full min-h-[7.5rem] px-4 py-3 text-sm resize-y border-0 bg-white leading-relaxed block"
              :placeholder="`第 ${i + 1} 页内容…`"
              rows="6"
            />
          </article>
        </div>
      </section>

      <aside class="min-h-0 bg-white border-l border-outline-variant p-4 overflow-y-auto space-y-4">
        <h2 class="text-sm font-semibold">说明</h2>
        <label class="block text-sm">
          <span class="text-xs font-medium text-on-surface-variant">附加说明</span>
          <textarea v-model="extraInstructions" rows="4" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 text-sm resize-none" placeholder="可选" />
        </label>
        <p class="text-xs text-on-surface-variant leading-relaxed">
          点击「生成」后，AI 将根据您的提示词与设置创建完整演示结构，并进入生成结果页继续微调与保存评估包。
        </p>
      </aside>
    </div>

    <footer class="shrink-0 border-t border-outline-variant bg-white py-3">
      <div class="relative flex items-center justify-between px-4 sm:px-6 min-h-[2.75rem]">
        <p class="text-sm text-on-surface-variant tabular-nums shrink-0 z-10">
          配额 {{ quotaText }}
        </p>
        <div class="absolute inset-x-0 flex items-center justify-center pointer-events-none px-4">
          <div class="relative pointer-events-auto">
            <p class="absolute right-full top-1/2 -translate-y-1/2 mr-3 whitespace-nowrap text-sm text-on-surface-variant tabular-nums">
              共 {{ pageCount }} 张卡片
            </p>
            <button
              type="button"
              class="min-w-[11rem] px-12 sm:px-14 py-2.5 rounded-full bg-primary text-on-primary font-medium inline-flex items-center justify-center gap-2 disabled:opacity-50 whitespace-nowrap shrink-0"
              :disabled="generating"
              @click="generate"
            >
              <span class="material-symbols-outlined text-[18px]">auto_awesome</span>
              {{ generating ? '生成中…' : '生成演示文稿' }}
            </button>
          </div>
        </div>
        <button
          type="button"
          class="px-5 py-2.5 rounded-lg border border-outline-variant bg-white text-sm font-medium hover:bg-surface-container-low transition whitespace-nowrap shrink-0 z-10"
          @click="save"
        >
          保存
        </button>
      </div>
      <p v-if="error" class="text-sm text-red-600 mt-2 text-center px-4">{{ error }}</p>
      <p v-if="premiumEstimateHint" class="text-xs text-on-surface-variant mt-1 text-center px-4">{{ premiumEstimateHint }}</p>
    </footer>

    <CardSplitModeDialog
      :open="splitDialogOpen"
      :page-count="pageCount"
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
import { computed, onActivated, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import CardSplitModeDialog from '../../components/create/CardSplitModeDialog.vue'
import ConfirmDialog from '../../components/ConfirmDialog.vue'
import CreatePageHeaderNav from '../../components/create/CreatePageHeaderNav.vue'
import UserMenu from '../../components/create/UserMenu.vue'
import { useToast } from '../../composables/useToast.js'
import { useQuota } from '../../composables/useQuota.js'
import {
  clearReturnToResult,
  loadDraft,
  normalizeDeckReviewDraftState,
  PENDING_RESULT_PUBLIC_ID,
  requireDeckDraft,
  saveDraft,
  saveGenerateJob,
  syncPageContents,
} from '../../composables/useAiCreateDraft.js'
import {
  estimatePremiumDeckRange,
  estimateQuickDeckSeconds,
  formatPremiumDeckRangeLabel,
} from '../../utils/deckGenerateEstimate.js'
import { listThemeOptions } from '../../utils/applyProjectTheme.js'
import { splitContentIntoPages } from '../../utils/splitContentIntoPages.js'

defineOptions({ name: 'AiGenerateReview' })

const router = useRouter()
const { success: toastSuccess } = useToast()
const { quotaText } = useQuota()
const draft = ref(loadDraft())
const densityOptions = ['简约', '精炼', '详细', '繁琐']

const pageCount = ref(10)
const textDensity = ref('精炼')
const audience = ref('')
const tone = ref('专业、清晰、具说服力')
const language = ref('简体中文')
const themeId = ref('zjy-minimal')
const themeOptions = listThemeOptions()
const extraContent = ref('')
const extraInstructions = ref('')
const contentMode = ref('free')
const cardSplitMode = ref(null)
const pageContents = ref([])
const splitDialogOpen = ref(false)
const truncateDialogOpen = ref(false)
const pendingPageCount = ref(null)
const generating = ref(false)
const error = ref('')

const estimatedSeconds = computed(() => {
  if (draft.value.pptTemplateId) {
    return estimatePremiumDeckRange(pageCount.value).typicalSeconds
  }
  return estimateQuickDeckSeconds(pageCount.value)
})

const premiumEstimateHint = computed(() => {
  if (!draft.value.pptTemplateId) return ''
  return `高质量生成约 ${formatPremiumDeckRangeLabel(pageCount.value)}`
})

function sourceTextForSplit() {
  return (extraContent.value || draft.value.topic || '').trim()
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
  toastSuccess(`已按 ${pageCount.value} 页拆分，可在各页中微调`)
}

function onSplitManual() {
  splitDialogOpen.value = false
  pageContents.value = syncPageContents([], pageCount.value)
  contentMode.value = 'per_page'
  cardSplitMode.value = 'manual'
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
  }
  pageCount.value = next
}

function confirmDecreasePageCount() {
  truncateDialogOpen.value = false
  if (pendingPageCount.value != null) {
    pageCount.value = pendingPageCount.value
    pageContents.value = syncPageContents(pageContents.value, pageCount.value)
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
  }
})

function hydrateFromDraft() {
  const d = requireDeckDraft(router)
  if (!d) return
  if (!d.topic?.trim()) {
    router.replace('/create/generate')
    return
  }
  draft.value = d
  const state = normalizeDeckReviewDraftState(d)
  pageCount.value = state.pageCount
  textDensity.value = state.textDensity
  audience.value = state.audience
  tone.value = state.tone
  language.value = state.language
  themeId.value = state.themeId
  extraContent.value = state.extraContent
  extraInstructions.value = state.extraInstructions
  contentMode.value = state.contentMode
  cardSplitMode.value = state.cardSplitMode
  pageContents.value = state.pageContents
}

onMounted(hydrateFromDraft)
onActivated(hydrateFromDraft)

function buildDraftPatch() {
  return {
    pageCount: pageCount.value,
    textDensity: textDensity.value,
    audience: audience.value,
    tone: tone.value,
    language: language.value,
    themeId: themeId.value,
    extraContent: extraContent.value,
    extraInstructions: extraInstructions.value,
    contentMode: contentMode.value,
    cardSplitMode: cardSplitMode.value,
    pageContents: pageContents.value,
  }
}

function save() {
  saveDraft(buildDraftPatch())
  error.value = ''
  toastSuccess('草稿已保存')
}

function buildGenerateBody() {
  let topic = (draft.value.topic || '').trim()
  if (!topic && contentMode.value === 'per_page') {
    const firstPage = pageContents.value.find((p) => String(p || '').trim())
    topic = String(firstPage || '演示文稿').trim().slice(0, 8000)
  }
  const body = {
    topic,
    page_count: pageCount.value,
    audience: audience.value,
    tone: tone.value,
    text_density: textDensity.value,
    language: language.value,
    viewport_mode: draft.value.viewportMode || 'auto',
    background_preset: draft.value.background ?? '',
    theme_id: themeId.value || draft.value.themeId || 'zjy-minimal',
    extra_instructions: extraInstructions.value,
    content_mode: contentMode.value,
    ppt_template_id: draft.value.pptTemplateId || null,
    ppt_template_kind: draft.value.pptTemplateKind || null,
    strict_template_mode: true,  // 默认启用严格PPT模板约束
  }
  if (contentMode.value === 'per_page') {
    body.page_contents = syncPageContents(pageContents.value, pageCount.value)
    body.extra_content = body.page_contents.filter(Boolean).join('\n\n')
  } else {
    body.extra_content = extraContent.value
    body.page_contents = []
  }
  return body
}

function generate() {
  if (contentMode.value === 'per_page') {
    const hasAny = pageContents.value.some((p) => p.trim())
    if (!hasAny) {
      error.value = '请至少填写一页内容'
      return
    }
  }

  generating.value = true
  error.value = ''
  clearReturnToResult()
  saveDraft({ ...buildDraftPatch(), themeId: themeId.value })
  const body = buildGenerateBody()
  saveGenerateJob(body, { estimatedSeconds: estimatedSeconds.value })
  router.push(`/create/generate/result/${PENDING_RESULT_PUBLIC_ID}`)
</script>

<style scoped>
.review-editor-grid {
  display: grid;
  grid-template-columns:
    minmax(190px, clamp(190px, 22vw, 260px))
    minmax(420px, 1fr)
    minmax(180px, clamp(180px, 20vw, 240px));
}

@media (max-width: 900px) {
  .review-editor-grid {
    grid-template-columns: minmax(170px, 0.75fr) minmax(360px, 1.65fr) minmax(170px, 0.7fr);
  }
}

.sidebar-field {
  @apply border border-outline-variant rounded-lg px-3 py-2 text-sm leading-relaxed resize-none overflow-y-auto;
  @apply focus:outline-none focus:ring-1 focus:ring-primary/30 focus:border-primary/40;
}

.review-page-textarea {
  @apply focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary/20;
}
</style>
