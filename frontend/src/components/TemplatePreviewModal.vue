<template>
  <div
    v-if="open"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60"
    @click.self="$emit('close')"
  >
    <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden">
      <div class="flex items-center justify-between px-4 py-3 border-b border-outline-variant shrink-0">
        <div>
          <h2 class="font-semibold">{{ template?.title || '模板试看' }}</h2>
          <p class="text-xs text-on-surface-variant">{{ template?.pages }} 页 · 含对话演示</p>
        </div>
        <button type="button" class="p-2 rounded-lg hover:bg-surface-container" @click="$emit('close')">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>
      <div class="flex-1 min-h-0 relative bg-black">
        <div v-if="loading" class="absolute inset-0 flex items-center justify-center text-white text-sm">加载试看…</div>
        <PresentationViewer
          v-else-if="previewProject"
          :project="previewProject"
          :project-id="null"
          mode="share"
          embedded
          loading-text="加载试看…"
        />
      </div>
      <div class="px-4 py-3 border-t border-outline-variant flex justify-end gap-2 shrink-0">
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
import { ref, watch } from 'vue'
import { api } from '../api/client'
import PresentationViewer from './PresentationViewer.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  template: { type: Object, default: null },
})

defineEmits(['close', 'use'])

const loading = ref(false)
const previewProject = ref(null)

watch(
  () => [props.open, props.template?.id],
  async ([isOpen, id]) => {
    previewProject.value = null
    if (!isOpen || !id) return
    loading.value = true
    try {
      const tpl = await api.previewTemplate(id)
      previewProject.value = {
        id: 0,
        title: tpl.title,
        theme: tpl.id,
        share_slug: null,
        settings: tpl.settings_json || {},
        slides: (tpl.slides_json || []).map((s, i) => ({
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
        })),
      }
    } catch (e) {
      console.error(e)
    } finally {
      loading.value = false
    }
  },
  { immediate: true }
)
</script>
