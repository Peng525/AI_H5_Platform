<template>
  <AiCreateLayout
    show-back
    back-label="返回首页"
    @back="router.push('/create/generate')"
  >
    <div class="mb-6 text-center sm:text-left">
      <h1 class="text-2xl sm:text-3xl font-bold">生成图片</h1>
      <p class="text-on-surface-variant text-sm mt-1">左侧编辑提示词，右侧查看生成结果，可裁切与复制</p>
    </div>

    <div class="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6 items-stretch">
      <!-- 左栏：提示词编辑 -->
      <section class="bg-white rounded-2xl border border-outline-variant shadow-card p-4 sm:p-5 flex flex-col h-full gap-4">
        <h2 class="text-base font-semibold text-on-surface shrink-0">提示词编辑</h2>
        <textarea
          v-model="prompt"
          class="flex-1 w-full rounded-2xl border border-outline-variant shadow-sm px-4 py-3 text-sm leading-relaxed resize-none min-h-[280px] sm:min-h-[360px] focus:outline-none focus:ring-2 focus:ring-primary/20"
          placeholder="描述画面内容，例如：科技感蓝色渐变背景的产品发布主视觉"
        />
        <label class="block text-sm shrink-0">
          <span class="font-medium text-on-surface-variant">尺寸</span>
          <select
            v-model="viewportMode"
            class="mt-1.5 w-full border border-outline-variant rounded-xl px-3 py-2.5 bg-white text-sm"
          >
            <option value="mobile">9:16 移动端</option>
            <option value="web">16:9 网页</option>
          </select>
        </label>
        <p v-if="error" class="text-sm text-red-600 shrink-0">{{ error }}</p>
        <button
          type="button"
          class="w-full py-2.5 rounded-xl bg-primary text-on-primary font-medium disabled:opacity-50 inline-flex items-center justify-center gap-2 shrink-0"
          :disabled="generating || !prompt.trim()"
          @click="submit"
        >
          <span v-if="generating" class="material-symbols-outlined animate-spin text-lg">progress_activity</span>
          {{ generating ? '生成中…' : '生成图片' }}
        </button>
      </section>

      <!-- 右栏：生成结果 -->
      <section class="bg-white rounded-2xl border border-outline-variant shadow-card p-4 sm:p-5 flex flex-col h-full gap-4">
        <h2 class="text-base font-semibold text-on-surface shrink-0">生成结果</h2>

        <p
          class="text-sm leading-relaxed shrink-0 min-h-[2.5rem]"
          :class="resultPrompt ? 'text-on-surface-variant line-clamp-2' : 'text-on-surface-variant/70'"
        >
          {{ resultPrompt || '生成后将在此显示所用提示词' }}
        </p>

        <div
          class="flex-1 relative rounded-2xl border border-outline-variant bg-surface-container-low min-h-[280px] sm:min-h-[360px] flex items-center justify-center overflow-hidden"
          :class="displayUrl && !generating ? 'border-solid' : 'border-dashed'"
        >
          <div v-if="generating" class="flex flex-col items-center gap-2 text-on-surface-variant">
            <span class="material-symbols-outlined animate-spin text-3xl text-primary">progress_activity</span>
            <span class="text-sm">生成中…</span>
          </div>
          <div v-else-if="!displayUrl" class="text-sm text-on-surface-variant/70 px-4 text-center">
            生成后将在此显示结果
          </div>
          <img
            v-else
            :src="displayUrl"
            alt="生成结果"
            title="点击裁切"
            class="w-full h-full max-h-full object-contain cursor-pointer hover:opacity-95 transition"
            @click="cropOpen = true"
          />
        </div>

        <button
          type="button"
          class="w-full py-2.5 rounded-xl border border-outline-variant text-sm font-medium hover:bg-surface-container-low/50 disabled:opacity-40 disabled:cursor-not-allowed transition shrink-0"
          :disabled="!displayUrl || generating"
          @click="copyImage"
        >
          复制
        </button>
      </section>
    </div>

    <ImageCropModal
      :open="cropOpen"
      :image-url="displayUrl"
      :initial-crop="lastCrop"
      @close="cropOpen = false"
      @confirm="onCropConfirm"
    />
  </AiCreateLayout>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../../api/client'
import AiCreateLayout from '../../components/create/AiCreateLayout.vue'
import ImageCropModal from '../../components/ImageCropModal.vue'
import { useToast } from '../../composables/useToast.js'
import { loadDraft } from '../../composables/useAiCreateDraft.js'
import { enrichImagePrompt } from '../../constants/imageGenerateOptions.js'
import { cropImageToBlobUrl, urlToBlob } from '../../utils/cropImage.js'

const router = useRouter()
const { success: toastSuccess, error: toastError } = useToast()

const prompt = ref('')
const viewportMode = ref('mobile')
const imageColor = ref('classic_white')
const imageStyle = ref('扁平插画')
const generating = ref(false)
const error = ref('')
const resultPrompt = ref('')
const displayUrl = ref('')
const blobUrls = ref([])
const cropOpen = ref(false)
const lastCrop = ref(null)

onMounted(() => {
  const draft = loadDraft()
  if (draft.topic) prompt.value = draft.topic
  if (draft.viewportMode && draft.viewportMode !== 'auto') {
    viewportMode.value = draft.viewportMode === 'web' ? 'web' : 'mobile'
  }
  if (draft.imageColor) imageColor.value = draft.imageColor
  if (draft.imageStyle) imageStyle.value = draft.imageStyle
})

onUnmounted(() => {
  blobUrls.value.forEach((u) => URL.revokeObjectURL(u))
})

function trackBlob(url) {
  if (url.startsWith('blob:')) blobUrls.value.push(url)
}

async function submit() {
  if (!prompt.value.trim()) return
  generating.value = true
  error.value = ''
  try {
    const preset = viewportMode.value === 'web' ? 'web-1280' : 'mobile-375'
    const finalPrompt = enrichImagePrompt(prompt.value.trim(), {
      imageStyle: imageStyle.value,
      imageColor: imageColor.value,
    })
    const result = await api.generateStandaloneImage({
      prompt: finalPrompt,
      tier: 'free',
      viewport_preset_id: preset,
      fit_mode: 'fill',
    })
    resultPrompt.value = finalPrompt
    displayUrl.value = result.image_url
    lastCrop.value = null
  } catch (e) {
    error.value = e.message || '生成失败'
  } finally {
    generating.value = false
  }
}

async function onCropConfirm(crop) {
  cropOpen.value = false
  lastCrop.value = crop
  try {
    const next = await cropImageToBlobUrl(displayUrl.value, crop)
    trackBlob(next)
    displayUrl.value = next
    toastSuccess('裁切已应用')
  } catch (e) {
    toastError(e.message || '裁切失败')
  }
}

async function copyImage() {
  if (!displayUrl.value) return
  try {
    const blob = await urlToBlob(displayUrl.value)
    if (navigator.clipboard?.write && window.ClipboardItem) {
      await navigator.clipboard.write([
        new ClipboardItem({ [blob.type || 'image/png']: blob }),
      ])
      toastSuccess('图片已复制到剪贴板')
      return
    }
    await navigator.clipboard.writeText(displayUrl.value)
    toastSuccess('已复制图片链接')
  } catch {
    try {
      await navigator.clipboard.writeText(displayUrl.value)
      toastSuccess('已复制图片链接')
    } catch {
      toastError('复制失败')
    }
  }
}
</script>
