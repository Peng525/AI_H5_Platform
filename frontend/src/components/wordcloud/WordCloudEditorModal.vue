<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="open" class="fixed inset-0 z-[200] bg-surface-container-low flex flex-col">
        <header class="shrink-0 flex items-center justify-between px-4 py-3 border-b border-outline-variant bg-white">
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-secondary">cloud</span>
            <h1 class="text-lg font-bold">文字云</h1>
          </div>
          <div class="flex items-center gap-2">
            <button
              type="button"
              class="px-3 py-1.5 text-sm border border-outline-variant rounded-lg"
              @click="refreshPreview"
            >
              刷新预览
            </button>
            <button
              type="button"
              class="px-3 py-1.5 text-sm border border-outline-variant rounded-lg"
              :disabled="exporting"
              @click="downloadImage"
            >
              下载
            </button>
            <button
              type="button"
              class="px-3 py-1.5 text-sm border border-outline-variant rounded-lg"
              @click="$emit('insert-vector', { ...content })"
            >
              插入（可编辑）
            </button>
            <button
              type="button"
              class="px-3 py-1.5 text-sm bg-primary text-on-primary rounded-lg font-medium"
              @click="insertAsImage"
            >
              插入图片
            </button>
            <button type="button" class="p-2 rounded-lg hover:bg-surface-container" @click="$emit('close')">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
        </header>

        <div class="flex-1 flex min-h-0">
          <aside class="w-32 shrink-0 border-r border-outline-variant bg-white overflow-y-auto p-2 space-y-2">
            <p class="text-[10px] font-semibold text-on-surface-variant px-1">形状</p>
            <button
              v-for="shape in WORD_CLOUD_SHAPES"
              :key="shape.id"
              type="button"
              class="w-full rounded-lg border p-2 text-center transition hover:border-primary"
              :class="content.shapeId === shape.id ? 'border-primary ring-1 ring-primary bg-primary/5' : 'border-outline-variant'"
              @click="content.shapeId = shape.id; refreshPreview()"
            >
              <span class="material-symbols-outlined text-2xl text-secondary">{{ shape.icon }}</span>
              <span class="block text-[10px] mt-1">{{ shape.label }}</span>
            </button>
          </aside>

          <main class="flex-1 min-w-0 flex items-center justify-center p-6 bg-[#e8eaed]">
            <div class="bg-white shadow-xl rounded-lg p-2 border border-outline-variant/50">
              <canvas ref="canvasRef" :width="previewW" :height="previewH" class="block max-w-full" />
            </div>
          </main>

          <aside class="w-64 shrink-0 border-l border-outline-variant bg-white overflow-y-auto p-3 space-y-4 text-xs">
            <section>
              <h3 class="font-semibold text-on-surface-variant mb-2">关键词</h3>
              <div class="flex flex-wrap gap-1 mb-2">
                <span
                  v-for="(w, i) in content.words"
                  :key="i"
                  class="inline-flex items-center gap-0.5 px-2 py-0.5 bg-surface-container-low rounded-full text-[10px]"
                >
                  {{ w.text }}
                  <button type="button" class="text-red-500" @click="removeWord(i)">×</button>
                </span>
              </div>
              <div class="flex gap-1">
                <input
                  v-model="newWord"
                  class="flex-1 border rounded px-2 py-1 text-xs"
                  placeholder="新关键词"
                  @keydown.enter="addWord"
                />
                <button type="button" class="px-2 py-1 bg-primary text-on-primary rounded text-xs" @click="addWord">
                  添加
                </button>
              </div>
            </section>

            <section>
              <h3 class="font-semibold text-on-surface-variant mb-1">粘贴表格</h3>
              <textarea
                v-model="pasteText"
                rows="4"
                class="w-full border rounded px-2 py-1 text-[10px] font-mono"
                placeholder="选项,票数&#10;年轻人,120"
              />
              <button type="button" class="mt-1 w-full py-1 border border-outline-variant rounded text-[10px]" @click="importPaste">
                从表格导入
              </button>
            </section>

            <section>
              <h3 class="font-semibold text-on-surface-variant mb-1">上传文件</h3>
              <input type="file" accept=".csv,.txt,.xlsx,.xls" class="text-[10px] w-full" @change="onFile" />
            </section>

            <section class="space-y-2">
              <label class="block">
                <span class="text-[10px] text-on-surface-variant">最大字号</span>
                <input v-model.number="content.maxFontSize" type="number" min="20" max="300" class="w-full border rounded px-2 py-1 mt-0.5" />
              </label>
              <label class="block">
                <span class="text-[10px] text-on-surface-variant">紧密度</span>
                <select v-model="content.density" class="w-full border rounded px-2 py-1 mt-0.5">
                  <option value="tight">紧密</option>
                  <option value="normal">正常</option>
                  <option value="loose">疏松</option>
                </select>
              </label>
              <label class="block">
                <span class="text-[10px] text-on-surface-variant">旋转</span>
                <select v-model="content.rotation" class="w-full border rounded px-2 py-1 mt-0.5">
                  <option value="random">随机</option>
                  <option value="horizontal">水平</option>
                  <option value="vertical">垂直</option>
                  <option value="mixed">混合</option>
                </select>
              </label>
              <label class="block">
                <span class="text-[10px] text-on-surface-variant">背景透明度</span>
                <input v-model.number="content.backgroundAlpha" type="range" min="0" max="1" step="0.05" class="w-full" />
              </label>
            </section>
          </aside>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { nextTick, ref, watch } from 'vue'
import { WORD_CLOUD_SHAPES } from '../../constants/wordCloudShapes.js'
import { defaultWordCloudContent, parseTableText, parseUploadedFile, wordsFromManual } from '../../utils/parseSurveyData.js'
import { renderWordCloud } from './WordCloudRenderer.js'
import { useToast } from '../../composables/useToast.js'

const { error: toastError } = useToast()

const props = defineProps({
  open: { type: Boolean, default: false },
  themeId: { type: String, default: 'zjy-minimal' },
  initialContent: { type: Object, default: null },
})

const emit = defineEmits(['close', 'insert-vector', 'insert-image'])

const previewW = 400
const previewH = 400
const canvasRef = ref(null)
const content = ref(defaultWordCloudContent())
const newWord = ref('')
const pasteText = ref('')
const exporting = ref(false)

watch(
  () => props.open,
  async (v) => {
    if (!v) return
    content.value = { ...defaultWordCloudContent(), ...(props.initialContent || {}) }
    await nextTick()
    refreshPreview()
  },
  { immediate: true }
)

function refreshPreview() {
  nextTick(() => {
    if (!canvasRef.value) return
    renderWordCloud(canvasRef.value, content.value, props.themeId)
  })
}

function addWord() {
  const t = newWord.value.trim()
  if (!t) return
  content.value.words = wordsFromManual([...content.value.words, { text: t, weight: 50 }])
  newWord.value = ''
  refreshPreview()
}

function removeWord(i) {
  content.value.words.splice(i, 1)
  refreshPreview()
}

function importPaste() {
  const words = parseTableText(pasteText.value)
  if (words.length) {
    content.value.words = words
    refreshPreview()
  }
}

async function onFile(e) {
  const file = e.target.files?.[0]
  if (!file) return
  try {
    content.value.words = await parseUploadedFile(file)
    refreshPreview()
  } catch (err) {
    toastError(err.message || '文件解析失败')
  }
  e.target.value = ''
}

async function downloadImage() {
  exporting.value = true
  try {
    if (!canvasRef.value) return
    const { downloadDataUrl } = await import('../../utils/exportCanvasImage.js')
    downloadDataUrl(canvasRef.value.toDataURL('image/png'), 'wordcloud.png')
  } finally {
    exporting.value = false
  }
}

async function insertAsImage() {
  if (!canvasRef.value) return
  emit('insert-image', canvasRef.value.toDataURL('image/png'))
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
