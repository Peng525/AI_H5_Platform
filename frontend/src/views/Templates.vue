<template>
  <div class="min-h-screen bg-background flex flex-col">
    <AppShell />

    <div class="max-w-7xl mx-auto px-3 py-4 sm:p-6 md:p-10 flex-1 w-full min-w-0">
      <div class="mb-5 sm:mb-8">
        <h1 class="text-xl sm:text-2xl md:text-3xl font-bold">探索模板</h1>
      </div>

      <div class="flex flex-col sm:flex-row gap-2 mb-5">
        <div class="flex-1 min-w-0">
          <input
            v-model="search"
            type="search"
            enterkeyhint="search"
            class="w-full border border-outline-variant rounded-lg px-3 py-2.5 text-sm bg-white"
            placeholder="搜索模板名称或关键词…"
            @keyup.enter="load"
          />
        </div>
        <button
          type="button"
          class="w-full sm:w-auto shrink-0 px-5 py-2.5 bg-primary text-on-primary rounded-lg text-sm font-medium"
          @click="load"
        >
          搜索
        </button>
      </div>

      <div class="mb-4">
        <p class="text-xs font-medium text-on-surface-variant mb-2">终端类型</p>
        <div class="flex flex-wrap gap-1.5 sm:gap-2">
          <button
            v-for="d in devices"
            :key="d.id"
            type="button"
            class="px-2.5 sm:px-3 py-1.5 rounded-full text-xs sm:text-sm border whitespace-nowrap"
            :class="device === d.id ? 'bg-secondary text-white border-secondary' : 'border-outline-variant hover:bg-white bg-white'"
            @click="device = d.id; load()"
          >
            {{ d.label }}
          </button>
        </div>
      </div>

      <div class="mb-6">
        <p class="text-xs font-medium text-on-surface-variant mb-2">模板类型</p>
        <div class="flex flex-wrap gap-1.5 sm:gap-2">
          <button
            v-for="c in categories"
            :key="c"
            type="button"
            class="px-2.5 sm:px-3 py-1.5 rounded-full text-xs sm:text-sm border whitespace-nowrap"
            :class="category === c ? 'bg-primary text-on-primary border-primary' : 'border-outline-variant hover:bg-white bg-white'"
            @click="category = c; load()"
          >
            {{ c }}
          </button>
        </div>
      </div>

      <div v-if="loading" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3" aria-busy="true" aria-label="模板加载中">
        <article
          v-for="i in 6"
          :key="i"
          class="bg-white rounded-xl border border-outline-variant overflow-hidden animate-pulse"
        >
          <div class="h-36 bg-surface-container-high" />
          <div class="p-4 space-y-2">
            <div class="h-4 bg-surface-container-high rounded w-2/3" />
            <div class="h-3 bg-surface-container-high rounded w-1/3" />
            <div class="h-3 bg-surface-container-high rounded w-full" />
          </div>
        </article>
      </div>

      <EmptyState
        v-else-if="loadError"
        icon="error"
        title="模板加载失败"
        :description="loadError"
        action-label="重试"
        @action="initPage"
      />

      <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <article
          v-for="t in templates"
          :key="t.id"
          class="bg-white rounded-xl border border-outline-variant overflow-hidden shadow-card hover:shadow-lg transition group"
        >
          <TemplateCoverThumb :template="t" />
          <div class="p-4">
            <div class="flex items-start justify-between gap-2">
              <h3 class="font-semibold group-hover:text-primary transition-colors">{{ t.title }}</h3>
              <span v-if="t.premium" class="text-xs bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full shrink-0">高级</span>
            </div>
            <p class="text-xs text-on-surface-variant mt-1">{{ t.category }}</p>
            <p class="text-sm text-on-surface-variant mt-2 line-clamp-2">{{ t.description }}</p>
            <p class="text-xs text-on-surface-variant mt-2">{{ t.pages }} 页</p>
            <div class="mt-3 flex gap-2">
              <button
                type="button"
                class="flex-1 py-2 border border-outline-variant rounded-lg text-sm font-medium hover:bg-surface-container-low"
                @click="openPreview(t)"
              >
                预览
              </button>
              <button
                type="button"
                class="flex-1 py-2 bg-primary text-on-primary rounded-lg text-sm font-medium"
                @click="useTemplate(t)"
              >
                使用
              </button>
            </div>
          </div>
        </article>

        <article
          v-if="templates.length === 0"
          class="sm:col-span-2 lg:col-span-3 bg-surface-container-low rounded-xl border border-dashed border-outline-variant p-10 text-center"
        >
          <p class="text-3xl text-on-surface-variant/30 font-light">暂无</p>
          <p class="text-on-surface-variant mt-3">未找到匹配的模板，请调整筛选或关键词</p>
        </article>

        <article class="bg-surface-container-low rounded-xl border border-dashed border-outline-variant p-6 flex flex-col items-center justify-center text-center min-h-[280px]">
          <p class="text-3xl text-primary font-light mb-2">＋</p>
          <h3 class="font-semibold">没有找到合适的？</h3>
          <p class="text-sm text-on-surface-variant mt-2 mb-4">创建空白项目，在编辑器中用 AI 生图</p>
          <router-link to="/create" class="px-4 py-2 bg-primary text-on-primary rounded-lg text-sm font-medium">
            新建演示
          </router-link>
        </article>
      </div>
    </div>

    <TemplatePreviewModal
      v-if="previewMounted"
      :open="previewOpen"
      :template="previewTemplate"
      @close="previewOpen = false"
      @use="useTemplate(previewTemplate)"
    />
  </div>
</template>

<script setup>
import { defineAsyncComponent, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'
import AppShell from '../components/AppShell.vue'
import EmptyState from '../components/EmptyState.vue'
import TemplateCoverThumb from '../components/TemplateCoverThumb.vue'

const TemplatePreviewModal = defineAsyncComponent(() => import('../components/TemplatePreviewModal.vue'))

const SETTINGS_PREFIX = 'ai_h5_project_settings_'
const CANVAS_PREFIX = 'ai_h5_canvas_'

const router = useRouter()
const categories = ref(['全部'])
const devices = ref([
  { id: '全部', label: '全部终端' },
  { id: 'mobile', label: '移动端' },
  { id: 'web', label: '网页版' },
])
const category = ref('全部')
const device = ref('全部')
const search = ref('')
const templates = ref([])
const loading = ref(true)
const loadError = ref('')
const previewOpen = ref(false)
const previewTemplate = ref(null)
const previewMounted = ref(false)

onMounted(() => {
  void initPage()
})

watch(previewOpen, (open) => {
  if (open) previewMounted.value = true
})

async function initPage() {
  loading.value = true
  loadError.value = ''
  try {
    const [cats, res] = await Promise.all([
      api.getTemplateCategories(),
      api.listTemplates(category.value, search.value, device.value),
    ])
    categories.value = cats.items
    if (cats.devices?.length) devices.value = cats.devices
    templates.value = res.items
  } catch (e) {
    loadError.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    const res = await api.listTemplates(category.value, search.value, device.value)
    templates.value = res.items
  } catch (e) {
    loadError.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

function openPreview(t) {
  previewTemplate.value = t
  previewOpen.value = true
}

async function useTemplate(t) {
  if (!t) return
  previewOpen.value = false
  const p = await api.createProject({
    title: t.title,
    theme: t.id,
    template_id: t.id,
  })
  const settings = p.settings || {}
  localStorage.setItem(
    `${SETTINGS_PREFIX}${p.id}`,
    JSON.stringify({
      viewportId: settings.viewportId || t.default_viewport || (t.device === 'web' ? 'web-1280' : 'mobile-375'),
      scrollEffect: settings.scrollEffect || 'vertical',
      themeId: settings.themeId || 'zjy-minimal',
      showScrollHint: settings.showScrollHint === true,
      slideBackgrounds: settings.slideBackgrounds || {},
      bgm: settings.bgm || { enabled: false, trackId: '', url: '', loop: true, volume: 0.35 },
      defaultChatTapToContinue: settings.defaultChatTapToContinue !== false,
    })
  )
  for (const slide of p.slides || []) {
    if (slide.canvas_elements?.length) {
      localStorage.setItem(`${CANVAS_PREFIX}${p.id}_${slide.id}`, JSON.stringify(slide.canvas_elements))
    }
  }
  router.push(`/editor/${p.id}`)
}
</script>
