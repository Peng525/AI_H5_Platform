<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/40"
        @click.self="emit('cancel')"
      >
        <div
          class="bg-white rounded-xl shadow-elevated border border-outline-variant w-full max-w-3xl max-h-[90vh] flex flex-col overflow-hidden"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="titleId"
        >
          <div class="flex items-center justify-between gap-3 px-4 py-3 border-b border-outline-variant shrink-0">
            <div class="min-w-0">
              <h2 :id="titleId" class="font-semibold text-on-surface truncate">
                {{ template?.title || '模板预览' }}
              </h2>
              <p v-if="template?.description" class="text-xs text-on-surface-variant mt-0.5 truncate">
                {{ template.description }}
              </p>
            </div>
            <button
              type="button"
              class="shrink-0 text-on-surface-variant hover:text-on-surface p-1 rounded-lg hover:bg-surface-container-low"
              title="关闭"
              @click="emit('cancel')"
            >
              <span class="material-symbols-outlined text-[22px]">close</span>
            </button>
          </div>

          <div class="flex-1 min-h-0 overflow-auto p-4 bg-surface-container-low">
            <img
              v-if="mode === 'visual' && previewSrc"
              :src="previewSrc"
              :alt="template?.title"
              class="max-h-[70vh] w-full object-contain object-top mx-auto block rounded-lg border border-outline-variant bg-white"
            />
            <p v-else-if="mode === 'visual'" class="text-sm text-on-surface-variant text-center py-12">
              暂无预览图
            </p>
            <div v-else class="space-y-3">
              <div
                v-if="promptBody"
                class="rounded-lg border border-outline-variant bg-white p-4 text-sm text-on-surface whitespace-pre-wrap leading-relaxed max-h-[60vh] overflow-y-auto"
              >
                {{ promptBody }}
              </div>
              <table
                v-if="template?.fields?.length"
                class="w-full text-xs text-on-surface-variant border-collapse bg-white rounded-lg border border-outline-variant overflow-hidden"
              >
                <tbody>
                  <tr
                    v-for="field in template.fields"
                    :key="field.label"
                    class="border-b border-outline-variant/50 last:border-0"
                  >
                    <td class="px-3 py-2 font-medium text-on-surface/80 w-16 shrink-0">{{ field.label }}</td>
                    <td class="px-3 py-2 leading-snug">{{ field.value }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="flex justify-between items-center gap-6 px-6 py-4 border-t border-outline-variant bg-white shrink-0">
            <button
              type="button"
              class="min-w-[7rem] px-5 py-2.5 rounded-lg border border-outline-variant text-sm font-medium text-on-surface hover:bg-surface-container-low transition"
              @click="emit('cancel')"
            >
              取消
            </button>
            <button
              type="button"
              class="min-w-[7rem] px-5 py-2.5 rounded-lg bg-primary text-on-primary text-sm font-medium hover:bg-primary/90 transition"
              @click="emit('confirm')"
            >
              选择此模板
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, useId } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  template: { type: Object, default: null },
  mode: { type: String, default: 'visual' },
  resolvePreviewUrl: {
    type: Function,
    default: (url) => url || '',
  },
})

const emit = defineEmits(['confirm', 'cancel'])

const titleId = useId()

const previewSrc = computed(() =>
  props.resolvePreviewUrl(props.template?.preview_url || ''),
)

const promptBody = computed(() =>
  props.template?.prompt_full
  || props.template?.prompt_hint
  || props.template?.description
  || '',
)
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
