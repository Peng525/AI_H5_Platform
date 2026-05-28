<template>
  <div class="space-y-4 text-sm">
    <div class="flex items-center justify-between">
      <h3 class="text-xs font-semibold text-on-surface-variant flex items-center gap-1">
        <span class="material-symbols-outlined text-[16px]">forum</span>
        微信对话脚本
      </h3>
      <label class="flex items-center gap-1.5 text-xs cursor-pointer">
        <input v-model="enabled" type="checkbox" class="rounded" @change="emitSave" />
        启用
      </label>
    </div>

    <p class="text-[11px] text-on-surface-variant">
      预览/分享时以微信气泡逐句弹出；观众点击屏幕显示下一条。
    </p>

    <div v-if="enabled" class="space-y-3">
      <div
        v-for="(msg, i) in messages"
        :key="msg.id || i"
        class="border border-outline-variant rounded-lg p-2 space-y-2 bg-white"
      >
        <div class="flex items-center justify-between gap-2">
          <span class="text-[10px] text-on-surface-variant">消息 {{ i + 1 }}</span>
          <button type="button" class="text-[10px] text-red-600" @click="removeMessage(i)">删除</button>
        </div>
        <div class="flex gap-2">
          <select v-model="msg.side" class="text-xs border rounded px-2 py-1" @change="emitSave">
            <option value="left">左侧（对方）</option>
            <option value="right">右侧（我）</option>
          </select>
          <input
            v-model="msg.name"
            class="flex-1 text-xs border rounded px-2 py-1"
            placeholder="昵称"
            @change="emitSave"
          />
        </div>
        <textarea
          v-model="msg.text"
          rows="2"
          class="w-full text-xs border rounded px-2 py-1 resize-none"
          placeholder="对话内容"
          @change="emitSave"
        />
      </div>

      <button
        type="button"
        class="w-full py-2 text-xs border border-dashed border-outline-variant rounded-lg hover:bg-white"
        @click="addMessage"
      >
        + 添加一条消息
      </button>

      <label class="block text-[11px] text-on-surface-variant">
        自动逐句间隔（毫秒，0 = 仅点击）
        <input
          v-model.number="autoAdvanceMs"
          type="number"
          min="0"
          step="500"
          class="mt-1 w-full border rounded px-2 py-1 text-xs"
          @change="emitSave"
        />
      </label>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  slide: { type: Object, default: null },
})

const emit = defineEmits(['save'])

const enabled = ref(false)
const autoAdvanceMs = ref(0)
const messages = ref([])

function genId() {
  return `m_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`
}

function loadFromSlide(slide) {
  const script = slide?.chat_script || {}
  enabled.value = !!script.enabled
  autoAdvanceMs.value = Number(script.autoAdvanceMs || 0)
  messages.value = Array.isArray(script.messages)
    ? script.messages.map((m) => ({ ...m, id: m.id || genId() }))
    : []
}

function payload() {
  return {
    chat_script: {
      enabled: enabled.value,
      autoAdvanceMs: autoAdvanceMs.value,
      messages: messages.value.map((m) => ({
        id: m.id || genId(),
        side: m.side === 'right' ? 'right' : 'left',
        avatar: m.avatar || '',
        name: m.name || '',
        text: m.text || '',
      })),
    },
  }
}

function emitSave() {
  emit('save', payload())
}

function addMessage() {
  messages.value.push({
    id: genId(),
    side: messages.value.length % 2 === 0 ? 'left' : 'right',
    avatar: '',
    name: messages.value.length % 2 === 0 ? '小助手' : '我',
    text: '',
  })
  emitSave()
}

function removeMessage(i) {
  messages.value.splice(i, 1)
  emitSave()
}

watch(
  () => props.slide?.id,
  () => loadFromSlide(props.slide),
  { immediate: true }
)
</script>
