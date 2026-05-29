<template>
  <div class="bgm-panel p-4 space-y-4 text-sm">
    <div>
      <h3 class="text-xs font-semibold text-on-surface flex items-center gap-1 mb-2">
        <span class="material-symbols-outlined text-[16px]">music_note</span>
        背景音乐
      </h3>
      <p class="text-xs text-on-surface/75 leading-relaxed mb-3">
        可选配置。开启后从曲库选择曲目，幻灯片右上角播放器可静音或继续播放。
      </p>

      <button
        type="button"
        class="text-xs font-medium text-primary hover:text-primary/80 underline underline-offset-2"
        @click="toggleBgmEnabled"
      >
        {{ bgmEnabled ? '关闭背景音乐' : '启用背景音乐' }}
      </button>
    </div>

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
          class="bgm-track-btn w-full text-left px-3 py-2 rounded-lg border bg-white transition-colors text-xs font-medium"
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
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useBgmCatalog } from '../composables/useBgmCatalog'

const props = defineProps({
  projectSettings: { type: Object, default: null },
})

const emit = defineEmits(['bgm-change'])

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
</script>

<style scoped>
.bgm-panel {
  -webkit-font-smoothing: auto;
  -moz-osx-font-smoothing: auto;
}

.bgm-track-btn {
  line-height: 1.35;
}
</style>
