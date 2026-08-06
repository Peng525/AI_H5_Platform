<template>
  <div class="space-y-4">
    <!-- Step 1: visual templates -->
    <template v-if="step === 'visual'">
      <ResumeTemplatePicker
        heading="选择简历模板（必选）"
        variant="visual"
        :templates="visualTemplates"
        :selected-id="selectedVisualId"
        @select="$emit('select-visual', $event)"
      />
      <p v-if="templateError" class="text-sm text-red-600">{{ templateError }}</p>
    </template>

    <!-- Step 2: prompt templates -->
    <template v-else>
      <div class="flex items-center justify-between gap-2">
        <button
          type="button"
          class="inline-flex items-center gap-1 text-sm text-primary hover:underline"
          @click="$emit('back-visual')"
        >
          <span class="material-symbols-outlined text-[18px]">arrow_back</span>
          返回选择模板
        </button>
        <span v-if="selectedVisualTitle" class="text-xs text-on-surface-variant truncate">
          已选：{{ selectedVisualTitle }}
        </span>
      </div>

      <section class="space-y-3">
        <h2 class="text-sm font-semibold text-on-surface-variant">选择行业</h2>
        <ResumeIndustryChips
          :industries="industries"
          :selected-id="selectedIndustryId"
          @update:selected-id="$emit('update:industry', $event)"
        />
      </section>

      <PageLoading v-if="promptLoading && !promptTemplates.length" message="加载提示词…" />
      <p v-else-if="promptError" class="text-sm text-red-600">{{ promptError }}</p>
      <ResumeTemplatePicker
        v-else
        heading="选择提示词模板（写作规则）"
        variant="prompt"
        :templates="promptTemplates"
        :selected-id="selectedPromptId"
        show-fields
        @select="$emit('select-prompt', $event)"
      />
    </template>
  </div>
</template>

<script setup>
import PageLoading from '../PageLoading.vue'
import ResumeIndustryChips from './ResumeIndustryChips.vue'
import ResumeTemplatePicker from './ResumeTemplatePicker.vue'

defineProps({
  step: { type: String, default: 'visual' },
  visualTemplates: { type: Array, default: () => [] },
  promptTemplates: { type: Array, default: () => [] },
  industries: { type: Array, default: () => [] },
  selectedVisualId: { type: String, default: '' },
  selectedVisualTitle: { type: String, default: '' },
  selectedPromptId: { type: String, default: '' },
  selectedIndustryId: { type: String, default: 'all' },
  templateError: { type: String, default: '' },
  promptLoading: { type: Boolean, default: false },
  promptError: { type: String, default: '' },
})

defineEmits(['select-visual', 'select-prompt', 'back-visual', 'update:industry'])
</script>
