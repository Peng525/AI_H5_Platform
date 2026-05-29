<template>
  <div
    v-if="open"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60"
    @click.self="$emit('close')"
  >
    <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl h-[min(90vh,820px)] flex flex-col overflow-hidden">
      <div class="flex items-center justify-between px-4 py-3 border-b border-outline-variant shrink-0">
        <div>
          <h2 class="font-semibold">{{ template?.title || '模板试看' }}</h2>
          <p class="text-xs text-on-surface-variant">
            {{ template?.pages || 0 }} 页
            <span v-if="template?.featured"> · 含对话演示</span>
            <span v-else-if="!hasPreviewSlides"> · 试看内容待完善，使用后可编辑</span>
          </p>
        </div>
        <button type="button" class="p-2 rounded-lg hover:bg-surface-container" @click="$emit('close')">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>
      <div class="flex-1 min-h-[480px] relative bg-black overflow-hidden">
        <div v-if="loading" class="absolute inset-0 flex items-center justify-center text-white text-sm z-10">
          加载试看…
        </div>
        <div
          v-else-if="loadError"
          class="absolute inset-0 flex items-center justify-center text-red-300 text-sm px-6 text-center z-10"
        >
          {{ loadError }}
        </div>
        <div
          v-else-if="!hasPreviewSlides"
          class="absolute inset-0 flex flex-col items-center justify-center text-white/80 text-sm px-6 text-center z-10 gap-2"
        >
          <span class="material-symbols-outlined text-4xl text-white/40">slideshow</span>
          <p>该模板试看内容尚未就绪，可先「使用此模板」在编辑器中编辑。</p>
        </div>
        <PresentationViewer
          v-else-if="previewProject"
          :project="previewProject"
          :project-id="null"
          mode="share"
          embedded
          loading-text="加载试看…"
        />
      </div>
      <div class="px-4 py-3 border-t border-outline-variant flex justify-end gap-2 shrink-0 bg-white">
        <button type="button" class="px-4 py-2 rounded-lg border border-outline-variant text-sm" @click="$emit('close')">
          关闭
        </button>
        <button type="button" class="px-4 py-2 rounded-lg bg-primary text-on-primary text-sm font-medium" @click="$emit('use')">
          使用此模板
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { api } from '../api/client'
import PresentationViewer from './PresentationViewer.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  template: { type: Object, default: null },
})

defineEmits(['close', 'use'])

const loading = ref(false)
const loadError = ref('')
const previewProject = ref(null)

const hasPreviewSlides = computed(() => (previewProject.value?.slides?.length || 0) > 0)

watch(
  () => [props.open, props.template?.id],
  async ([isOpen, id]) => {
    previewProject.value = null
    loadError.value = ''
    if (!isOpen || !id) return
    loading.value = true
    try {
      const tpl = await api.previewTemplate(id)
      const slides = (tpl.slides_json || []).map((s, i) => ({
        id: i + 1,
        sort_order: i,
        layout: s.layout || 'bullets',
        title: s.title || '',
        subtitle: s.subtitle || '',
        bullets: s.bullets || [],
        speaker_notes: s.speakerNotes || s.speaker_notes || '',
        animation: s.animation || 'fade',
        canvas_elements: s.canvas_elements || [],
        chat_script: s.chat_script?.enabled ? s.chat_script : null,
        canvas_background: s.canvas_background || null,
      }))
      previewProject.value = {
        id: 0,
        title: tpl.title,
        theme: tpl.id,
        share_slug: null,
        settings: tpl.settings_json || {},
        slides,
      }
    } catch (e) {
      loadError.value = e.message || '无法加载模板试看'
      console.error(e)
    } finally {
      loading.value = false
    }
  },
  { immediate: true }
)
</script>
