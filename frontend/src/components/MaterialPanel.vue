<template>
  <div class="p-3">
    <p class="text-xs font-semibold text-on-surface-variant mb-3">点击添加到画布</p>
    <div class="grid grid-cols-2 gap-2">
      <button
        v-for="item in presets"
        :key="item.id"
        class="flex flex-col items-center gap-1 p-3 rounded-lg border border-outline-variant hover:border-primary hover:bg-white transition text-xs"
        @click="$emit('add', item)"
      >
        <span
          v-if="item.type === 'shape'"
          class="w-10 h-10 rounded-lg"
          :style="{ background: item.color }"
        />
        <span v-else-if="item.type === 'image'" class="material-symbols-outlined text-3xl text-primary">{{ item.icon }}</span>
        <span v-else class="material-symbols-outlined text-3xl text-on-surface-variant">{{ item.icon }}</span>
        {{ item.label }}
      </button>
    </div>
  </div>
</template>

<script setup>
defineEmits(['add'])

const presets = [
  { id: 'blue', type: 'shape', label: '蓝色块', color: '#005daa', borderRadius: 8 },
  { id: 'green', type: 'shape', label: '绿色块', color: '#006d33', borderRadius: 8 },
  { id: 'circle', type: 'shape', label: '圆形', color: '#0075d5', borderRadius: 999 },
  { id: 'wechat', type: 'shape', label: '微信绿', color: '#95ec69', borderRadius: 12 },
  { id: 'chart', type: 'image', label: '图表占位', icon: 'bar_chart', content: 'https://placehold.co/200x120/005daa/white?text=Chart' },
  { id: 'photo', type: 'image', label: '图片占位', icon: 'image', content: 'https://placehold.co/200x120/f0eded/404753?text=Image' },
  { id: 'icon-ai', type: 'image', label: 'AI 图标', icon: 'smart_toy', content: 'https://placehold.co/80x80/005daa/white?text=AI' },
  { id: 'icon-star', type: 'image', label: '星标', icon: 'star', content: 'https://placehold.co/80x80/ffc107/white?text=★' },
]
</script>
