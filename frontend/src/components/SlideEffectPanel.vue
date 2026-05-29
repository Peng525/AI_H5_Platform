<template>
  <div class="slide-effect-panel p-4 space-y-5 text-sm">
    <section>
      <h3 class="text-xs font-semibold text-on-surface mb-2 flex items-center gap-1">
        <span class="material-symbols-outlined text-[16px]">animation</span>
        页面切换动效
      </h3>
      <p class="text-xs text-on-surface/75 mb-2 leading-relaxed">应用于预览与分享时的翻页过渡</p>
      <div class="grid grid-cols-2 gap-2">
        <button
          v-for="a in PAGE_ANIMATIONS"
          :key="a.id"
          class="effect-option-btn flex items-center gap-2 px-2.5 py-2.5 rounded-lg border text-left text-xs font-medium transition-colors"
          :class="animation === a.id ? 'border-primary bg-white text-primary shadow-[inset_0_0_0_1px_#005daa]' : 'border-outline-variant bg-white text-on-surface hover:border-primary/50'"
          @click="pickAnimation(a.id)"
        >
          <span class="material-symbols-outlined text-[16px]">{{ a.icon }}</span>
          {{ a.label }}
        </button>
      </div>
    </section>

    <section>
      <h3 class="text-xs font-semibold text-on-surface mb-2 flex items-center gap-1">
        <span class="material-symbols-outlined text-[16px]">swap_vert</span>
        浏览滚动效果
      </h3>
      <p class="text-xs text-on-surface/75 mb-2 leading-relaxed">全局演示浏览方式（保存后，在顶部「预览」中体验）</p>
      <div class="space-y-2">
        <button
          v-for="s in SCROLL_EFFECTS"
          :key="s.id"
          class="effect-option-btn w-full text-left px-3 py-2.5 rounded-lg border bg-white transition-colors"
          :class="scrollEffect === s.id ? 'border-primary shadow-[inset_0_0_0_1px_#005daa]' : 'border-outline-variant hover:border-primary/50'"
          @click="pickScrollEffect(s.id)"
        >
          <div class="font-medium text-xs flex items-center gap-1.5" :class="scrollEffect === s.id ? 'text-primary' : 'text-on-surface'">
            <span class="material-symbols-outlined text-[14px]">{{ scrollModeIcon(s.id) }}</span>
            {{ s.label }}
          </div>
          <div class="text-[11px] text-on-surface/70 mt-0.5 leading-snug">{{ s.desc }}</div>
        </button>
      </div>
    </section>

    <button
      class="w-full py-2.5 text-xs font-medium border border-dashed border-outline-variant rounded-lg bg-white hover:border-primary/50 disabled:opacity-60"
      :disabled="previewing"
      @click="previewTransition"
    >
      {{ previewing ? '动效演示中…' : '预览当前页动效' }}
    </button>
    <p class="text-center text-[11px] text-on-surface/70 leading-relaxed">可重复点击预览，演示期间请稍候</p>

    <section class="border-t border-outline-variant pt-4">
      <ChatScriptEditor
        :slide="slide"
        @save="$emit('save', $event)"
        @open-generator="$emit('open-dialogue-generator')"
      />
    </section>

    <section v-if="showBgm" class="border-t border-outline-variant pt-4 space-y-3">
      <h3 class="text-xs font-semibold text-on-surface flex items-center gap-1">
        <span class="material-symbols-outlined text-[16px]">music_note</span>
        背景音乐
      </h3>
      <p class="text-xs text-on-surface/75 leading-relaxed">
        可选配置。开启后从曲库选择曲目，画布右上角播放器可静音或继续播放。
      </p>

      <button
        type="button"
        class="text-xs font-medium text-primary hover:text-primary/80 underline underline-offset-2"
        @click="toggleBgmEnabled"
      >
        {{ bgmEnabled ? '关闭背景音乐' : '启用背景音乐' }}
      </button>

      <template v-if="bgmEnabled">
        <p v-if="catalogLoading" class="text-[11px] text-on-surface/70">加载曲目列表…</p>
        <p v-else-if="!availableTracks.length" class="text-[11px] text-amber-800 leading-relaxed">
          暂无可用 MP3，请将文件放入 <code class="text-[11px]">backend/static/bgm/</code>
        </p>
        <div v-else class="space-y-1.5">
          <p class="text-xs font-medium text-on-surface">选择曲目</p>
          <button
            v-for="t in availableTracks"
            :key="t.id"
            type="button"
            class="effect-option-btn w-full text-left px-3 py-2 rounded-lg border bg-white transition-colors text-xs font-medium"
            :class="bgmTrackId === t.id ? 'border-primary text-primary shadow-[inset_0_0_0_1px_#005daa]' : 'border-outline-variant text-on-surface hover:border-primary/50'"
            @click="pickTrack(t)"
          >
            {{ t.title }}
          </button>
        </div>
        <p v-if="currentTrackLabel" class="text-[11px] text-on-surface/70">
          当前：{{ currentTrackLabel }}
        </p>
      </template>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import ChatScriptEditor from './ChatScriptEditor.vue'
import { PAGE_ANIMATIONS, SCROLL_EFFECTS } from '../constants/editorPresets'
import { useBgmCatalog } from '../composables/useBgmCatalog'

const props = defineProps({
  slide: { type: Object, default: null },
  scrollEffect: { type: String, default: 'page' },
  projectSettings: { type: Object, default: null },
  showBgm: { type: Boolean, default: true },
})

const emit = defineEmits(['save', 'scroll-change', 'preview-animation', 'bgm-change', 'open-dialogue-generator'])

const animation = ref('fade')
const previewing = ref(false)
let previewTimer = null

const { tracks: catalogTracks, loading: catalogLoading, loadBgmCatalog, findTrackById, findTrackByUrl } =
  useBgmCatalog()

const bgmEnabled = computed(() => !!props.projectSettings?.bgm?.enabled)
const bgmUrl = computed(() => props.projectSettings?.bgm?.url || '')
const bgmTrackId = computed(() => props.projectSettings?.bgm?.trackId || '')
const bgmVolume = computed(() => Number(props.projectSettings?.bgm?.volume ?? 0.35))

const availableTracks = computed(() => catalogTracks.value.filter((t) => t.available))

const currentTrackLabel = computed(() => {
  if (!bgmUrl.value) return ''
  const t = findTrackById(bgmTrackId.value) || findTrackByUrl(bgmUrl.value)
  return t?.title || bgmUrl.value
})

onMounted(() => {
  loadBgmCatalog()
})

function emitBgm(patch) {
  emit('bgm-change', patch)
}

function toggleBgmEnabled() {
  if (bgmEnabled.value) {
    emitBgm({ enabled: false })
    return
  }
  const first = availableTracks.value[0]
  if (first) {
    emitBgm({
      enabled: true,
      trackId: first.id,
      url: first.url,
      loop: true,
      volume: first.defaultVolume ?? bgmVolume.value,
    })
    return
  }
  emitBgm({ enabled: true, loop: true })
}

function pickTrack(track) {
  if (!track?.available) return
  emitBgm({
    enabled: true,
    trackId: track.id,
    url: track.url,
    loop: true,
    volume: track.defaultVolume ?? bgmVolume.value,
  })
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

<style scoped>
.slide-effect-panel {
  -webkit-font-smoothing: auto;
  -moz-osx-font-smoothing: auto;
}

.effect-option-btn {
  line-height: 1.35;
}
</style>
