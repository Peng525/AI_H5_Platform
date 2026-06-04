<template>
  <component :is="templateComponent" v-if="structured" :structured="structured" class="w-full h-full" />
</template>

<script setup>
import { computed } from 'vue'
import { getSlideTemplateComponent } from './registry.js'
import { resolveSlideStructured } from '../utils/compileStructuredSlide.js'

const props = defineProps({
  slide: { type: Object, default: null },
  structured: { type: Object, default: null },
})

const structured = computed(() => props.structured || resolveSlideStructured(props.slide))
const templateComponent = computed(() => getSlideTemplateComponent(structured.value?.template))
</script>
