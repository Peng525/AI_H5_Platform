<template>
  <AiCreateLayout :quota-text="quotaText">
    <div class="text-center mb-8 sm:mb-10">
      <h1 class="text-3xl sm:text-4xl font-bold text-on-surface">生成</h1>
      <p class="text-on-surface-variant mt-2 text-sm sm:text-base">您今天想创建什么？</p>
    </div>

    <div class="grid sm:grid-cols-2 gap-4 max-w-2xl mx-auto mb-8">
      <button
        type="button"
        class="text-left rounded-2xl border-2 p-5 bg-white shadow-sm transition hover:shadow-md"
        :class="type === 'deck' ? 'border-primary ring-2 ring-primary/20' : 'border-outline-variant/60'"
        @click="type = 'deck'"
      >
        <div class="h-28 rounded-xl bg-gradient-to-br from-sky-100 to-blue-200 mb-4 flex items-center justify-center">
          <span class="material-symbols-outlined text-4xl text-primary">stacked_bar_chart</span>
        </div>
        <h2 class="font-semibold text-lg">演示文稿</h2>
        <p class="text-sm text-on-surface-variant mt-1">根据提示词生成多页 H5 演示</p>
      </button>
      <button
        type="button"
        class="text-left rounded-2xl border-2 p-5 bg-white shadow-sm transition hover:shadow-md"
        :class="type === 'image' ? 'border-primary ring-2 ring-primary/20' : 'border-outline-variant/60'"
        @click="type = 'image'"
      >
        <div class="h-28 rounded-xl bg-gradient-to-br from-violet-100 to-fuchsia-200 mb-4 flex items-center justify-center">
          <span class="material-symbols-outlined text-4xl text-secondary">image</span>
        </div>
        <h2 class="font-semibold text-lg">图片</h2>
        <p class="text-sm text-on-surface-variant mt-1">AI 生成单张配图并创建项目</p>
      </button>
    </div>

    <div v-if="type === 'deck'" class="max-w-2xl mx-auto bg-white/90 rounded-2xl border border-outline-variant/60 p-5 sm:p-6 space-y-4 shadow-sm">
      <div class="grid sm:grid-cols-2 gap-4">
        <label class="block text-sm">
          <span class="font-medium text-on-surface-variant">页数</span>
          <select v-model.number="pageCount" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 bg-white">
            <option v-for="n in 10" :key="n" :value="n">{{ n }} 页</option>
          </select>
        </label>
        <label class="block text-sm">
          <span class="font-medium text-on-surface-variant">背景</span>
          <select v-model="background" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 bg-white">
            <option value="classic_white">经典白粉</option>
            <option value="light_gray">浅灰</option>
          </select>
        </label>
        <label class="block text-sm">
          <span class="font-medium text-on-surface-variant">尺寸</span>
          <select v-model="viewportMode" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 bg-white">
            <option value="auto">默认动态</option>
            <option value="web">传统网页</option>
            <option value="mobile">移动端</option>
          </select>
        </label>
        <label class="block text-sm">
          <span class="font-medium text-on-surface-variant">语言</span>
          <select v-model="language" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 bg-white">
            <option value="简体中文">简体中文</option>
            <option value="English">English</option>
          </select>
        </label>
      </div>
    </div>

    <div class="max-w-2xl mx-auto mt-8 flex flex-col sm:flex-row items-center justify-between gap-3">
      <router-link to="/create/blank" class="text-sm text-on-surface-variant hover:text-primary">
        创建空白项目
      </router-link>
      <button
        type="button"
        class="w-full sm:w-auto px-8 py-2.5 rounded-xl bg-primary text-on-primary font-medium shadow-card hover:bg-primary-container transition"
        @click="goNext"
      >
        下一步
      </button>
    </div>
  </AiCreateLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../../api/client'
import AiCreateLayout from '../../components/create/AiCreateLayout.vue'
import { loadDraft, saveDraft } from '../../composables/useAiCreateDraft.js'

const router = useRouter()
const type = ref('deck')
const pageCount = ref(10)
const background = ref('classic_white')
const viewportMode = ref('auto')
const language = ref('简体中文')
const quotaText = ref('')

onMounted(async () => {
  const draft = loadDraft()
  type.value = draft.type || 'deck'
  pageCount.value = draft.pageCount || 10
  background.value = draft.background || 'classic_white'
  viewportMode.value = draft.viewportMode || 'auto'
  language.value = draft.language || '简体中文'
  try {
    const q = await api.getQuota()
    quotaText.value = `${q.quota_remaining}/${q.quota_total}`
  } catch {
    quotaText.value = '—'
  }
})

function goNext() {
  saveDraft({
    type: type.value,
    pageCount: pageCount.value,
    background: background.value,
    viewportMode: viewportMode.value,
    language: language.value,
  })
  if (type.value === 'image') {
    router.push('/create/generate/image')
    return
  }
  router.push('/create/generate/prompt')
}
</script>
