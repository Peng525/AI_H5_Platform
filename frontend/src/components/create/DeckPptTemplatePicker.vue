<template>
  <section class="space-y-4">
    <h2 v-if="heading" class="text-sm font-semibold text-on-surface-variant">{{ heading }}</h2>

    <p v-if="loading" class="text-sm text-on-surface-variant py-4 text-center">加载模板…</p>
    <p v-else-if="loadError" class="text-sm text-red-600">
      {{ loadError }}
      <button type="button" class="text-primary ml-2 hover:underline" @click="emit('retry')">重试</button>
    </p>
    <p v-else-if="!templates.length" class="text-sm text-on-surface-variant py-4 text-center">暂无 PPT 模板</p>

    <template v-else>
      <ResumeIndustryChips
        :industries="categoryChips"
        :selected-id="selectedCategory"
        @update:selected-id="selectedCategory = $event"
      />

      <p v-if="!filteredTemplates.length" class="text-sm text-on-surface-variant py-4 text-center">
        {{ emptyMessage }}
      </p>

      <div v-for="group in displayGroups" v-else :key="group.key" class="space-y-2">
        <h3 v-if="group.label" class="text-xs font-medium text-on-surface-variant/80">{{ group.label }}</h3>
        <ul class="flex md:grid md:grid-cols-3 gap-2 overflow-x-auto pb-1 md:overflow-visible snap-x snap-mandatory md:snap-none">
          <li
            v-for="tpl in group.items"
            :key="tpl.id"
            class="snap-start shrink-0 w-[min(78vw,14rem)] md:w-auto md:shrink flex"
          >
            <PromptTemplateCard
              :title="tpl.title"
              :description="tpl.description"
              :fields="[]"
              :preview-url="resolveDeckPreviewUrl(tpl.preview_url)"
              :show-preview="true"
              :selected="selectedId === tpl.id"
              @select="openPreview(tpl)"
            />
          </li>
        </ul>
      </div>
    </template>

    <VisualTemplatePreviewModal
      :open="previewOpen"
      :template="previewTpl"
      mode="visual"
      :resolve-preview-url="resolveDeckPreviewUrl"
      @confirm="confirmPreview"
      @cancel="closePreview"
    />
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import PromptTemplateCard from './PromptTemplateCard.vue'
import VisualTemplatePreviewModal from './VisualTemplatePreviewModal.vue'
import ResumeIndustryChips from '../resume/ResumeIndustryChips.vue'
import { resolveDeckPreviewUrl } from '../../utils/deckPreviewUrl.js'

const props = defineProps({
  templates: { type: Array, default: () => [] },
  selectedId: { type: String, default: '' },
  heading: { type: String, default: '选择 PPT 模板' },
  loading: { type: Boolean, default: false },
  loadError: { type: String, default: '' },
})

const emit = defineEmits(['select', 'retry'])

const previewOpen = ref(false)
const previewTpl = ref(null)
const selectedCategory = ref('deck')

const categoryChips = [
  { id: 'deck', label: '品牌模板' },
  { id: 'layout', label: '结构模板' },
  { id: 'imported', label: '我的导入' },
  { id: 'all', label: '全部' },
]

const filteredTemplates = computed(() => {
  const items = props.templates
  if (selectedCategory.value === 'all') return items
  if (selectedCategory.value === 'layout') {
    return items.filter((t) => t.kind === 'layout')
  }
  if (selectedCategory.value === 'deck') {
    return items.filter((t) => t.kind === 'deck' && !t.imported)
  }
  if (selectedCategory.value === 'imported') {
    return items.filter((t) => t.imported)
  }
  return items
})

const emptyMessage = computed(() => {
  if (selectedCategory.value === 'imported') {
    return '暂无导入模板，可使用上方「导入 PPT 模板」'
  }
  if (selectedCategory.value === 'layout') return '暂无结构模板'
  if (selectedCategory.value === 'deck') return '暂无品牌模板'
  return '暂无 PPT 模板'
})

const displayGroups = computed(() => {
  if (selectedCategory.value !== 'all') {
    return [{ key: selectedCategory.value, label: '', items: filteredTemplates.value }]
  }

  const layouts = props.templates.filter((t) => t.kind === 'layout')
  const decks = props.templates.filter((t) => t.kind === 'deck' && !t.imported)
  const imported = props.templates.filter((t) => t.imported)
  const groups = []
  if (decks.length) groups.push({ key: 'deck', label: '品牌模板', items: decks })
  if (layouts.length) groups.push({ key: 'layout', label: '结构模板', items: layouts })
  if (imported.length) groups.push({ key: 'imported', label: '我的导入', items: imported })
  if (!groups.length && filteredTemplates.value.length) {
    groups.push({ key: 'all', label: '', items: filteredTemplates.value })
  }
  return groups
})

function openPreview(tpl) {
  previewTpl.value = tpl
  previewOpen.value = true
}

function closePreview() {
  previewOpen.value = false
  previewTpl.value = null
}

function confirmPreview() {
  if (previewTpl.value) {
    emit('select', previewTpl.value)
  }
  closePreview()
}
</script>
