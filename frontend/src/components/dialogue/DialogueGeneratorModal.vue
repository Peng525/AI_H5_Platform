<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 z-[200] bg-surface-container-low flex flex-col"
      >
        <header class="shrink-0 flex flex-wrap items-center justify-between gap-2 px-3 sm:px-4 py-3 border-b border-outline-variant bg-white">
          <div class="flex items-center gap-2 min-w-0">
            <span class="material-symbols-outlined text-primary shrink-0">forum</span>
            <h1 class="text-base sm:text-lg font-bold truncate">对话生成器</h1>
          </div>
          <div class="flex items-center gap-1.5 sm:gap-2 flex-wrap justify-end">
            <button
              type="button"
              class="px-2.5 sm:px-3 py-1.5 text-xs sm:text-sm border border-outline-variant rounded-lg hover:bg-surface-container-low"
              :disabled="exporting"
              @click="downloadImage"
            >
              {{ exporting ? '导出中…' : '下载图片' }}
            </button>
            <button
              type="button"
              class="px-2.5 sm:px-3 py-1.5 text-xs sm:text-sm bg-primary text-on-primary rounded-lg font-medium"
              @click="insertIntoSlide"
            >
              插入当前页
            </button>
            <button type="button" class="p-2 rounded-lg hover:bg-surface-container" @click="$emit('close')">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
        </header>

        <div class="flex-1 min-h-0 overflow-auto">
          <div class="dialogue-generator-body flex flex-row min-h-full min-w-[44rem]">
            <aside class="w-28 xl:w-36 shrink-0 border-r border-outline-variant bg-white overflow-y-auto p-2 flex flex-col gap-2">
              <p class="text-[10px] font-semibold text-on-surface-variant px-1 shrink-0">样式预设</p>
              <button
                v-for="preset in CHAT_STYLE_PRESETS"
                :key="preset.id"
                type="button"
                class="w-full rounded-lg border p-2 text-left transition hover:border-primary"
                :class="localScript.style?.presetId === preset.id ? 'border-primary ring-1 ring-primary' : 'border-outline-variant'"
                @click="applyPreset(preset)"
              >
                <div class="flex gap-1 mb-1 h-5">
                  <span class="flex-1 rounded-full" :style="{ background: preset.thumb.owner }" />
                  <span class="flex-1 rounded-full border border-black/10" :style="{ background: preset.thumb.other }" />
                </div>
                <span class="text-[10px]">{{ preset.label }}</span>
              </button>
            </aside>

            <main class="flex-1 min-w-[14rem] min-h-0 h-full flex items-center justify-center p-3 sm:p-6 bg-[#e8eaed] overflow-hidden">
              <PhoneDeviceFrame ref="phoneFrameRef" class="shrink-0 h-full max-h-full" fit="contain">
                <DialoguePreviewCanvas
                  v-model="localScript"
                  editable
                  @select-index="onSelectTimelineIndex"
                />
              </PhoneDeviceFrame>
            </main>

            <aside class="w-52 xl:w-56 shrink-0 border-l border-outline-variant bg-white overflow-y-auto p-3 space-y-4 text-xs">
            <section>
              <h3 class="font-semibold text-on-surface-variant mb-2">圆角</h3>
              <label class="block mb-2">
                <span class="text-[10px] text-on-surface-variant">头像圆角 (px)</span>
                <input
                  v-model.number="localScript.style.avatarRadius"
                  type="number"
                  min="0"
                  max="50"
                  class="w-full mt-0.5 border rounded px-2 py-1"
                />
              </label>
              <label class="block">
                <span class="text-[10px] text-on-surface-variant">气泡圆角 (px)</span>
                <input
                  v-model.number="localScript.style.bubbleRadius"
                  type="number"
                  min="0"
                  max="24"
                  class="w-full mt-0.5 border rounded px-2 py-1"
                />
              </label>
            </section>

            <section>
              <h3 class="font-semibold text-on-surface-variant mb-2">颜色</h3>
              <label v-for="row in colorRows" :key="row.key" class="flex items-center justify-between gap-2 mb-1.5">
                <span class="text-[10px] text-on-surface-variant shrink-0">{{ row.label }}</span>
                <input
                  v-model="localScript.style[row.key]"
                  type="color"
                  class="w-8 h-6 border-0 cursor-pointer p-0"
                />
              </label>
            </section>

            <section v-if="selectedParticipant">
              <h3 class="font-semibold text-on-surface-variant mb-2">参与者头像</h3>
              <p class="text-[10px] text-on-surface-variant mb-2">{{ selectedParticipant.name }}</p>
              <div class="flex items-center gap-2 mb-3">
                <div
                  class="w-12 h-12 bg-gray-200 flex items-center justify-center text-sm font-semibold text-gray-600 overflow-hidden shrink-0"
                  :style="{ borderRadius: `${localScript.style.avatarRadius || 6}px` }"
                >
                  <img
                    v-if="selectedParticipant.avatar && !selectedParticipant.useDefaultAvatar"
                    :src="selectedParticipant.avatar"
                    alt=""
                    class="w-full h-full object-cover"
                  />
                  <span v-else>{{ selectedParticipant.name?.slice(0, 1) || '用' }}</span>
                </div>
                <div class="flex flex-col gap-1.5 min-w-0">
                  <label class="cursor-pointer px-2 py-1.5 text-[10px] border border-outline-variant rounded-lg text-center hover:bg-surface-container-low">
                    上传头像
                    <input type="file" accept="image/*" class="hidden" @change="onAvatarUpload" />
                  </label>
                  <button
                    type="button"
                    class="px-2 py-1.5 text-[10px] border border-outline-variant rounded-lg hover:bg-surface-container-low"
                    @click="useDefaultAvatar"
                  >
                    使用默认
                  </button>
                </div>
              </div>
              <input
                v-model="selectedParticipant.name"
                class="w-full border rounded px-2 py-1 text-xs mb-2"
                placeholder="昵称"
                @input="syncScript"
              />
              <label class="block">
                <span class="text-[10px] text-on-surface-variant">内容</span>
                <textarea
                  v-model="selectedMessageText"
                  rows="3"
                  class="mt-0.5 w-full border rounded px-2 py-1.5 text-xs resize-y min-h-[4.5rem]"
                  placeholder="你好，小文"
                />
              </label>
            </section>
            <section v-else>
              <h3 class="font-semibold text-on-surface-variant mb-2">参与者</h3>
              <p class="text-[10px] text-on-surface-variant leading-relaxed">
                选中一条消息后，右侧可编辑昵称与内容（实时同步到气泡）。点击 + 可添加时间戳或添加用户。
              </p>
            </section>

            <section>
              <h3 class="font-semibold text-on-surface-variant mb-2">播放方式</h3>
              <div class="grid grid-cols-2 gap-2 mb-2">
                <button
                  type="button"
                  class="px-2 py-2 rounded-lg border text-[11px] font-medium transition"
                  :class="playbackMode === 'click' ? 'border-primary bg-primary/5 text-primary' : 'border-outline-variant hover:bg-surface-container-low'"
                  @click="setPlaybackMode('click')"
                >
                  点击播放
                </button>
                <button
                  type="button"
                  class="px-2 py-2 rounded-lg border text-[11px] font-medium transition"
                  :class="playbackMode === 'auto' ? 'border-primary bg-primary/5 text-primary' : 'border-outline-variant hover:bg-surface-container-low'"
                  @click="setPlaybackMode('auto')"
                >
                  自动播放
                </button>
              </div>
              <p class="text-[10px] text-on-surface-variant leading-relaxed mb-2">
                {{ playbackMode === 'click' ? '预览/分享时点击屏幕逐句显示下一条消息。' : '预览/分享时按间隔自动逐句弹出，仍可点击加速。' }}
              </p>
              <label v-if="playbackMode === 'auto'" class="block text-[10px] text-on-surface-variant">
                逐句间隔 (ms)
                <input
                  :value="autoIntervalDraft"
                  type="text"
                  inputmode="numeric"
                  class="w-full mt-0.5 border rounded px-2 py-1"
                  placeholder="例如 200"
                  @input="onAutoIntervalInput"
                  @blur="commitAutoInterval"
                  @keydown.enter="commitAutoInterval"
                />
              </label>
            </section>
            </aside>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import DialoguePreviewCanvas from './DialoguePreviewCanvas.vue'
import PhoneDeviceFrame from '../PhoneDeviceFrame.vue'
import { CHAT_STYLE_PRESETS } from '../../constants/chatStylePresets.js'
import { emptyChatScript, normalizeChatScript, serializeChatScript } from '../../utils/chatScript.js'
import { downloadElementAsPng } from '../../utils/exportCanvasImage.js'

const props = defineProps({
  open: { type: Boolean, default: false },
  initialScript: { type: Object, default: null },
})

const emit = defineEmits(['close', 'insert'])

const localScript = ref(emptyChatScript())
const exporting = ref(false)
const phoneFrameRef = ref(null)
const selectedTimelineIndex = ref(-1)
const autoIntervalDraft = ref('1500')

const AUTO_INTERVAL_MIN = 100
const AUTO_INTERVAL_MAX = 60000
const AUTO_INTERVAL_DEFAULT = 1500

const colorRows = [
  { key: 'ownerBgColor', label: '右侧气泡' },
  { key: 'ownerTextColor', label: '右侧文字' },
  { key: 'otherBgColor', label: '左侧气泡' },
  { key: 'otherTextColor', label: '左侧文字' },
  { key: 'dateTextColor', label: '日期文字' },
  { key: 'background', label: '对话背景' },
]

const selectedParticipant = computed(() => {
  const idx = selectedTimelineIndex.value
  if (idx < 0) return null
  const item = localScript.value.timeline?.[idx]
  if (!item || item.type !== 'message') return null
  return localScript.value.participants?.find((p) => p.id === item.participantId) || null
})

const selectedMessageText = computed({
  get() {
    const idx = selectedTimelineIndex.value
    const item = localScript.value.timeline?.[idx]
    if (!item || item.type !== 'message') return ''
    return item.text ?? ''
  },
  set(text) {
    const idx = selectedTimelineIndex.value
    if (idx < 0) return
    const timeline = localScript.value.timeline.map((t, i) =>
      i === idx && t.type === 'message' ? { ...t, text } : t
    )
    localScript.value = { ...localScript.value, timeline }
  },
})

const playbackMode = computed({
  get() {
    const n = normalizeChatScript(localScript.value)
    return n.playbackMode
  },
  set(mode) {
    const next = normalizeChatScript({ ...localScript.value, playbackMode: mode })
    localScript.value = { ...localScript.value, playbackMode: next.playbackMode, autoAdvanceMs: next.autoAdvanceMs }
  },
})

function syncAutoIntervalDraft() {
  const ms = Number(localScript.value.autoAdvanceMs || 0)
  autoIntervalDraft.value = String(ms > 0 ? ms : AUTO_INTERVAL_DEFAULT)
}

function onAutoIntervalInput(e) {
  autoIntervalDraft.value = e.target.value.replace(/[^\d]/g, '')
}

function commitAutoInterval() {
  const raw = autoIntervalDraft.value.trim()
  const n = parseInt(raw, 10)
  const ms = Number.isFinite(n)
    ? Math.min(AUTO_INTERVAL_MAX, Math.max(AUTO_INTERVAL_MIN, n))
    : AUTO_INTERVAL_DEFAULT
  autoIntervalDraft.value = String(ms)
  localScript.value = { ...localScript.value, playbackMode: 'auto', autoAdvanceMs: ms }
}

function setPlaybackMode(mode) {
  playbackMode.value = mode
  if (mode === 'auto') syncAutoIntervalDraft()
}

watch(
  () => [props.open, props.initialScript],
  () => {
    if (!props.open) return
    selectedTimelineIndex.value = -1
    localScript.value = normalizeChatScript(
      props.initialScript?.enabled !== false ? props.initialScript : { ...emptyChatScript(), enabled: true }
    )
    syncAutoIntervalDraft()
  },
  { immediate: true, deep: true }
)

function onSelectTimelineIndex(i) {
  selectedTimelineIndex.value = i
}

function applyPreset(preset) {
  localScript.value = {
    ...localScript.value,
    style: { ...preset.style },
  }
}

function syncScript() {
  localScript.value = { ...localScript.value }
}

function onAvatarUpload(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  const p = selectedParticipant.value
  if (!file || !p) return
  const reader = new FileReader()
  reader.onload = () => {
    p.avatar = reader.result
    p.useDefaultAvatar = false
    syncScript()
  }
  reader.readAsDataURL(file)
}

function useDefaultAvatar() {
  const p = selectedParticipant.value
  if (!p) return
  p.avatar = ''
  p.useDefaultAvatar = true
  syncScript()
}

async function downloadImage() {
  exporting.value = true
  try {
    const el = phoneFrameRef.value?.$el || document.querySelector('.dialogue-preview')
    if (el) await downloadElementAsPng(el, 'dialogue.png')
  } finally {
    exporting.value = false
  }
}

function getSerialized() {
  if (playbackMode.value === 'auto') commitAutoInterval()
  return serializeChatScript({ ...localScript.value, enabled: true })
}

function insertIntoSlide() {
  emit('insert', getSerialized())
}

defineExpose({ getSerialized, insertIntoSlide })
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

.dialogue-generator-body {
  height: 100%;
}
</style>
