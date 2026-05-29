<template>
  <div class="chat-script-editor space-y-3 text-sm">
    <div class="flex items-center justify-between">
      <h3 class="text-xs font-semibold text-on-surface flex items-center gap-1">
        <span class="material-symbols-outlined text-[16px]">forum</span>
        微信对话脚本
      </h3>
      <label class="flex items-center gap-1.5 text-xs font-medium text-on-surface cursor-pointer">
        <input v-model="enabled" type="checkbox" class="rounded" @change="emitSave" />
        启用
      </label>
    </div>

    <p class="text-xs text-on-surface/75 leading-relaxed">
      预览/分享时以气泡逐句弹出。使用全屏对话生成器编辑样式、参与者与时间戳。
    </p>

    <div v-if="enabled" class="space-y-2">
      <div class="text-xs text-on-surface bg-white border border-outline-variant rounded-lg p-2.5 leading-relaxed">
        <p>{{ summary }}</p>
      </div>
      <button
        type="button"
        class="w-full py-2 text-xs bg-primary text-on-primary rounded-lg font-medium"
        @click="$emit('open-generator')"
      >
        打开对话生成器
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { normalizeChatScript, serializeChatScript } from '../utils/chatScript.js'

const props = defineProps({
  slide: { type: Object, default: null },
})

const emit = defineEmits(['save', 'open-generator'])

const enabled = ref(false)
const scriptState = ref(null)

function loadFromSlide(slide) {
  const script = slide?.chat_script || {}
  const n = normalizeChatScript(script)
  enabled.value = !!script.enabled
  scriptState.value = n
}

const summary = computed(() => {
  const n = scriptState.value
  if (!n) return '暂无对话'
  const msgs = n.timeline.filter((t) => t.type === 'message').length
  const ts = n.timeline.filter((t) => t.type === 'timestamp').length
  return `${n.participants.length} 位参与者 · ${msgs} 条消息 · ${ts} 个时间戳`
})

function emitSave() {
  const base = scriptState.value || normalizeChatScript({})
  emit('save', {
    chat_script: serializeChatScript({ ...base, enabled: enabled.value }),
  })
}

watch(
  () => props.slide?.id,
  () => loadFromSlide(props.slide),
  { immediate: true }
)

watch(
  () => props.slide?.chat_script,
  () => loadFromSlide(props.slide),
  { deep: true }
)
</script>

<style scoped>
.chat-script-editor {
  -webkit-font-smoothing: auto;
  -moz-osx-font-smoothing: auto;
}
</style>
