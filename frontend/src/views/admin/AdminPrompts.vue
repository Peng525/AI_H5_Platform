<template>
  <AdminShell title="文稿提示词">
    <p v-if="loading" class="text-on-surface-variant">加载中…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>

    <div v-else class="flex flex-col min-h-[calc(100vh-8rem)]">
      <!-- 移动端 Tab -->
      <div class="lg:hidden flex gap-1 p-1 mb-4 bg-surface-container-low rounded-lg text-sm">
        <button
          v-for="tab in mobileTabs"
          :key="tab.id"
          type="button"
          class="flex-1 py-2 rounded-md transition-colors"
          :class="mobileTab === tab.id ? 'bg-white shadow-sm text-primary font-medium' : 'text-on-surface-variant'"
          @click="mobileTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="flex-1 grid lg:grid-cols-[280px_1fr_260px] gap-4 lg:gap-5 min-h-0">
        <!-- 左栏：设置 -->
        <aside
          class="flex flex-col gap-4 min-h-0 overflow-y-auto"
          :class="mobileTab !== 'settings' && 'hidden lg:flex'"
        >
          <div class="flex items-center justify-between gap-2">
            <h3 class="text-sm font-semibold text-on-surface">设置</h3>
            <button
              type="button"
              class="text-xs px-2.5 py-1 rounded-lg bg-primary text-on-primary font-medium"
              @click="openCreate"
            >
              新建模板
            </button>
          </div>

          <div class="space-y-2">
            <button
              v-for="t in templates"
              :key="t.id"
              type="button"
              class="w-full text-left px-3 py-2.5 rounded-xl border transition-colors text-sm"
              :class="selectedId === t.id
                ? 'border-primary bg-primary/5 text-primary font-medium'
                : 'border-outline-variant bg-white hover:bg-surface-container-low'"
              @click="select(t.id)"
            >
              <span class="flex items-center justify-between gap-2">
                <span class="truncate">{{ t.name }}</span>
                <span v-if="t.builtin" class="text-[10px] shrink-0 text-on-surface-variant">内置</span>
              </span>
            </button>
          </div>

          <div v-if="detail" class="bg-white rounded-xl border border-outline-variant p-4 space-y-3 text-sm">
            <label class="block">
              <span class="text-xs font-medium text-on-surface-variant">模板 ID</span>
              <input
                v-model="form.id"
                :disabled="dialogMode === 'edit' && detail.builtin"
                class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 text-xs font-mono disabled:bg-surface-container-low"
              />
            </label>
            <label class="block">
              <span class="text-xs font-medium text-on-surface-variant">名称</span>
              <input v-model="form.name" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2" />
            </label>
            <label class="block">
              <span class="text-xs font-medium text-on-surface-variant">描述</span>
              <textarea
                v-model="form.description"
                rows="3"
                class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 text-sm resize-none"
              />
            </label>
          </div>
        </aside>

        <!-- 中栏：内容 -->
        <main
          class="flex flex-col min-h-0 bg-white rounded-xl border border-outline-variant overflow-hidden"
          :class="mobileTab !== 'content' && 'hidden lg:flex'"
        >
          <div class="px-4 pt-4 pb-2 border-b border-outline-variant shrink-0">
            <h3 class="text-sm font-semibold text-on-surface mb-3">内容</h3>
            <div class="inline-flex p-0.5 bg-surface-container-low rounded-lg text-sm">
              <button
                v-for="tab in contentTabs"
                :key="tab.id"
                type="button"
                class="px-4 py-1.5 rounded-md transition-colors"
                :class="contentTab === tab.id ? 'bg-white shadow-sm text-primary font-medium' : 'text-on-surface-variant'"
                @click="contentTab = tab.id"
              >
                {{ tab.label }}
              </button>
            </div>
          </div>

          <div v-if="detail" class="flex-1 min-h-0 p-4">
            <textarea
              v-show="contentTab === 'system'"
              v-model="form.system"
              class="w-full h-full min-h-[280px] lg:min-h-[420px] border border-outline-variant rounded-xl px-4 py-3 font-mono text-sm leading-relaxed resize-none focus:outline-none focus:ring-2 focus:ring-primary/20"
              placeholder="System 提示词：定义 AI 角色与输出格式约束…"
            />
            <textarea
              v-show="contentTab === 'user'"
              v-model="form.user"
              class="w-full h-full min-h-[280px] lg:min-h-[420px] border border-outline-variant rounded-xl px-4 py-3 font-mono text-sm leading-relaxed resize-none focus:outline-none focus:ring-2 focus:ring-primary/20"
              placeholder="User 提示词：用户侧指令模板，支持 Jinja2 变量…"
            />
          </div>
          <div v-else class="flex-1 flex items-center justify-center text-sm text-on-surface-variant p-8">
            请选择或新建模板
          </div>
        </main>

        <!-- 右栏：说明 -->
        <aside
          class="flex flex-col gap-4 min-h-0 overflow-y-auto"
          :class="mobileTab !== 'help' && 'hidden lg:flex'"
        >
          <div class="bg-white rounded-xl border border-outline-variant p-4">
            <h3 class="text-sm font-semibold text-on-surface mb-2">附加说明</h3>
            <p class="text-xs text-on-surface-variant leading-relaxed">
              文稿提示词用于 AI 全量生成与单页改写，与生图提示词模板无关。修改后保存即写入 YAML 文件。
            </p>
          </div>
          <div class="bg-white rounded-xl border border-outline-variant p-4">
            <h3 class="text-sm font-semibold text-on-surface mb-2">提示</h3>
            <ul class="text-xs text-on-surface-variant space-y-2 leading-relaxed">
              <li>System 定义角色、输出格式（如 JSON schema）与硬性约束。</li>
              <li>User 为每次请求的用户侧模板，可引用变量。</li>
              <li>内置模板 ID 不可修改，但内容可编辑。</li>
            </ul>
          </div>
          <div class="bg-surface-container-low rounded-xl border border-outline-variant p-4">
            <h3 class="text-sm font-semibold text-on-surface mb-2">Jinja2 变量</h3>
            <div class="flex flex-wrap gap-1.5">
              <code
                v-for="v in sampleVars"
                :key="v"
                class="text-[11px] px-2 py-0.5 bg-white border border-outline-variant rounded-md font-mono"
              >{{ v }}</code>
            </div>
          </div>
        </aside>
      </div>

      <!-- 底部操作条 -->
      <div
        v-if="detail"
        class="sticky bottom-0 mt-4 py-3 px-4 bg-white border border-outline-variant rounded-xl flex flex-wrap items-center justify-between gap-3 shadow-sm"
      >
        <p v-if="saveError" class="text-red-600 text-sm flex-1 min-w-0">{{ saveError }}</p>
        <div v-else class="text-xs text-on-surface-variant hidden sm:block">
          {{ detail.name }} · {{ dialogMode === 'create' ? '新建' : '编辑中' }}
        </div>
        <div class="flex gap-2 ml-auto">
          <button
            v-if="detail && !detail.builtin && dialogMode === 'edit'"
            type="button"
            class="px-4 py-2 border border-red-200 text-red-600 rounded-lg text-sm"
            @click="remove"
          >
            删除
          </button>
          <button
            type="button"
            class="px-6 py-2 bg-primary text-on-primary rounded-lg text-sm font-medium disabled:opacity-50"
            :disabled="saving"
            @click="save"
          >
            {{ saving ? '保存中…' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <ConfirmDialog
      :open="!!deleteConfirm"
      title="删除提示词模板"
      :message="deleteConfirm?.message || ''"
      confirm-text="删除"
      cancel-text="取消"
      danger
      @confirm="onDeleteConfirm"
      @cancel="deleteConfirm = null"
    />
  </AdminShell>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../../api/client'
import AdminShell from '../../components/AdminShell.vue'
import ConfirmDialog from '../../components/ConfirmDialog.vue'

const templates = ref([])
const selectedId = ref('')
const detail = ref(null)
const loading = ref(true)
const error = ref('')
const saving = ref(false)
const deleteConfirm = ref(null)
const saveError = ref('')
const dialogMode = ref('edit')
const contentTab = ref('system')
const mobileTab = ref('content')
const form = reactive({ id: '', name: '', description: '', system: '', user: '' })

const mobileTabs = [
  { id: 'settings', label: '模板' },
  { id: 'content', label: '内容' },
  { id: 'help', label: '说明' },
]

const contentTabs = [
  { id: 'system', label: 'System' },
  { id: 'user', label: 'User' },
]

const sampleVars = ['{{ topic }}', '{{ page_count }}', '{{ instruction }}']

onMounted(async () => {
  try {
    const res = await api.getPromptTemplates()
    templates.value = res.items || []
    if (templates.value.length) await select(templates.value[0].id)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

async function select(id) {
  selectedId.value = id
  dialogMode.value = 'edit'
  saveError.value = ''
  mobileTab.value = 'content'
  try {
    detail.value = await api.getPromptTemplate(id)
    Object.assign(form, {
      id: detail.value.id,
      name: detail.value.name,
      description: detail.value.description,
      system: detail.value.system,
      user: detail.value.user,
    })
  } catch (e) {
    saveError.value = e.message
  }
}

function openCreate() {
  dialogMode.value = 'create'
  detail.value = { id: '', name: '', description: '', system: '', user: '', builtin: false }
  selectedId.value = ''
  mobileTab.value = 'settings'
  Object.assign(form, { id: '', name: '', description: '', system: '你是助手。', user: '' })
}

async function save() {
  saving.value = true
  saveError.value = ''
  try {
    if (dialogMode.value === 'create') {
      await api.createPromptTemplate({ ...form })
      const res = await api.getPromptTemplates()
      templates.value = res.items || []
      await select(form.id)
    } else {
      await api.updatePromptTemplate(form.id, {
        name: form.name,
        description: form.description,
        system: form.system,
        user: form.user,
      })
      await select(form.id)
    }
    dialogMode.value = 'edit'
  } catch (e) {
    saveError.value = e.message
  } finally {
    saving.value = false
  }
}

function remove() {
  if (!detail.value) return
  deleteConfirm.value = { message: `确定删除「${detail.value.name}」？` }
}

async function onDeleteConfirm() {
  if (!detail.value) {
    deleteConfirm.value = null
    return
  }
  deleteConfirm.value = null
  try {
    await api.deletePromptTemplate(detail.value.id)
    const res = await api.getPromptTemplates()
    templates.value = res.items || []
    if (templates.value.length) await select(templates.value[0].id)
    else detail.value = null
  } catch (e) {
    saveError.value = e.message
  }
}
</script>
