<template>
  <Teleport to="body">
    <div
      v-if="selected && anchorRect"
      data-editor-chrome
      class="inline-flex flex-nowrap items-center gap-1 overflow-x-auto bg-[#1e293b] shadow-lg rounded-lg px-2 py-1.5 border border-slate-600 pointer-events-auto w-max max-w-[calc(100vw-16px)]"
      :style="barStyle"
      @mousedown.stop
    >
      <TextFormatControls
        :selected="selected"
        theme-id="zjy-minimal"
        viewport-id="resume-a4"
        slide-id="resume"
        @style-change="$emit('style-change', $event)"
      />
    </div>
  </Teleport>
</template>

<script setup>
import { computed, toRef, watch } from 'vue'
import TextFormatControls from '../create/TextFormatControls.vue'
import { floatingBarStyle, useElementAnchor } from '../../composables/useElementAnchor.js'

const props = defineProps({
  selected: { type: Object, default: null },
  resolveElementEl: { type: Function, default: null },
  scrollRootRef: { type: Object, default: null },
})

defineEmits(['style-change'])

const bindId = computed(() => props.selected?.id || '')

const { anchorRect, refresh } = useElementAnchor({
  elementId: bindId,
  slideId: 'resume',
  resolveElementEl: props.resolveElementEl,
  enabled: computed(() => !!bindId.value),
  scrollRootRef: toRef(props, 'scrollRootRef'),
})

watch(bindId, () => refresh())

const barStyle = computed(() =>
  floatingBarStyle(anchorRect.value, 'above', 8, { compact: true, barHeight: 44 }),
)
</script>
