<template>
  <aside class="editor-ai-panel w-[14rem] sm:w-[16.25rem] lg:w-[18.75rem] border-l border-outline-variant bg-surface-container-low flex flex-col h-full min-h-0 shrink-0 overflow-hidden">
    <div class="p-4 border-b border-outline-variant shrink-0">
      <h2 class="font-semibold text-sm">AI 智能面板</h2>
    </div>

    <nav class="flex border-b border-outline-variant text-xs sm:text-sm shrink-0 overflow-x-auto">
      <button
        v-for="t in tabs"
        :key="t.id"
        type="button"
        class="flex-1 min-w-[4.5rem] py-2 sm:py-2.5 text-center whitespace-nowrap px-1"
        :class="tab === t.id ? 'text-primary border-b-2 border-primary font-medium' : 'text-on-surface-variant'"
        @click="tab = t.id"
      >
        {{ t.label }}
      </button>
    </nav>

    <div
      ref="scrollRef"
      class="flex-1 min-h-0 overflow-y-auto overflow-x-hidden overscroll-y-contain ai-panel-scroll"
    >
      <div v-if="tab === 'assistant'" class="p-4 pb-6 space-y-3">
        <p class="text-xs font-medium text-on-surface-variant">生成通道</p>
        <button
          class="w-full text-left p-3 rounded-lg border-2"
          :class="channelTier === 'free' ? 'border-secondary bg-white' : 'border-outline-variant'"
          @click="channelTier = 'free'"
        >
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium">基础通道（免费）</span>
            <span v-if="channelTier === 'free'" class="material-symbols-outlined text-secondary text-lg">check_circle</span>
          </div>
          <p class="text-xs text-on-surface-variant mt-1">标准画质，免费使用</p>
        </button>
        <button
          class="w-full text-left p-3 rounded-lg border border-outline-variant opacity-70"
          :class="channelTier === 'pro' ? 'border-primary' : ''"
          @click="onProClick"
        >
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium">官方原生通道（VIP）</span>
            <span class="material-symbols-outlined text-lg">lock</span>
          </div>
          <p class="text-xs text-on-surface-variant mt-1">高清画质，会员专享</p>
        </button>

        <div>
          <label class="text-xs font-medium text-on-surface-variant">画面描述 / 指令</label>
          <textarea
            v-model="prompt"
            rows="4"
            class="mt-1 w-full border border-outline-variant rounded-lg p-3 text-sm resize-y min-h-[88px] max-h-48"
            placeholder="描述您想要的 H5 画面，例如：站在路口的人，左右两条分岔路…"
          />
        </div>

        <div class="flex flex-wrap gap-2">
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

        <div>
          <label class="text-xs font-medium text-on-surface-variant">生图分辨率</label>
          <select
            v-model="genViewportId"
            class="mt-1 w-full border border-outline-variant rounded-lg px-2 py-2 text-sm bg-white"
          >
            <optgroup v-for="g in imageGenGroups" :key="g.label" :label="g.label">
              <option v-for="opt in g.options" :key="opt.id" :value="opt.id">
                {{ opt.label }} · {{ opt.contentWidth }}×{{ opt.contentHeight }}
              </option>
            </optgroup>
          </select>
          <p class="text-[10px] text-on-surface-variant mt-1">
            生图：{{ genResolutionHint }}（内容区）
          </p>
        </div>

        <div class="space-y-2 pt-1">
          <button
            class="w-full py-3 rounded-lg bg-primary text-on-primary font-medium flex items-center justify-center gap-2 disabled:opacity-50"
            :disabled="imageLoading"
            @click="onGenerateImage"
          >
            <span class="material-symbols-outlined text-lg">image</span>
            {{ imageLoading ? '生图生成中…' : 'AI 生图' }}
          </button>
          <p class="text-xs text-center text-on-surface-variant">
            剩余免费次数 {{ quotaRemaining }}/{{ quotaTotal }}
          </p>
          <router-link to="/upgrade" class="block text-center text-xs text-primary pb-1">升级会员 →</router-link>
        </div>

        <div
          v-if="generatedImage"
          ref="previewRef"
          class="rounded-lg border border-outline-variant overflow-hidden bg-white"
        >
          <div class="px-2 py-1.5 bg-surface-container-low border-b border-outline-variant flex items-center justify-between gap-2">
            <span class="text-xs text-on-surface-variant">原图预览</span>
            <span v-if="generatedImage.width && generatedImage.height" class="text-[10px] text-on-surface-variant/80">
              {{ generatedImage.width }}×{{ generatedImage.height }}
            </span>
          </div>
          <div class="p-2 bg-surface-container-low">
            <img
              :src="generatedImage.url"
              alt="AI 生图原图"
              class="w-full h-auto max-w-full object-contain rounded-sm mx-auto block"
              draggable="false"
            />
          </div>
          <div class="p-2 space-y-2 border-t border-outline-variant">
            <div>
              <p class="text-[11px] font-medium text-on-surface-variant mb-1">添加到页面的方式</p>
              <p class="text-[10px] text-on-surface-variant mb-1.5 leading-snug">
                填充：按当前画布内容区完整显示；原始：等比紧包裹；适应宽：宽度贴齐
              </p>
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
            </div>
            <div class="flex gap-1.5">
              <button
                type="button"
                class="flex-1 py-1.5 text-xs rounded-md bg-primary text-on-primary"
                @click="emitAddToPage"
              >
                按「{{ fitModeLabel }}」添加
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

        <p v-if="imageError" class="text-xs text-red-600">{{ imageError }}</p>
      </div>

      <div v-else-if="tab === 'prompts'" class="p-4 pb-6 space-y-3">
        <p class="text-xs text-on-surface-variant">
          选择模板后将自动填入「AI 助手」中的画面描述，可按需修改后生成。
        </p>
        <ul class="space-y-2">
          <li
            v-for="tpl in promptTemplates"
            :key="tpl.id"
            class="rounded-lg border bg-white overflow-hidden transition-colors"
            :class="selectedTemplateId === tpl.id ? 'border-primary ring-1 ring-primary/20' : 'border-outline-variant hover:border-primary/40'"
          >
            <button
              type="button"
              class="w-full text-left p-3"
              @click="applyPromptTemplate(tpl)"
            >
              <div class="flex items-start justify-between gap-2">
                <div class="min-w-0">
                  <p class="text-sm font-medium text-on-surface">{{ tpl.title }}</p>
                  <p v-if="tpl.description" class="text-xs text-on-surface-variant mt-0.5">{{ tpl.description }}</p>
                </div>
                <span
                  v-if="selectedTemplateId === tpl.id"
                  class="material-symbols-outlined text-primary text-lg shrink-0"
                >check_circle</span>
              </div>
              <table class="mt-2 w-full text-[11px] text-on-surface-variant border-collapse">
                <tbody>
                  <tr v-for="field in tpl.fields" :key="field.label" class="align-top">
                    <td class="pr-2 py-0.5 whitespace-nowrap text-on-surface/70 w-10">{{ field.label }}</td>
                    <td class="py-0.5 leading-snug">{{ field.value }}</td>
                  </tr>
                </tbody>
              </table>
            </button>
          </li>
        </ul>
      </div>

      <div v-else class="p-4 pb-6 text-sm">
        <p>已用 {{ quotaTotal - quotaRemaining }} / {{ quotaTotal }} 次</p>
        <div class="mt-2 h-2 bg-outline-variant/30 rounded-full overflow-hidden">
          <div
            class="h-full bg-secondary transition-all"
            :style="{ width: `${(quotaRemaining / quotaTotal) * 100}%` }"
          />
        </div>
      </div>
    </div>

    <ConfirmDialog
      :open="upgradeDialogOpen"
      title="升级会员"
      message="官方原生通道为会员专享，提供更高清的画质。是否前往升级页面开通会员？"
      confirm-text="去升级"
      cancel-text="取消"
      @confirm="onUpgradeConfirm"
      @cancel="upgradeDialogOpen = false"
    />
  </aside>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { IMAGE_PROMPT_TEMPLATES, formatImagePromptTemplate } from '../constants/imagePromptTemplates'
import {
  IMAGE_GEN_PRESET_GROUPS,
  IMAGE_GEN_PRESET_IDS,
  getCanvasContentSize,
  getViewportPreset,
} from '../constants/editorPresets'
import ConfirmDialog from './ConfirmDialog.vue'

const props = defineProps({
  imageLoading: Boolean,
  quotaRemaining: { type: Number, default: 5 },
  quotaTotal: { type: Number, default: 5 },
  llmChannel: { type: String, default: '' },
  canvasViewportId: { type: String, default: 'mobile-375' },
})
const emit = defineEmits(['generate-image', 'add-image-to-page'])

const router = useRouter()
const { user } = useAuth()
const tab = ref('assistant')
const channelTier = ref('free')
const prompt = ref('')
const selectedStyle = ref('商务专业')
const fitMode = ref('width')
const generatedImage = ref(null)
const imageError = ref('')
const scrollRef = ref(null)
const previewRef = ref(null)
const upgradeDialogOpen = ref(false)
const selectedTemplateId = ref('')
const promptTemplates = IMAGE_PROMPT_TEMPLATES

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

const genViewportId = ref(
  IMAGE_GEN_PRESET_IDS.includes(props.canvasViewportId) ? props.canvasViewportId : 'mobile-375'
)

watch(
  () => props.canvasViewportId,
  (id) => {
    if (IMAGE_GEN_PRESET_IDS.includes(id)) {
      genViewportId.value = id
    }
  }
)

const imageGenGroups = computed(() =>
  IMAGE_GEN_PRESET_GROUPS.map((g) => ({
    label: g.label,
    options: g.ids.map((id) => {
      const preset = getViewportPreset(id)
      const content = getCanvasContentSize(preset)
      return {
        id,
        label: preset.label.replace(/^手机 · /, ''),
        contentWidth: content.width,
        contentHeight: content.height,
      }
    }),
  }))
)

const genViewportPreset = computed(() => getViewportPreset(genViewportId.value))
const genContentSize = computed(() => getCanvasContentSize(genViewportPreset.value))
const genResolutionHint = computed(() => {
  const p = genViewportPreset.value
  const c = genContentSize.value
  const short = p.label.replace(/^手机 · /, '').replace(/^网页 · /, '')
  return `${c.width}×${c.height}（${short}）`
})

const fitModeLabel = computed(() => fitModes.find((m) => m.id === fitMode.value)?.label || '适应宽度')

function onProClick() {
  if (user.value?.tier === 'pro') {
    channelTier.value = 'pro'
    return
  }
  upgradeDialogOpen.value = true
}

function onUpgradeConfirm() {
  upgradeDialogOpen.value = false
  router.push('/upgrade')
}

function applyPromptTemplate(tpl) {
  selectedTemplateId.value = tpl.id
  prompt.value = formatImagePromptTemplate(tpl)
  if (tpl.suggestedStyle && styles.includes(tpl.suggestedStyle)) {
    selectedStyle.value = tpl.suggestedStyle
  }
  tab.value = 'assistant'
  nextTick(() => {
    scrollRef.value?.scrollTo({ top: 0, behavior: 'smooth' })
  })
}

function payloadBase() {
  const content = genContentSize.value
  return {
    prompt: prompt.value,
    channelTier: channelTier.value,
    channel: props.llmChannel,
    style: selectedStyle.value,
    viewportPresetId: genViewportId.value,
    viewportWidth: content.width,
    viewportHeight: content.height,
    fitMode: fitMode.value,
  }
}

function onGenerateImage() {
  if (!prompt.value?.trim()) return
  imageError.value = ''
  emit('generate-image', payloadBase())
}

function scrollPreviewIntoView() {
  previewRef.value?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
}

function setGeneratedImage(result) {
  generatedImage.value = {
    url: result.image_url,
    channel: result.channel,
    model: result.model,
    width: result.width,
    height: result.height,
  }
  nextTick(() => {
    scrollPreviewIntoView()
  })
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
    } catch {
      imageError.value = '复制失败，请使用「添加到页面」'
    }
  }
}

defineExpose({ setGeneratedImage, setImageError })
</script>

<style scoped>
.ai-panel-scroll {
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 93, 170, 0.35) transparent;
}
.ai-panel-scroll::-webkit-scrollbar {
  width: 6px;
}
.ai-panel-scroll::-webkit-scrollbar-thumb {
  background: rgba(0, 93, 170, 0.35);
  border-radius: 999px;
}
.ai-panel-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 93, 170, 0.55);
}
</style>
