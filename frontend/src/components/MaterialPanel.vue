<template>
  <div class="p-3 flex flex-col gap-3 min-h-0">
    <!-- 页面画布背景色 -->
    <div>
      <p class="text-[11px] font-semibold text-on-surface-variant mb-1.5">页面背景色</p>
      <div class="flex flex-wrap gap-1">
        <button
          v-for="c in quickColors"
          :key="c"
          type="button"
          class="w-5 h-5 rounded-sm border border-black/10 shrink-0 hover:scale-110 transition-transform"
          :class="[c === '#FFFFFF' ? 'ring-1 ring-inset ring-gray-300' : '', canvasBackground === c ? 'ring-2 ring-primary ring-offset-1' : '']"
          :style="{ background: c }"
          :title="c"
          @click="pickCanvasBg(c)"
        />
        <input
          :value="canvasBackground"
          type="color"
          class="w-5 h-5 border-0 cursor-pointer p-0 shrink-0"
          title="自定义页面背景"
          @input="pickCanvasBg($event.target.value)"
        />
      </div>
    </div>

    <p class="text-[11px] font-semibold text-on-surface-variant">点击添加到画布</p>

    <div class="material-grid">
      <button
        v-for="item in presets"
        :key="item.id"
        type="button"
        class="material-card group"
        @click="$emit('add', item)"
      >
        <div class="material-preview">
          <span
            v-if="item.kind === 'text'"
            class="text-[10px] text-on-surface-variant px-1 border border-dashed border-outline-variant rounded w-full text-center py-1 bg-white"
          >
            Aa
          </span>
          <span
            v-else-if="item.kind === 'rect'"
            class="w-9 h-7 rounded-sm border border-black/10 bg-primary"
          />
          <div
            v-else-if="item.kind === 'table'"
            class="w-10 h-8 grid grid-cols-3 grid-rows-2 gap-px bg-outline-variant p-px rounded-sm overflow-hidden"
          >
            <span v-for="n in 6" :key="n" class="bg-white" :class="n <= 3 ? 'bg-primary' : ''" />
          </div>
          <span
            v-else-if="item.kind === 'icon'"
            class="material-symbols-outlined text-2xl text-primary"
          >{{ item.icon }}</span>
          <span
            v-else-if="item.kind === 'image'"
            class="material-symbols-outlined text-2xl text-primary"
          >image</span>
          <div v-else-if="item.kind === 'chart'" class="flex items-end gap-0.5 h-8 px-1">
            <span
              v-for="(h, i) in chartPreviewBars"
              :key="i"
              class="w-1.5 rounded-t-sm bg-primary"
              :style="{ height: h + 'px' }"
            />
          </div>
        </div>
        <span class="material-label">{{ item.label }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { THEME_COLORS } from '../constants/textFormats'

defineProps({
  canvasBackground: { type: String, default: '#005daa' },
})

const emit = defineEmits(['add', 'canvas-bg-change'])

const quickColors = ['#005daa', '#4472C4', '#70AD47', '#ED7D31', '#FFC000', '#FFFFFF', '#44546A', '#C00000', ...THEME_COLORS.filter((c, i, a) => a.indexOf(c) === i)].slice(0, 12)

const chartPreviewBars = [10, 18, 12, 22]

const presets = [
  { id: 'textbox', kind: 'text', label: '文本框', type: 'text' },
  { id: 'rect', kind: 'rect', label: '矩形', type: 'shape' },
  { id: 'table', kind: 'table', label: '表格', type: 'table' },
  { id: 'icon', kind: 'icon', label: '图标', type: 'icon', icon: 'emoji_objects' },
  { id: 'image', kind: 'image', label: '图片', type: 'image' },
  { id: 'chart', kind: 'chart', label: '图表', type: 'chart' },
]

function pickCanvasBg(color) {
  emit('canvas-bg-change', color)
}
</script>

<style scoped>
.material-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

@media (max-width: 220px) {
  .material-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.material-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 4px;
  border-radius: 8px;
  border: 1px solid var(--outline-variant, #c0c7d6);
  background: white;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.material-card:hover {
  border-color: #005daa;
  box-shadow: 0 2px 8px rgba(0, 93, 170, 0.12);
}

.material-preview {
  width: 100%;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f6f3f2;
  border-radius: 6px;
}

.material-label {
  font-size: 10px;
  color: #404753;
  text-align: center;
  line-height: 1.2;
}

.group:hover .material-label {
  color: #005daa;
}
</style>
