<template>
  <AdminShell title="提示词模板">
    <div class="flex justify-between items-center mb-6">
      <p class="text-sm text-on-surface-variant">配图相关提示词（可选，当前编辑器以画面描述为主）</p>
      <button
        type="button"
        class="px-4 py-2 rounded-lg bg-primary text-on-primary text-sm font-medium"
        @click="openCreate"
      >
        新建模板
      </button>
    </div>

    <p v-if="loading" class="text-on-surface-variant">加载中…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>

    <div v-else class="grid lg:grid-cols-3 gap-6">
      <div class="lg:col-span-1 bg-white rounded-xl border border-outline-variant p-4">
        <ul class="space-y-1">
          <li
            v-for="t in templates"
            :key="t.id"
            class="px-3 py-2 rounded-lg cursor-pointer text-sm flex justify-between gap-2"
            :class="selectedId === t.id ? 'bg-primary/10 text-primary font-medium' : 'hover:bg-surface-container-low'"
            @click="select(t.id)"
          >
            <span>{{ t.name }}</span>
            <span v-if="t.builtin" class="text-[10px] text-on-surface-variant shrink-0">内置</span>
          </li>
        </ul>
      </div>

      <div v-if="detail" class="lg:col-span-2 bg-white rounded-xl border border-outline-variant p-6 space-y-4">
        <div class="grid grid-cols-2 gap-3 text-sm">
          <label class="block">
            <span class="font-medium">ID</span>
            <input v-model="form.id" :disabled="!!detail.builtin && dialogMode === 'edit'" class="mt-1 w-full border rounded-lg px-3 py-2 disabled:bg-surface-container-low" />
          </label>
          <label class="block">
            <span class="font-medium">名称</span>
            <input v-model="form.name" class="mt-1 w-full border rounded-lg px-3 py-2" />
          </label>
        </div>
        <label class="block text-sm">
          <span class="font-medium">描述</span>
          <input v-model="form.description" class="mt-1 w-full border rounded-lg px-3 py-2" />
        </label>
        <label class="block text-sm">
          <span class="font-medium">System 提示词</span>
          <textarea v-model="form.system" rows="10" class="mt-1 w-full border rounded-lg px-3 py-2 font-mono text-xs" />
        </label>
        <label class="block text-sm">
          <span class="font-medium">User 提示词</span>
          <textarea v-model="form.user" rows="4" class="mt-1 w-full border rounded-lg px-3 py-2 font-mono text-xs" />
        </label>
        <p class="text-xs text-on-surface-variant">支持 Jinja2 变量，如 &#123;&#123; topic &#125;&#125;、&#123;&#123; page_count &#125;&#125;</p>
        <p v-if="saveError" class="text-red-600 text-sm">{{ saveError }}</p>
        <div class="flex gap-2">
          <button type="button" class="px-4 py-2 bg-primary text-on-primary rounded-lg text-sm" :disabled="saving" @click="save">
            {{ saving ? '保存中…' : '保存' }}
          </button>
          <button
            v-if="detail && !detail.builtin"
            type="button"
            class="px-4 py-2 border border-red-200 text-red-600 rounded-lg text-sm"
            @click="remove"
          >
            删除
          </button>
        </div>
      </div>
    </div>
  </AdminShell>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../../api/client'
import AdminShell from '../../components/AdminShell.vue'

const templates = ref([])
const selectedId = ref('')
const detail = ref(null)
const loading = ref(true)
const error = ref('')
const saving = ref(false)
const saveError = ref('')
const dialogMode = ref('edit')
const form = reactive({ id: '', name: '', description: '', system: '', user: '' })

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

async function remove() {
  if (!detail.value || !confirm(`确定删除「${detail.value.name}」？`)) return
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
