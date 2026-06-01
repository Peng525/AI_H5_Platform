<template>
  <AiCreateLayout show-back back-label="上一步" :quota-text="quotaText" @back="router.push('/create/generate')">
    <div class="mb-6 text-center sm:text-left">
      <h1 class="text-2xl sm:text-3xl font-bold">生成图片</h1>
      <p class="text-on-surface-variant text-sm mt-1">描述您想生成的画面，将创建单页项目并插入配图</p>
    </div>

    <div class="max-w-xl mx-auto bg-white rounded-2xl border border-outline-variant/60 shadow-sm p-4 sm:p-5 space-y-4">
      <textarea
        v-model="prompt"
        rows="5"
        class="w-full border border-outline-variant rounded-xl px-3 py-2.5 text-sm resize-none"
        placeholder="描述画面内容，例如：科技感蓝色渐变背景的产品发布主视觉"
      />
      <label class="block text-sm">
        <span class="font-medium text-on-surface-variant">尺寸</span>
        <select v-model="viewportMode" class="mt-1 w-full border border-outline-variant rounded-lg px-3 py-2 bg-white">
          <option value="mobile">移动端</option>
          <option value="web">传统网页</option>
        </select>
      </label>
      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
      <button
        type="button"
        class="w-full py-2.5 rounded-xl bg-primary text-on-primary font-medium disabled:opacity-50"
        :disabled="generating || !prompt.trim()"
        @click="submit"
      >
        {{ generating ? '生成中…' : '生成并进入编辑器' }}
      </button>
    </div>
  </AiCreateLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../../api/client'
import AiCreateLayout from '../../components/create/AiCreateLayout.vue'
import { applyProjectSettingsLocal, loadDraft } from '../../composables/useAiCreateDraft.js'

const router = useRouter()
const prompt = ref('')
const viewportMode = ref('mobile')
const generating = ref(false)
const error = ref('')
const quotaText = ref('')

onMounted(async () => {
  const draft = loadDraft()
  if (draft.viewportMode && draft.viewportMode !== 'auto') {
    viewportMode.value = draft.viewportMode === 'web' ? 'web' : 'mobile'
  }
  try {
    const q = await api.getQuota()
    quotaText.value = `${q.quota_remaining}/${q.quota_total}`
  } catch {
    quotaText.value = '—'
  }
})

async function submit() {
  if (!prompt.value.trim()) return
  generating.value = true
  error.value = ''
  try {
    const project = await api.createProject({ title: prompt.value.trim().slice(0, 40), theme: 'default' })
    const viewportId = viewportMode.value === 'web' ? 'web-1280' : 'mobile-375'
    applyProjectSettingsLocal(project.id, { viewportId, scrollEffect: 'vertical', themeId: 'zjy-minimal' })

    const slide = project.slides?.[0]
    if (!slide) throw new Error('项目创建失败')

    const preset = viewportMode.value === 'web' ? 'web-1280' : 'mobile-375'
    const result = await api.generateImage(project.id, {
      prompt: prompt.value.trim(),
      tier: 'free',
      viewport_preset_id: preset,
      fit_mode: 'fill',
    })

    const w = viewportMode.value === 'web' ? 960 : 335
    const h = viewportMode.value === 'web' ? 540 : 500
    const elements = [
      {
        id: `img_${Date.now()}`,
        type: 'image',
        x: viewportMode.value === 'web' ? 40 : 20,
        y: viewportMode.value === 'web' ? 40 : 80,
        width: w,
        height: h,
        zIndex: 1,
        content: result.image_url,
        style: { objectFit: 'cover', borderRadius: 8 },
      },
    ]
    await api.saveSlideCanvas(project.id, slide.id, elements)
    localStorage.setItem(`ai_h5_canvas_${project.id}_${slide.id}`, JSON.stringify(elements))
    router.push(`/editor/${project.id}`)
  } catch (e) {
    error.value = e.message || '生成失败'
    generating.value = false
  }
}
</script>
