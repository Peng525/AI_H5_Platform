<template>
  <aside class="w-[300px] border-l border-outline-variant bg-surface-container-low flex flex-col shrink-0">
    <div class="p-4 border-b border-outline-variant">
      <h2 class="font-semibold text-sm">AI 智能面板</h2>
      <p class="text-xs text-on-surface-variant">智能创作</p>
    </div>

    <nav class="flex border-b border-outline-variant text-sm">
      <button
        v-for="t in tabs"
        :key="t.id"
        class="flex-1 py-2.5 text-center"
        :class="tab === t.id ? 'text-primary border-b-2 border-primary font-medium' : 'text-on-surface-variant'"
        @click="tab = t.id"
      >
        {{ t.label }}
      </button>
    </nav>

    <div v-if="tab === 'assistant'" class="flex-1 flex flex-col p-4 overflow-y-auto min-h-0">
      <p class="text-xs font-medium text-on-surface-variant mb-2">生成通道</p>
      <button
        class="w-full text-left p-3 rounded-lg border-2 mb-2"
        :class="channelTier === 'free' ? 'border-secondary bg-white' : 'border-outline-variant'"
        @click="channelTier = 'free'"
      >
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium">基础通道（免费）</span>
          <span v-if="channelTier === 'free'" class="material-symbols-outlined text-secondary text-lg">check_circle</span>
        </div>
        <p class="text-xs text-on-surface-variant mt-1">Gemini 配图模型 · 读取 .env 配置</p>
      </button>
      <button
        class="w-full text-left p-3 rounded-lg border border-outline-variant opacity-70 mb-4"
        :class="channelTier === 'pro' ? 'border-primary' : ''"
        @click="onProClick"
      >
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium">官方原生通道（VIP）</span>
          <span class="material-symbols-outlined text-lg">lock</span>
        </div>
        <p class="text-xs text-on-surface-variant mt-1">Gemini 3 Pro · 需升级</p>
      </button>

      <label class="text-xs font-medium text-on-surface-variant">画面描述 / 指令</label>
      <textarea
        v-model="prompt"
        rows="4"
        class="mt-1 w-full border border-outline-variant rounded-lg p-3 text-sm resize-none"
        placeholder="描述您想要的 H5 画面，例如：站在路口的人，左右两条分岔路…"
      />

      <div class="flex flex-wrap gap-2 mt-2">
        <button
          v-for="s in styles"
          :key="s"
          class="px-2 py-1 text-xs rounded-full border"
          :class="selectedStyle === s ? 'bg-primary text-on-primary border-primary' : 'border-outline-variant'"
          @click="selectedStyle = s"
        >
          {{ s }}
        </button>
      </div>

      <p class="text-xs font-medium text-on-surface-variant mt-3 mb-1">添加到页面时的尺寸</p>
      <div class="flex flex-wrap gap-1.5">
        <button
          v-for="m in fitModes"
          :key="m.id"
          type="button"
          class="px-2 py-1 text-[11px] rounded-full border"
          :class="fitMode === m.id ? 'bg-secondary/15 border-secondary text-secondary' : 'border-outline-variant'"
          @click="fitMode = m.id"
        >
          {{ m.label }}
        </button>
      </div>

      <label class="flex items-center gap-2 mt-2 text-xs text-on-surface-variant cursor-pointer">
        <input v-model="autoAddToPage" type="checkbox" class="rounded border-outline-variant text-primary focus:ring-primary" />
        生成后自动添加到当前页
      </label>

      <div v-if="generatedImage" class="mt-3 rounded-lg border border-outline-variant overflow-hidden bg-white">
        <img :src="generatedImage.url" alt="AI 生成配图" class="w-full max-h-40 object-contain bg-surface-container-low" />
        <div class="p-2 space-y-1.5 border-t border-outline-variant">
          <p class="text-[10px] text-on-surface-variant truncate" :title="generatedImage.model">
            {{ generatedImage.channel }} · {{ generatedImage.model }}
          </p>
          <div class="flex gap-1.5">
            <button
              type="button"
              class="flex-1 py-1.5 text-xs rounded-md bg-primary text-on-primary"
              @click="emitAddToPage"
            >
              添加到页面
            </button>
            <button
              type="button"
              class="px-2 py-1.5 text-xs rounded-md border border-outline-variant hover:bg-surface-container-low"
              title="复制图片到剪贴板"
              @click="copyImage"
            >
              复制
            </button>
          </div>
        </div>
      </div>

      <p v-if="imageError" class="text-xs text-red-600 mt-2">{{ imageError }}</p>

      <div class="mt-auto pt-4 space-y-2">
        <button
          class="w-full py-3 rounded-lg bg-primary text-on-primary font-medium flex items-center justify-center gap-2 disabled:opacity-50"
          :disabled="imageLoading"
          @click="onGenerateImage"
        >
          <span class="material-symbols-outlined text-lg">image</span>
          {{ imageLoading ? '配图生成中…' : '生成配图' }}
        </button>
        <button
          type="button"
          class="w-full py-2 rounded-lg border border-outline-variant text-sm text-on-surface-variant hover:bg-white disabled:opacity-50"
          :disabled="textLoading"
          @click="onGenerateText"
        >
          {{ textLoading ? '文案生成中…' : '仅生成文案（标题与要点）' }}
        </button>
        <p class="text-xs text-center text-on-surface-variant">
          剩余免费次数 {{ quotaRemaining }}/{{ quotaTotal }}
        </p>
        <router-link to="/upgrade" class="block text-center text-xs text-primary">升级解锁 Pro 模型 →</router-link>
      </div>
    </div>

    <div v-else-if="tab === 'prompts'" class="p-4 text-sm text-on-surface-variant">
      <p class="font-medium text-on-surface mb-2">内置模板</p>
      <ul class="space-y-2">
        <li class="p-2 bg-white rounded-lg border">全量生成 — 整套 H5 结构</li>
        <li class="p-2 bg-white rounded-lg border">单页改写 — 自然语言改一页</li>
        <li class="p-2 bg-white rounded-lg border">AI 配图 — 根据描述生成插画</li>
      </ul>
    </div>

    <div v-else class="p-4 text-sm">
      <p>已用 {{ quotaTotal - quotaRemaining }} / {{ quotaTotal }} 次</p>
      <div class="mt-2 h-2 bg-outline-variant/30 rounded-full overflow-hidden">
        <div
          class="h-full bg-secondary transition-all"
          :style="{ width: `${(quotaRemaining / quotaTotal) * 100}%` }"
        />
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const props = defineProps({
  textLoading: Boolean,
  imageLoading: Boolean,
  quotaRemaining: { type: Number, default: 5 },
  quotaTotal: { type: Number, default: 5 },
  llmChannel: { type: String, default: '' },
})
const emit = defineEmits(['generate-text', 'generate-image', 'add-image-to-page'])

const router = useRouter()
const { user } = useAuth()
const tab = ref('assistant')
const channelTier = ref('free')
const prompt = ref('')
const selectedStyle = ref('商务专业')
const fitMode = ref('width')
const autoAddToPage = ref(true)
const generatedImage = ref(null)
const imageError = ref('')

const tabs = [
  { id: 'assistant', label: 'AI 助手' },
  { id: 'prompts', label: '提示词' },
  { id: 'quota', label: '配额' },
]
const styles = ['3D质感', '扁平插画', '商务专业']
const fitModes = [
  { id: 'width', label: '适应宽度' },
  { id: 'fill', label: '填充页面' },
  { id: 'original', label: '原始尺寸' },
]

function onProClick() {
  if (user.value?.tier === 'pro') {
    channelTier.value = 'pro'
  } else {
    router.push('/upgrade')
  }
}

function payloadBase() {
  return {
    prompt: prompt.value,
    channelTier: channelTier.value,
    channel: props.llmChannel,
    style: selectedStyle.value,
  }
}

function onGenerateText() {
  if (!prompt.value?.trim()) return
  emit('generate-text', payloadBase())
}

function onGenerateImage() {
  if (!prompt.value?.trim()) return
  imageError.value = ''
  emit('generate-image', payloadBase())
}

function setGeneratedImage(result) {
  generatedImage.value = {
    url: result.image_url,
    channel: result.channel,
    model: result.model,
    width: result.width,
    height: result.height,
  }
  if (autoAddToPage.value) {
    emitAddToPage()
  }
}

function setImageError(msg) {
  imageError.value = msg
  generatedImage.value = null
}

function emitAddToPage() {
  if (!generatedImage.value) return
  emit('add-image-to-page', {
    ...generatedImage.value,
    fitMode: fitMode.value,
  })
}

async function copyImage() {
  if (!generatedImage.value?.url) return
  try {
    const res = await fetch(generatedImage.value.url)
    const blob = await res.blob()
    await navigator.clipboard.write([new ClipboardItem({ [blob.type]: blob })])
  } catch {
    try {
      await navigator.clipboard.writeText(generatedImage.value.url)
    } catch (e) {
      imageError.value = '复制失败，请使用「添加到页面」'
    }
  }
}

defineExpose({ setGeneratedImage, setImageError })
</script>
