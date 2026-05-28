<template>
  <div class="absolute top-4 left-1/2 -translate-x-1/2 flex items-center gap-1 bg-white shadow-card rounded-lg px-2 py-1 border border-outline-variant z-20 flex-wrap max-w-[90%]">
    <div class="relative group">
      <button class="p-2 hover:bg-surface-container rounded flex items-center gap-1 text-primary font-medium text-xs">
        <span class="material-symbols-outlined text-[18px]">add_circle</span>
        添加
      </button>
      <div class="hidden group-hover:block absolute top-full left-0 mt-1 w-44 bg-white border border-outline-variant rounded-lg shadow-lg py-1 z-50">
        <button class="w-full text-left px-3 py-2 text-sm hover:bg-surface-container-low flex items-center gap-2" @click="$emit('add-text')">
          <span class="material-symbols-outlined text-[16px] text-primary">text_fields</span>
          文本框
        </button>
        <button class="w-full text-left px-3 py-2 text-sm hover:bg-surface-container-low flex items-center gap-2" @click="$emit('add-shape')">
          <span class="material-symbols-outlined text-[16px] text-secondary">category</span>
          形状
        </button>
      </div>
    </div>

    <div class="w-px h-5 bg-outline-variant" />

    <template v-if="selected">
      <label class="flex items-center gap-1 text-xs px-1">
        <span class="material-symbols-outlined text-[16px] text-on-surface-variant">palette</span>
        <input type="color" :value="selected.style?.background || '#005daa'" class="w-6 h-6 border-0 cursor-pointer" @input="onColor('background', $event.target.value)" />
      </label>
      <label class="flex items-center gap-1 text-xs px-1">
        <span class="material-symbols-outlined text-[16px] text-on-surface-variant">text_format</span>
        <select
          :value="selected.style?.fontSize || 16"
          class="text-xs border rounded px-1 py-0.5"
          @change="onColor('fontSize', Number($event.target.value))"
        >
          <option v-for="s in [12, 14, 16, 18, 22, 28]" :key="s" :value="s">{{ s }}px</option>
        </select>
      </label>
      <button class="p-1.5 hover:bg-surface-container rounded text-on-surface-variant" title="复制" @click="$emit('duplicate')">
        <span class="material-symbols-outlined text-[18px]">content_copy</span>
      </button>
      <button class="p-1.5 hover:bg-surface-container rounded text-on-surface-variant" title="置顶" @click="$emit('bring-front')">
        <span class="material-symbols-outlined text-[18px]">vertical_align_top</span>
      </button>
      <button class="p-1.5 hover:bg-red-50 rounded text-red-600" title="删除" @click="$emit('delete')">
        <span class="material-symbols-outlined text-[18px]">delete</span>
      </button>
    </template>
  </div>
</template>

<script setup>
defineProps({
  selected: { type: Object, default: null },
})

const emit = defineEmits(['add-text', 'add-shape', 'add-image', 'style-change', 'duplicate', 'delete', 'bring-front'])

function onColor(key, value) {
  emit('style-change', { [key]: value })
}
</script>
