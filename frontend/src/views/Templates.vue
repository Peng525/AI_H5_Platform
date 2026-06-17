<template>
  <div>
    <div class="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-10 w-full">
      <div class="space-y-6 mb-8">
        <div class="space-y-1">
          <div class="flex items-center gap-2 min-w-0">
            <span class="material-symbols-outlined text-[22px] text-on-surface-variant">dashboard_customize</span>
            <h1 class="text-xl font-bold text-on-surface">模板库</h1>
          </div>
          <p class="text-sm text-on-surface-variant">
            探索模板，快速创建 H5 演示
          </p>
        </div>

        <div class="flex items-center gap-2.5 w-full max-w-md">
          <div class="relative flex-1 min-w-0">
            <span
              class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[18px] text-on-surface-variant pointer-events-none"
              aria-hidden="true"
            >
              search
            </span>
            <input
              v-model="search"
              type="search"
              enterkeyhint="search"
              class="w-full pl-10 pr-3 py-2 text-sm border border-outline-variant rounded-lg bg-white"
              placeholder="搜索模板名称或关键词…"
              @keyup.enter="load"
            />
          </div>
          <button
            type="button"
            class="shrink-0 px-5 py-2 rounded-full bg-primary text-on-primary text-sm font-medium hover:bg-primary/90 transition"
            @click="load"
          >
            搜索
          </button>
        </div>

        <div class="flex flex-wrap gap-2">
          <button
            v-for="opt in filterOptions"
            :key="`${opt.type}-${opt.id}`"
            type="button"
            class="whitespace-nowrap"
            :class="isFilterActive(opt) ? filterChipActive : filterChipDefault"
            @click="selectFilter(opt)"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>

      <PageLoading v-if="loading" />

      <EmptyState
        v-else-if="loadError"
        icon="error"
        title="模板加载失败"
        :description="loadError"
        action-label="重试"
        @action="initPage"
      />

      <div
        v-else-if="templates.length === 0"
        class="text-center py-20 bg-surface-container-low rounded-xl border border-dashed border-outline-variant"
      >
        <span class="material-symbols-outlined text-5xl text-on-surface-variant/40">dashboard_customize</span>
        <p class="text-sm text-on-surface-variant mt-4 mb-4">未找到匹配的模板，请调整筛选或关键词</p>
        <router-link to="/create/generate" class="text-sm text-primary font-medium hover:underline">
          新建演示 →
        </router-link>
      </div>

      <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <article
          v-for="t in templates"
          :key="t.id"
          class="bg-white rounded-xl border border-outline-variant overflow-hidden shadow-card hover:shadow-lg transition group relative cursor-pointer"
          @click="askUseTemplate(t)"
        >
          <TemplateCoverThumb :template="t" />

          <div class="p-4">
            <div class="flex items-start gap-2 flex-1 min-w-0">
              <h2 class="font-semibold truncate group-hover:text-primary transition-colors flex-1 min-w-0">
                {{ t.title }}
              </h2>
              <span
                v-if="t.premium"
                class="text-xs bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full shrink-0"
              >
                高级
              </span>
            </div>
            <p class="text-sm text-on-surface-variant mt-1">{{ t.category }} · {{ t.pages }} 页</p>
          </div>
        </article>
      </div>
    </div>

    <ConfirmDialog
      :open="createDialog.open"
      title="使用此模板？"
      :message="createDialogMessage"
      confirm-text="创建"
      cancel-text="取消"
      :loading="createDialog.loading"
      @cancel="closeCreateDialog"
      @confirm="confirmUseTemplate"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'
import { openProjectInResult } from '../composables/useAiCreateDraft.js'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import EmptyState from '../components/EmptyState.vue'
import PageLoading from '../components/PageLoading.vue'
import TemplateCoverThumb from '../components/TemplateCoverThumb.vue'

const SETTINGS_PREFIX = 'ai_h5_project_settings_'
const CANVAS_PREFIX = 'ai_h5_canvas_'

const router = useRouter()
const categories = ref(['全部'])
const category = ref('全部')
const device = ref('全部')
const search = ref('')
const templates = ref([])
const loading = ref(true)
const loadError = ref('')

const createDialog = reactive({
  open: false,
  loading: false,
  template: null,
})

const filterChipDefault =
  'text-xs px-3 py-1.5 rounded-full bg-surface-container-high text-on-surface-variant hover:bg-surface-container-high/80 transition'
const filterChipActive =
  'text-xs px-3 py-1.5 rounded-full bg-blue-100 text-blue-800 font-medium transition'

const filterOptions = computed(() => {
  const opts = [
    { type: 'all', id: '全部', label: '全部' },
    { type: 'device', id: 'mobile', label: '移动端' },
    { type: 'device', id: 'web', label: '网页版' },
  ]
  for (const c of categories.value) {
    if (c !== '全部') opts.push({ type: 'category', id: c, label: c })
  }
  return opts
})

const createDialogMessage = computed(() => {
  const title = createDialog.template?.title || '该模板'
  return `将基于「${title}」创建新项目并进入编辑器。`
})

onMounted(() => {
  void initPage()
})

function isFilterActive(opt) {
  if (opt.type === 'all') return category.value === '全部' && device.value === '全部'
  if (opt.type === 'device') return device.value === opt.id && category.value === '全部'
  return category.value === opt.id && device.value === '全部'
}

function selectFilter(opt) {
  if (opt.type === 'all') {
    category.value = '全部'
    device.value = '全部'
  } else if (opt.type === 'device') {
    category.value = '全部'
    device.value = opt.id
  } else {
    category.value = opt.id
    device.value = '全部'
  }
  void load()
}

function askUseTemplate(t) {
  createDialog.template = t
  createDialog.open = true
}

function closeCreateDialog() {
  if (createDialog.loading) return
  createDialog.open = false
  createDialog.template = null
}

async function initPage() {
  loading.value = true
  loadError.value = ''
  try {
    const [cats, res] = await Promise.all([
      api.getTemplateCategories(),
      api.listTemplates(category.value, search.value, device.value),
    ])
    categories.value = cats.items
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

async function confirmUseTemplate() {
  if (!createDialog.template || createDialog.loading) return
  createDialog.loading = true
  try {
    await useTemplate(createDialog.template)
    createDialog.open = false
    createDialog.template = null
  } catch (e) {
    loadError.value = e.message || '创建失败'
    createDialog.open = false
    createDialog.template = null
  } finally {
    createDialog.loading = false
  }
}

async function useTemplate(t) {
  if (!t) return
  const p = await api.createProject({
    title: t.title,
    theme: t.id,
    template_id: t.id,
  })
  const settings = p.settings || {}
  localStorage.setItem(
    `${SETTINGS_PREFIX}${p.public_id}`,
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
      localStorage.setItem(`${CANVAS_PREFIX}${p.public_id}_${slide.id}`, JSON.stringify(slide.canvas_elements))
    }
  }
  const path = openProjectInResult(p.public_id)
  if (path) router.push(path)
}
</script>
