<template>
  <section class="rounded-xl border border-outline-variant/70 bg-surface-container-low/50 p-4 sm:p-5 space-y-3">
    <div class="flex items-start gap-3">
      <span class="material-symbols-outlined text-[22px] text-primary shrink-0 mt-0.5">auto_awesome</span>
      <div class="min-w-0 flex-1">
        <h2 class="text-sm font-semibold text-on-surface">演示生成方式</h2>
        <p class="text-xs text-on-surface-variant mt-1 leading-relaxed">
          <strong class="font-medium text-on-surface">快速生成</strong>：秒级出稿，适合移动端预览与草稿；版式为固定模板，复杂页可能裁切。
          <strong class="font-medium text-on-surface ml-1">高质量</strong>：先用 ppt-master 导出 PPTX，再导入本平台编辑发布（推荐汇报交付）。
        </p>
      </div>
    </div>
    <div class="flex flex-wrap gap-2">
      <a
        href="https://github.com/hugohe3/ppt-master#quick-start"
        target="_blank"
        rel="noopener noreferrer"
        class="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg border border-outline-variant bg-white text-xs font-medium hover:bg-surface-container-low transition-colors"
      >
        <span class="material-symbols-outlined text-[16px]">open_in_new</span>
        ppt-master Quick Start
      </a>
      <button
        type="button"
        class="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg border border-primary/30 bg-primary/5 text-primary text-xs font-medium hover:bg-primary/10 transition-colors disabled:opacity-50"
        :disabled="importing"
        @click="triggerImport"
      >
        <span class="material-symbols-outlined text-[16px]">upload</span>
        {{ importing ? '导入中…' : '导入 ppt-master 成品' }}
      </button>
    </div>
    <p v-if="importError" class="text-xs text-red-600">{{ importError }}</p>
    <p v-if="importOk" class="text-xs text-emerald-700">已导入，正在打开编辑器…</p>
    <input
      ref="fileInputRef"
      type="file"
      accept=".pptx,application/vnd.openxmlformats-officedocument.presentationml.presentation"
      class="hidden"
      @change="onFileSelected"
    />
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../../api/client.js'

const router = useRouter()
const fileInputRef = ref(null)
const importing = ref(false)
const importError = ref('')
const importOk = ref(false)

function triggerImport() {
  importError.value = ''
  importOk.value = false
  fileInputRef.value?.click()
}

async function onFileSelected(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  if (!file.name.toLowerCase().endsWith('.pptx')) {
    importError.value = '请选择 .pptx 文件'
    return
  }
  importing.value = true
  importError.value = ''
  try {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('device', 'web')
    fd.append('title', file.name.replace(/\.pptx$/i, ''))
    const project = await api.importPremiumProjectPptx(fd)
    importOk.value = true
    router.push(`/editor/${project.public_id}`)
  } catch (err) {
    importError.value = err.message || '导入失败'
  } finally {
    importing.value = false
  }
}
</script>
