<template>
  <section class="flex-1 bg-surface-container-low flex items-center justify-center overflow-hidden relative">
    <EditorCanvasToolbar
      :selected="selectedElement"
      @add-text="$emit('add-text')"
      @add-shape="$emit('add-shape')"
      @add-image="$emit('add-image', $event)"
      @style-change="$emit('style-change', $event)"
      @duplicate="$emit('duplicate')"
      @delete="$emit('delete-selected')"
      @bring-front="$emit('bring-front')"
    />

    <div class="absolute bottom-6 flex items-center gap-1 bg-white shadow-card rounded-full px-2 py-1 border border-outline-variant z-20">
      <button class="p-1.5 hover:bg-surface-container rounded-full" @click="zoomOut">
        <span class="material-symbols-outlined text-[18px]">remove</span>
      </button>
      <span class="text-xs w-10 text-center">{{ Math.round(scale * 100) }}%</span>
      <button class="p-1.5 hover:bg-surface-container rounded-full" @click="zoomIn">
        <span class="material-symbols-outlined text-[18px]">add</span>
      </button>
    </div>

    <div
      class="relative transition-transform origin-center"
      :style="{ transform: `scale(${scale})` }"
      @mousedown.self="$emit('deselect')"
    >
      <div
        class="w-[375px] h-[812px] bg-white shadow-2xl rounded-[2rem] overflow-hidden border-[8px] border-gray-900 flex flex-col"
      >
        <div class="h-7 w-full flex justify-between items-center px-4 pt-1 shrink-0 bg-white">
          <span class="text-[12px] font-medium">9:41</span>
          <div class="flex gap-1 items-center opacity-80">
            <span class="material-symbols-outlined text-[14px]">signal_cellular_alt</span>
            <span class="material-symbols-outlined text-[14px]">wifi</span>
            <span class="material-symbols-outlined text-[14px]">battery_full</span>
          </div>
        </div>

        <div
          ref="canvasRef"
          class="flex-1 relative overflow-hidden"
          :class="slideBgClass"
          @mousedown.self="$emit('deselect')"
        >
          <CanvasElement
            v-for="el in elements"
            :key="el.id"
            :element="el"
            :selected="el.id === selectedId"
            :scale="scale"
            @select="$emit('select', $event)"
            @update="(id, patch) => $emit('update-element', id, patch)"
          />

          <div
            v-if="!elements.length && slide"
            class="absolute inset-0 p-6 text-white pointer-events-none"
          >
            <span class="text-xs opacity-80">第 {{ slideIndex + 1 }} 页</span>
            <h2 class="text-xl font-bold mt-2">{{ slide.title }}</h2>
            <p v-if="slide.subtitle" class="text-sm mt-2 opacity-90">{{ slide.subtitle }}</p>
            <ul v-if="slide.bullets?.length" class="mt-4 space-y-2 text-sm">
              <li v-for="(b, j) in slide.bullets" :key="j">• {{ b }}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import CanvasElement from './CanvasElement.vue'
import EditorCanvasToolbar from './EditorCanvasToolbar.vue'

const props = defineProps({
  elements: { type: Array, default: () => [] },
  selectedId: { type: String, default: null },
  slide: { type: Object, default: null },
  slideIndex: { type: Number, default: 0 },
})

defineEmits([
  'select',
  'deselect',
  'update-element',
  'add-text',
  'add-shape',
  'add-image',
  'style-change',
  'duplicate',
  'delete-selected',
  'bring-front',
])

const scale = ref(0.9)
const canvasRef = ref(null)

const selectedElement = computed(() => props.elements.find((el) => el.id === props.selectedId) || null)

const slideBgClass = computed(() =>
  props.elements.length
    ? 'bg-[#f3f3f3]'
    : 'bg-gradient-to-br from-primary to-primary-container'
)

function zoomIn() {
  scale.value = Math.min(1.2, scale.value + 0.1)
}
function zoomOut() {
  scale.value = Math.max(0.5, scale.value - 0.1)
}
</script>
