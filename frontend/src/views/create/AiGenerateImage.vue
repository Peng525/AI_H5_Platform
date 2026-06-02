<template>
  <AiCreateLayout show-back back-label="上一步" @back="router.push('/create/generate')">
    <div class="mb-6 text-center sm:text-left">
      <h1 class="text-2xl sm:text-3xl font-bold">生成图片</h1>
      <p class="text-on-surface-variant text-sm mt-1">
        {{ phase === 'form' ? '输入提示词生成图片，可裁切、复制与下载' : '图片已生成，可进行裁切或复制' }}
      </p>
    </div>

    <div v-if="phase === 'form'" class="max-w-xl mx-auto bg-white rounded-2xl border border-outline-variant/60 shadow-sm p-4 sm:p-5 space-y-4">
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
        {{ generating ? '生成中…' : '生成图片' }}
      </button>
    </div>

    <div v-else class="max-w-2xl mx-auto space-y-4">
      <div class="bg-white rounded-2xl border border-outline-variant/60 shadow-sm p-4 overflow-hidden">
        <img
          :src="displayUrl"
          alt="生成结果"
          class="w-full max-h-[min(70vh,520px)] object-contain mx-auto rounded-lg bg-surface-container-low"
        />
      </div>
      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
      <div class="flex flex-wrap gap-2 justify-center sm:justify-end">
        <button
          type="button"
          class="px-4 py-2 rounded-lg border border-outline-variant text-sm font-medium hover:bg-white bg-white/90"
          @click="cropOpen = true"
        >
          裁切
        </button>
        <button
          type="button"
          class="px-4 py-2 rounded-lg border border-outline-variant text-sm font-medium hover:bg-white bg-white/90"
          @click="copyImage"
        >
          复制图片
        </button>
        <button
          type="button"
          class="px-4 py-2 rounded-lg border border-outline-variant text-sm font-medium hover:bg-white bg-white/90"
          @click="downloadImage"
        >
          下载
        </button>
        <button
          type="button"
          class="px-4 py-2 rounded-lg bg-primary text-on-primary text-sm font-medium"
          @click="resetToForm"
        >
          重新生成
        </button>
      </div>
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
import { cropImageToBlobUrl, urlToBlob } from '../../utils/cropImage.js'

const router = useRouter()
const { success: toastSuccess, error: toastError } = useToast()

const prompt = ref('')
const viewportMode = ref('mobile')
const phase = ref('form')
const generating = ref(false)
const error = ref('')
const originalUrl = ref('')
const displayUrl = ref('')
const blobUrls = ref([])
const cropOpen = ref(false)
const lastCrop = ref(null)

onMounted(() => {
  const draft = loadDraft()
  if (draft.viewportMode && draft.viewportMode !== 'auto') {
    viewportMode.value = draft.viewportMode === 'web' ? 'web' : 'mobile'
  }
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
    const result = await api.generateStandaloneImage({
      prompt: prompt.value.trim(),
      tier: 'free',
      viewport_preset_id: preset,
      fit_mode: 'fill',
    })
    originalUrl.value = result.image_url
    displayUrl.value = result.image_url
    lastCrop.value = null
    phase.value = 'result'
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
      toastError('复制失败，请尝试下载')
    }
  }
}

function downloadImage() {
  const a = document.createElement('a')
  a.href = displayUrl.value
  a.download = `ai-image-${Date.now()}.png`
  a.rel = 'noopener'
  document.body.appendChild(a)
  a.click()
  a.remove()
}

function resetToForm() {
  phase.value = 'form'
  error.value = ''
  originalUrl.value = ''
  displayUrl.value = ''
  lastCrop.value = null
}
</script>
