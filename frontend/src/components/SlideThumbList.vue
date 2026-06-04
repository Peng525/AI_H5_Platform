<template>
  <div class="flex flex-col" :class="compact ? 'p-2 gap-1' : 'p-3 gap-2'">
    <div class="flex items-center justify-between mb-1">
      <span class="text-xs font-semibold text-on-surface-variant">页面列表</span>
      <button class="text-primary hover:bg-primary/10 rounded p-1" title="新增页面" @click="$emit('add')">
        <span class="material-symbols-outlined text-[16px]">add</span>
      </button>
    </div>

    <div
      v-for="(s, i) in slides"
      :key="s.id"
      class="group relative rounded-md border overflow-hidden cursor-pointer transition-all duration-200 ease-out bg-white"
      :class="thumbSectionClass(s.id)"
      @click="$emit('select', s)"
    >
      <SlideCanvasThumb
        :slide="s"
        :slide-index="i"
        :project-id="projectId"
        :viewport="viewport"
        :project-settings="projectSettings"
        :live-slide-id="liveSlideId"
        :live-elements="liveElements"
        :size="compact ? 'compact' : 'default'"
      />
      <div
        class="absolute top-1 left-1 text-[10px] px-1.5 py-0.5 rounded font-bold shadow-sm z-10"
        :class="currentId === s.id ? 'bg-primary text-on-primary' : 'bg-surface-variant text-on-surface-variant'"
      >
        {{ i + 1 }}
      </div>
      <div
        v-if="!compact"
        class="p-1.5 text-center border-t border-outline-variant text-xs truncate"
        :class="currentId === s.id ? 'text-primary font-medium' : 'text-on-surface-variant'"
      >
        页面{{ i + 1 }}
      </div>
      <button
        v-if="slides.length > 1"
        class="absolute top-1 right-1 z-10 opacity-0 group-hover:opacity-100 p-0.5 bg-red-50 text-red-600 rounded"
        title="删除页面"
        @click.stop="$emit('remove', s.id)"
      >
        <span class="material-symbols-outlined text-[14px]">close</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import SlideCanvasThumb from './SlideCanvasThumb.vue'

const props = defineProps({
  slides: { type: Array, default: () => [] },
  currentId: { type: Number, default: null },
  projectId: { type: [Number, String], default: null },
  viewport: { type: Object, default: null },
  projectSettings: { type: Object, default: null },
  liveSlideId: { type: Number, default: null },
  liveElements: { type: Array, default: null },
  compact: { type: Boolean, default: false },
})

defineEmits(['select', 'add', 'remove'])

function thumbSectionClass(slideId) {
  const selected = props.currentId === slideId
  if (selected) {
    return 'border-black shadow-[0_6px_16px_rgba(0,0,0,0.14)] -translate-y-0.5 z-[1]'
  }
  return 'border-black/30 hover:border-black/50 hover:shadow-[0_4px_10px_rgba(0,0,0,0.08)] hover:-translate-y-px'
}
</script>
