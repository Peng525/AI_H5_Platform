<template>
  <Teleport to="body">
    <ElementQuickToolbar
      v-if="showQuickBar"
      :selected="selectedElement"
      :anchor-rect="anchorRect"
      :viewport="viewport"
      @image-fit="$emit('image-fit', $event)"
      @image-crop="$emit('image-crop')"
      @image-layout="$emit('image-layout', $event)"
      @duplicate="$emit('duplicate')"
      @bring-front="$emit('bring-front')"
      @send-back="$emit('send-back')"
      @delete-selected="$emit('delete-selected')"
      @edit-chart-stack="$emit('edit-chart-stack')"
    />
    <TextFormatToolbar
      v-if="showTextBar"
      :selected="selectedElement"
      :visible="textEditing"
      :anchor-rect="anchorRect"
      :theme-id="themeId"
      :viewport-id="viewportId"
      :slide-id="slideId"
      @style-change="$emit('style-change', $event)"
    />
  </Teleport>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useElementAnchor } from '../../composables/useElementAnchor.js'
import ElementQuickToolbar from './ElementQuickToolbar.vue'
import TextFormatToolbar from './TextFormatToolbar.vue'

const props = defineProps({
  selectedElement: { type: Object, default: null },
  slideId: { type: [Number, String], default: null },
  textEditing: { type: Boolean, default: false },
  themeId: { type: String, default: 'zjy-minimal' },
  viewportId: { type: String, default: 'mobile-375' },
  viewport: { type: Object, default: () => ({ width: 375, height: 667 }) },
  resolveElementEl: { type: Function, default: null },
  scrollRootRef: { type: Object, default: null },
  hidden: { type: Boolean, default: false },
})

defineEmits([
  'style-change',
  'image-fit',
  'image-crop',
  'image-layout',
  'duplicate',
  'bring-front',
  'send-back',
  'delete-selected',
  'edit-chart-stack',
])

const elementId = computed(() => props.selectedElement?.id ?? null)

const enabled = computed(() => !props.hidden && !!props.selectedElement && props.slideId != null)

const { anchorRect, refresh } = useElementAnchor({
  elementId,
  slideId: computed(() => props.slideId),
  resolveElementEl: (sid, eid) => props.resolveElementEl?.(sid, eid),
  enabled,
  scrollRootRef: computed(() => props.scrollRootRef),
})

watch(
  () => props.selectedElement,
  () => refresh(),
  { deep: true },
)

const showQuickBar = computed(
  () => enabled.value && props.selectedElement && !props.textEditing,
)
const showTextBar = computed(
  () => enabled.value && props.selectedElement?.type === 'text' && props.textEditing,
)
</script>
