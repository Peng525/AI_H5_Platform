<template>
  <div class="h-screen flex flex-col bg-background overflow-hidden">
    <EditorTopBar project-title="探索模板" />
    <div class="flex flex-1 min-h-0">
      <!-- 左侧工具箱 -->
      <aside class="w-14 md:w-52 border-r border-outline-variant bg-surface-container-low flex flex-col shrink-0">
        <div class="p-3 hidden md:block">
          <p class="text-xs font-semibold text-on-surface-variant">工具箱</p>
          <p class="text-xs text-on-surface-variant">编辑器</p>
        </div>
        <nav class="flex-1 flex md:flex-col">
          <router-link
            v-for="item in tools"
            :key="item.id"
            :to="item.to"
            class="flex md:flex-row flex-col items-center gap-1 md:gap-2 px-2 md:px-4 py-3 text-xs md:text-sm"
            :class="$route.path.startsWith(item.match) ? 'bg-white text-primary font-medium' : 'text-on-surface-variant'"
          >
            <span class="material-symbols-outlined">{{ item.icon }}</span>
            <span class="hidden md:inline">{{ item.label }}</span>
          </router-link>
        </nav>
        <div class="p-3 border-t border-outline-variant hidden md:block">
          <p class="text-xs text-on-surface-variant mb-1">配额</p>
          <div class="h-1.5 bg-outline-variant/30 rounded-full">
            <div class="h-full bg-secondary rounded-full" :style="{ width: quotaPct + '%' }" />
          </div>
          <p class="text-xs mt-1">剩余 {{ quota.remaining }}/{{ quota.total }}</p>
        </div>
      </aside>

      <!-- 中间模板区 -->
      <main class="flex-1 overflow-y-auto p-6">
        <h1 class="text-2xl font-bold mb-4">探索模板</h1>
        <div class="flex flex-wrap gap-2 mb-4">
          <input
            v-model="search"
            class="flex-1 min-w-[200px] border border-outline-variant rounded-lg px-3 py-2 text-sm"
            placeholder="搜索模板…"
            @keyup.enter="load"
          />
          <button class="px-4 py-2 bg-primary text-on-primary rounded-lg text-sm" @click="load">搜索</button>
        </div>
        <div class="flex flex-wrap gap-2 mb-6">
          <button
            v-for="c in categories"
            :key="c"
            class="px-3 py-1.5 rounded-full text-sm border"
            :class="category === c ? 'bg-primary text-on-primary border-primary' : 'border-outline-variant'"
            @click="category = c; load()"
          >
            {{ c }}
          </button>
        </div>

        <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <article
            v-for="t in templates"
            :key="t.id"
            class="bg-white rounded-xl border border-outline-variant overflow-hidden shadow-card hover:shadow-lg transition"
          >
            <div class="h-36 bg-gradient-to-br" :class="t.cover_gradient" />
            <div class="p-4">
              <div class="flex items-start justify-between gap-2">
                <h3 class="font-semibold">{{ t.title }}</h3>
                <span v-if="t.premium" class="text-xs bg-amber-100 text-amber-800 px-2 py-0.5 rounded">Premium</span>
              </div>
              <p class="text-sm text-on-surface-variant mt-2 line-clamp-2">{{ t.description }}</p>
              <p class="text-xs text-on-surface-variant mt-2">{{ t.pages }} 页</p>
              <button
                class="mt-3 w-full py-2 bg-primary text-on-primary rounded-lg text-sm font-medium"
                @click="useTemplate(t)"
              >
                使用此模板
              </button>
            </div>
          </article>

          <article class="bg-surface-container-low rounded-xl border border-dashed border-outline-variant p-6 flex flex-col items-center justify-center text-center min-h-[280px]">
            <span class="material-symbols-outlined text-4xl text-primary mb-2">auto_awesome</span>
            <h3 class="font-semibold">没有找到合适的？</h3>
            <p class="text-sm text-on-surface-variant mt-2 mb-4">输入需求，让 AI 定制专属 H5</p>
            <router-link to="/create" class="px-4 py-2 bg-primary text-on-primary rounded-lg text-sm font-medium">
              AI 生成模板
            </router-link>
          </article>
        </div>
      </main>

      <AiPanel :quota-remaining="quota.remaining" :quota-total="quota.total" @generate="onAiGenerate" />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'
import { useAuth } from '../composables/useAuth'
import AiPanel from '../components/AiPanel.vue'
import EditorTopBar from '../components/EditorTopBar.vue'

const router = useRouter()
const { user } = useAuth()
const categories = ref(['全部'])
const category = ref('全部')
const search = ref('')
const templates = ref([])
const quota = ref({ remaining: 5, total: 5 })

const tools = [
  { id: 'tpl', label: '模板', icon: 'grid_view', to: '/templates', match: '/templates' },
  { id: 'create', label: '页面', icon: 'layers', to: '/create', match: '/create' },
  { id: 'settings', label: '设置', icon: 'settings', to: '/settings', match: '/settings' },
]

const quotaPct = computed(() => (quota.value.remaining / quota.value.total) * 100)

onMounted(async () => {
  const [cats, q] = await Promise.all([
    api.getTemplateCategories(),
    api.getQuota(user.value?.user_id),
  ])
  categories.value = cats.items
  quota.value = { remaining: q.quota_remaining, total: q.quota_total }
  await load()
})

async function load() {
  const res = await api.listTemplates(category.value, search.value)
  templates.value = res.items
}

async function useTemplate(t) {
  const p = await api.createProject({ title: t.title, theme: t.id }, user.value?.user_id)
  router.push(`/editor/${p.id}`)
}

function onAiGenerate() {
  router.push('/create')
}
</script>
