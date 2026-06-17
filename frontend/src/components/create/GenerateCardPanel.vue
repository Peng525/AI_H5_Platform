<template>
  <div
    data-generate-card-panel
    class="max-w-2xl mx-auto w-full px-2 sm:px-4 text-white"
    @mousedown.stop
    @click.stop
  >
    <div class="flex items-center justify-between gap-3 mb-2">
      <p v-if="quotaRemaining != null" class="inline-flex items-center gap-1 text-sm text-white/90">
        <span class="material-symbols-outlined text-[16px]">auto_awesome</span>
        剩余 {{ quotaRemaining }} / {{ quotaTotal }}
      </p>
      <div v-else class="flex-1" />
      <div class="flex items-center gap-2 ml-auto">
        <label class="relative inline-flex items-center">
          <select v-model="language" class="panel-pill-select" :disabled="loading">
            <option value="简体中文">简体中文</option>
            <option value="English">English</option>
          </select>
          <span class="material-symbols-outlined panel-pill-chevron">expand_more</span>
        </label>
        <button
          type="button"
          class="p-1 rounded-lg text-white/80 hover:text-white hover:bg-white/10 transition-colors"
          aria-label="关闭"
          :disabled="loading"
          @click="$emit('close')"
        >
          <span class="material-symbols-outlined text-[20px]">close</span>
        </button>
      </div>
    </div>

    <h2 id="generate-card-title" class="text-base font-semibold text-white mb-3 text-left">Generate card</h2>

    <GenerateTopicInput
      v-model="prompt"
      show-send
      :rows="3"
      :auto-resize="false"
      placeholder="描述你想制作的内容…"
      :disabled="loading"
      :loading="loading"
      @submit="submit"
    />

    <div class="mt-4">
      <GenerateTemplatePicker
        v-model="templateUiId"
        :disabled="loading"
        @update:template-hint="templateHint = $event"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import GenerateTopicInput from './GenerateTopicInput.vue'
import GenerateTemplatePicker from './GenerateTemplatePicker.vue'

const props = defineProps({
  loading: { type: Boolean, default: false },
  quotaRemaining: { type: Number, default: null },
  quotaTotal: { type: Number, default: null },
})

const emit = defineEmits(['close', 'generate'])

const prompt = ref('')
const templateUiId = ref('magic')
const templateHint = ref('magic')
const language = ref('简体中文')

function submit() {
  const text = prompt.value.trim()
  if (!text || props.loading) return
  emit('generate', {
    prompt: text,
    templateHint: templateHint.value,
    language: language.value,
  })
}
</script>

<style scoped>
.panel-pill-select {
  @apply appearance-none rounded-full border border-white/25 bg-white/10 pl-2.5 pr-7 py-0.5 text-xs text-white cursor-pointer hover:bg-white/15 transition disabled:opacity-50;
}

.panel-pill-chevron {
  @apply absolute right-1.5 text-[15px] text-white/70 pointer-events-none;
}
</style>
