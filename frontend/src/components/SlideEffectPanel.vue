<template>
  <div class="p-4 space-y-5 text-sm">
    <section>
      <h3 class="text-xs font-semibold text-on-surface-variant mb-2 flex items-center gap-1">
        <span class="material-symbols-outlined text-[16px]">animation</span>
        页面切换动效
      </h3>
      <p class="text-[11px] text-on-surface-variant mb-2">应用于预览与分享时的翻页过渡</p>
      <div class="grid grid-cols-2 gap-2">
        <button
          v-for="a in PAGE_ANIMATIONS"
          :key="a.id"
          class="flex items-center gap-2 px-2 py-2 rounded-lg border text-left text-xs transition"
          :class="animation === a.id ? 'border-primary bg-primary/5 text-primary font-medium' : 'border-outline-variant hover:border-outline'"
          @click="pickAnimation(a.id)"
        >
          <span class="material-symbols-outlined text-[16px]">{{ a.icon }}</span>
          {{ a.label }}
        </button>
      </div>
    </section>

    <section>
      <h3 class="text-xs font-semibold text-on-surface-variant mb-2 flex items-center gap-1">
        <span class="material-symbols-outlined text-[16px]">swap_vert</span>
        浏览滚动效果
      </h3>
      <p class="text-[11px] text-on-surface-variant mb-2">全局演示浏览方式（保存后，在顶部「预览」中体验）</p>
      <div class="space-y-2">
        <button
          v-for="s in SCROLL_EFFECTS"
          :key="s.id"
          class="w-full text-left px-3 py-2 rounded-lg border transition"
          :class="scrollEffect === s.id ? 'border-primary bg-primary/5' : 'border-outline-variant hover:bg-white'"
          @click="pickScrollEffect(s.id)"
        >
          <div class="font-medium text-xs flex items-center gap-1.5" :class="scrollEffect === s.id ? 'text-primary' : ''">
            <span class="material-symbols-outlined text-[14px]">{{ scrollModeIcon(s.id) }}</span>
            {{ s.label }}
          </div>
          <div class="text-[10px] text-on-surface-variant mt-0.5">{{ s.desc }}</div>
        </button>
      </div>
    </section>

    <button
      class="w-full py-2 text-xs border border-dashed border-outline-variant rounded-lg hover:bg-white disabled:opacity-60"
      :disabled="previewing"
      @click="previewTransition"
    >
      {{ previewing ? '动效演示中…' : '预览当前页动效' }}
    </button>
    <p class="text-center text-[10px] text-on-surface-variant">可重复点击预览，演示期间请稍候</p>

    <section class="border-t border-outline-variant pt-4">
      <ChatScriptEditor :slide="slide" @save="$emit('save', $event)" />
    </section>

    <section v-if="showBgm" class="border-t border-outline-variant pt-4 space-y-2">
      <h3 class="text-xs font-semibold text-on-surface-variant flex items-center gap-1">
        <span class="material-symbols-outlined text-[16px]">music_note</span>
        背景音乐
      </h3>
      <label class="flex items-center gap-2 text-xs">
        <input type="checkbox" :checked="bgmEnabled" @change="onBgmToggle" />
        预览时播放 BGM
      </label>
      <input
        :value="bgmUrl"
        class="w-full text-xs border rounded px-2 py-1.5"
        placeholder="/static/bgm/demo-loop.mp3"
        @change="onBgmUrl"
      />
      <label class="block text-[11px] text-on-surface-variant">
        音量 {{ Math.round(bgmVolume * 100) }}%
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          :value="bgmVolume"
          class="w-full"
          @input="onBgmVolume"
        />
      </label>
    </section>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import ChatScriptEditor from './ChatScriptEditor.vue'
import { PAGE_ANIMATIONS, SCROLL_EFFECTS } from '../constants/editorPresets'

const props = defineProps({
  slide: { type: Object, default: null },
  scrollEffect: { type: String, default: 'page' },
  projectSettings: { type: Object, default: null },
  showBgm: { type: Boolean, default: true },
})

const emit = defineEmits(['save', 'scroll-change', 'preview-animation', 'bgm-change'])

const animation = ref('fade')
const previewing = ref(false)
let previewTimer = null

const bgmEnabled = computed(() => !!props.projectSettings?.bgm?.enabled)
const bgmUrl = computed(() => props.projectSettings?.bgm?.url || '')
const bgmVolume = computed(() => Number(props.projectSettings?.bgm?.volume ?? 0.35))

function onBgmToggle(e) {
  emit('bgm-change', { enabled: e.target.checked })
}

function onBgmUrl(e) {
  emit('bgm-change', { url: e.target.value })
}

function onBgmVolume(e) {
  emit('bgm-change', { volume: Number(e.target.value) })
}

const PREVIEW_MS = 700

watch(
  () => props.slide,
  (s) => {
    animation.value = s?.animation || 'fade'
  },
  { immediate: true }
)

function pickAnimation(id) {
  animation.value = id
  emit('save', { animation: id })
  playPreview(id)
}

function pickScrollEffect(id) {
  emit('scroll-change', id)
}

function scrollModeIcon(id) {
  const icons = {
    page: 'menu_book',
    vertical: 'unfold_more',
    horizontal: 'swipe',
    snap: 'view_carousel',
  }
  return icons[id] || 'touch_app'
}

function previewTransition() {
  if (previewing.value) return
  playPreview(animation.value)
}

function playPreview(id) {
  clearTimeout(previewTimer)
  previewing.value = true
  emit('preview-animation', id)
  previewTimer = setTimeout(() => {
    previewing.value = false
  }, PREVIEW_MS)
}
</script>
