<template>
  <section>
    <h2 v-if="heading" class="text-sm font-semibold text-on-surface-variant mb-3">{{ heading }}</h2>
    <p v-if="!templates.length" class="text-sm text-on-surface-variant py-4 text-center">暂无模板</p>
    <ul v-else class="flex md:grid md:grid-cols-3 gap-2 overflow-x-auto pb-1">
      <li v-for="tpl in templates" :key="tpl.id" class="snap-start shrink-0 w-[min(78vw,14rem)] md:w-auto">
        <PromptTemplateCard
          :title="tpl.title"
          :description="tpl.description"
          :fields="[]"
          :preview-url="tpl.preview_url || ''"
          :selected="selectedId === tpl.id"
          @select="$emit('select', tpl)"
        />
      </li>
    </ul>
  </section>
</template>

<script setup>
import PromptTemplateCard from '../create/PromptTemplateCard.vue'

defineProps({
  templates: { type: Array, default: () => [] },
  selectedId: { type: String, default: '' },
  heading: { type: String, default: '选择简历模板' },
})

defineEmits(['select'])
</script>
