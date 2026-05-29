<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 z-[200] bg-surface-container-low flex flex-col"
      >
        <header class="shrink-0 flex items-center justify-between px-4 py-3 border-b border-outline-variant bg-white">
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">forum</span>
            <h1 class="text-lg font-bold">对话生成器</h1>
          </div>
          <div class="flex items-center gap-2">
            <button
              type="button"
              class="px-3 py-1.5 text-sm border border-outline-variant rounded-lg hover:bg-surface-container-low"
              :disabled="exporting"
              @click="downloadImage"
            >
              {{ exporting ? '导出中…' : '下载图片' }}
            </button>
            <button
              type="button"
              class="px-3 py-1.5 text-sm bg-primary text-on-primary rounded-lg font-medium"
              @click="$emit('insert', getSerialized())"
            >
              插入当前页
            </button>
            <button type="button" class="p-2 rounded-lg hover:bg-surface-container" @click="$emit('close')">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
        </header>

        <div class="flex-1 flex min-h-0">
          <aside class="w-36 shrink-0 border-r border-outline-variant bg-white overflow-y-auto p-2 space-y-2">
            <p class="text-[10px] font-semibold text-on-surface-variant px-1">样式预设</p>
            <button
              v-for="preset in CHAT_STYLE_PRESETS"
              :key="preset.id"
              type="button"
              class="w-full rounded-lg border p-2 text-left transition hover:border-primary"
              :class="localScript.style?.presetId === preset.id ? 'border-primary ring-1 ring-primary' : 'border-outline-variant'"
              @click="applyPreset(preset)"
            >
              <div class="flex gap-1 mb-1 h-6">
                <span class="flex-1 rounded-sm" :style="{ background: preset.thumb.owner }" />
                <span class="flex-1 rounded-sm border border-black/10" :style="{ background: preset.thumb.other }" />
              </div>
              <span class="text-[10px]">{{ preset.label }}</span>
            </button>
          </aside>

          <main class="flex-1 min-w-0 flex items-center justify-center p-6 bg-[#e8eaed]">
            <div
              class="w-full max-w-[375px] h-[min(640px,80vh)] bg-white shadow-2xl rounded-2xl overflow-hidden border border-outline-variant/50"
            >
              <DialoguePreviewCanvas v-model="localScript" editable />
            </div>
          </main>

          <aside class="w-56 shrink-0 border-l border-outline-variant bg-white overflow-y-auto p-3 space-y-4 text-xs">
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

            <section>
              <h3 class="font-semibold text-on-surface-variant mb-2">参与者</h3>
              <div
                v-for="p in localScript.participants"
                :key="p.id"
                class="border border-outline-variant rounded-lg p-2 mb-2 space-y-1"
              >
                <input v-model="p.name" class="w-full border rounded px-2 py-1 text-xs" placeholder="昵称" />
                <input v-model="p.avatar" class="w-full border rounded px-2 py-1 text-[10px]" placeholder="头像 URL" />
                <select v-model="p.defaultSide" class="w-full border rounded px-2 py-1 text-xs">
                  <option value="left">默认左侧</option>
                  <option value="right">默认右侧</option>
                </select>
                <select v-model="p.role" class="w-full border rounded px-2 py-1 text-xs">
                  <option value="owner">主人</option>
                  <option value="guest">访客</option>
                </select>
              </div>
              <button
                type="button"
                class="w-full py-1.5 border border-dashed border-outline-variant rounded text-[10px]"
                @click="addParticipant"
              >
                + 新用户
              </button>
            </section>

            <section>
              <label class="block text-[10px] text-on-surface-variant">
                自动逐句间隔 (ms，0=点击)
                <input
                  v-model.number="localScript.autoAdvanceMs"
                  type="number"
                  min="0"
                  step="500"
                  class="w-full mt-0.5 border rounded px-2 py-1"
                />
              </label>
            </section>
          </aside>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'
import DialoguePreviewCanvas from './DialoguePreviewCanvas.vue'
import { CHAT_STYLE_PRESETS } from '../../constants/chatStylePresets.js'
import { emptyChatScript, genChatId, normalizeChatScript, serializeChatScript } from '../../utils/chatScript.js'
import { downloadElementAsPng } from '../../utils/exportCanvasImage.js'

const props = defineProps({
  open: { type: Boolean, default: false },
  initialScript: { type: Object, default: null },
})

defineEmits(['close', 'insert'])

const localScript = ref(emptyChatScript())
const exporting = ref(false)

const colorRows = [
  { key: 'ownerBgColor', label: '主人气泡背景' },
  { key: 'ownerTextColor', label: '主人文字' },
  { key: 'otherBgColor', label: '他人气泡背景' },
  { key: 'otherTextColor', label: '他人文字' },
  { key: 'dateTextColor', label: '日期文字' },
  { key: 'background', label: '对话背景' },
]

watch(
  () => [props.open, props.initialScript],
  () => {
    if (!props.open) return
    localScript.value = normalizeChatScript(
      props.initialScript?.enabled !== false ? props.initialScript : { ...emptyChatScript(), enabled: true }
    )
  },
  { immediate: true, deep: true }
)

function applyPreset(preset) {
  localScript.value = {
    ...localScript.value,
    style: { ...preset.style },
  }
}

function addParticipant() {
  const n = localScript.value.participants.length
  localScript.value.participants.push({
    id: genChatId('p'),
    name: `用户${String.fromCharCode(65 + n)}`,
    avatar: '',
    role: 'guest',
    defaultSide: 'left',
  })
}

async function downloadImage() {
  exporting.value = true
  try {
    const el = document.querySelector('.dialogue-preview')
    if (el) await downloadElementAsPng(el, 'dialogue.png')
  } finally {
    exporting.value = false
  }
}

function getSerialized() {
  return serializeChatScript({ ...localScript.value, enabled: true })
}

defineExpose({ getSerialized })
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
