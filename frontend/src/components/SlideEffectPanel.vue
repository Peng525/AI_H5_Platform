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

    <section v-if="showBgm" class="border-t border-outline-variant pt-4 space-y-3">
      <h3 class="text-xs font-semibold text-on-surface-variant flex items-center gap-1">
        <span class="material-symbols-outlined text-[16px]">music_note</span>
        背景音乐
      </h3>
      <p class="text-[11px] text-on-surface-variant leading-relaxed">
        可选配置。关闭后预览与分享页不播放音乐；开启后请选择曲目或填写自定义地址。
      </p>

      <label class="flex items-center gap-2 text-xs cursor-pointer">
        <input type="checkbox" :checked="bgmEnabled" @change="onBgmToggle" />
        <span>启用背景音乐</span>
      </label>

      <template v-if="bgmEnabled">
        <div class="space-y-1.5">
          <label class="text-[11px] text-on-surface-variant">选择曲目</label>
          <select
            class="w-full text-xs border border-outline-variant rounded-lg px-2 py-2 bg-white"
            :value="selectedTrackKey"
            @change="onTrackSelect"
          >
            <option value="">— 不选曲目（仅自定义 URL）—</option>
            <option
              v-for="t in catalogTracks"
              :key="t.id"
              :value="t.id"
              :disabled="!t.available"
            >
              {{ t.title }}{{ t.available ? '' : '（未安装）' }}
            </option>
            <option value="__custom__">自定义 URL…</option>
          </select>
          <p v-if="catalogLoading" class="text-[10px] text-on-surface-variant">加载曲目列表…</p>
          <p v-else-if="!availableTrackCount" class="text-[10px] text-amber-700 leading-relaxed">
            暂无可用 MP3。将文件放入 <code class="text-[10px]">backend/media/bgm/</code> 或运行
            <code class="text-[10px]">scripts/install-bgm.ps1</code>
          </p>
          <p v-else-if="catalogHint" class="text-[10px] text-on-surface-variant">{{ catalogHint }}</p>
        </div>

        <div v-if="showCustomUrl" class="space-y-1">
          <label class="text-[11px] text-on-surface-variant">自定义音频地址</label>
          <input
            :value="bgmUrl"
            class="w-full text-xs border border-outline-variant rounded-lg px-2 py-1.5"
            placeholder="/static/bgm/happier-sakura-girl.mp3"
            @change="onBgmUrl"
          />
        </div>

        <p v-if="bgmEnabled && !bgmUrl" class="text-[10px] text-amber-700">
          已启用但未选择曲目，预览时将无音乐。
        </p>
        <p v-else-if="currentTrackLabel" class="text-[10px] text-on-surface-variant">
          当前：{{ currentTrackLabel }}
        </p>

        <label class="flex items-center gap-2 text-xs cursor-pointer">
          <input type="checkbox" :checked="bgmLoop" @change="onBgmLoop" />
          循环播放
        </label>

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

const emit = defineEmits(['save', 'scroll-change', 'preview-animation', 'bgm-change'])

const animation = ref('fade')
const previewing = ref(false)
let previewTimer = null

const { tracks: catalogTracks, loading: catalogLoading, hint: catalogHint, loadBgmCatalog, findTrackById, findTrackByUrl } =
  useBgmCatalog()

const bgmEnabled = computed(() => !!props.projectSettings?.bgm?.enabled)
const bgmUrl = computed(() => props.projectSettings?.bgm?.url || '')
const bgmTrackId = computed(() => props.projectSettings?.bgm?.trackId || '')
const bgmVolume = computed(() => Number(props.projectSettings?.bgm?.volume ?? 0.35))
const bgmLoop = computed(() => props.projectSettings?.bgm?.loop !== false)

const availableTrackCount = computed(() => catalogTracks.value.filter((t) => t.available).length)

const showCustomUrl = computed(() => {
  if (!bgmTrackId.value && bgmUrl.value) return true
  return selectedTrackKey.value === '__custom__'
})

const selectedTrackKey = computed(() => {
  if (bgmTrackId.value) return bgmTrackId.value
  if (bgmUrl.value && !findTrackByUrl(bgmUrl.value)) return '__custom__'
  const byUrl = findTrackByUrl(bgmUrl.value)
  if (byUrl) return byUrl.id
  return ''
})

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

function onBgmToggle(e) {
  const enabled = e.target.checked
  if (!enabled) {
    emitBgm({ enabled: false })
    return
  }
  emitBgm({ enabled: true })
  if (!bgmUrl.value && availableTrackCount.value > 0) {
    const first = catalogTracks.value.find((t) => t.available)
    if (first) {
      emitBgm({
        enabled: true,
        trackId: first.id,
        url: first.url,
        volume: first.defaultVolume ?? bgmVolume.value,
      })
    }
  }
}

function onTrackSelect(e) {
  const value = e.target.value
  if (!value) {
    emitBgm({ trackId: '', url: '' })
    return
  }
  if (value === '__custom__') {
    emitBgm({ trackId: '' })
    return
  }
  const track = findTrackById(value)
  if (!track || !track.available) return
  emitBgm({
    trackId: track.id,
    url: track.url,
    volume: track.defaultVolume ?? bgmVolume.value,
  })
}

function onBgmUrl(e) {
  const url = e.target.value.trim()
  const matched = findTrackByUrl(url)
  emitBgm({
    url,
    trackId: matched?.id || '',
  })
}

function onBgmLoop(e) {
  emitBgm({ loop: e.target.checked })
}

function onBgmVolume(e) {
  emitBgm({ volume: Number(e.target.value) })
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
