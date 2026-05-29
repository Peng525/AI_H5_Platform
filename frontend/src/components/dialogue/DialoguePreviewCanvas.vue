<template>
  <div
    ref="rootRef"
    class="dialogue-preview flex flex-col h-full min-h-0 overflow-hidden"
    :style="dialogueBackgroundStyle(script.style)"
  >
    <div class="flex-1 overflow-y-auto px-3 py-4 space-y-3 min-h-0">
      <template v-for="(item, i) in renderItems" :key="item.id || i">
        <div
          v-if="item.type === 'timestamp'"
          class="text-center text-xs py-1"
          :style="timestampStyle(script.style)"
        >
          {{ item.text }}
        </div>

        <div
          v-else
          class="relative group"
          :class="editable ? 'cursor-pointer' : ''"
          @click.stop="editable && selectIndex(i)"
        >
          <div
            v-if="editable && selectedIndex === i"
            class="absolute -inset-1 border-2 border-primary rounded-lg pointer-events-none z-10"
          />
          <div
            v-if="editable && selectedIndex === i"
            class="absolute -top-3 left-1/2 -translate-x-1/2 z-20"
          >
            <button
              type="button"
              class="w-6 h-6 rounded-full bg-primary text-white text-sm shadow flex items-center justify-center"
              title="在上方插入"
              @click.stop="insertAt(i, 'above')"
            >
              +
            </button>
          </div>
          <div
            v-if="editable && selectedIndex === i"
            class="absolute -bottom-3 left-1/2 -translate-x-1/2 z-20"
          >
            <button
              type="button"
              class="w-6 h-6 rounded-full bg-primary text-white text-sm shadow flex items-center justify-center"
              title="在下方插入"
              @click.stop="insertAt(i, 'below')"
            >
              +
            </button>
          </div>
          <div
            v-if="editable && selectedIndex === i"
            class="absolute -top-2 -right-2 z-20"
          >
            <button
              type="button"
              class="w-5 h-5 rounded-full bg-red-500 text-white text-xs shadow"
              title="删除"
              @click.stop="removeAt(i)"
            >
              ×
            </button>
          </div>

          <div
            class="flex gap-2 items-start"
            :class="item.side === 'right' ? 'flex-row-reverse' : 'flex-row'"
          >
            <div
              class="shrink-0 w-10 h-10 overflow-hidden bg-gray-200 flex items-center justify-center text-sm font-semibold text-gray-600"
              :style="avatarInlineStyle(script.style)"
            >
              <img
                v-if="item.avatar"
                :src="item.avatar"
                alt=""
                class="w-full h-full object-cover"
                @error="($event.target.style.display = 'none')"
              />
              <span v-else>{{ avatarInitial(item.name, item.side) }}</span>
            </div>
            <div class="max-w-[72%] min-w-0">
              <p
                v-if="item.name"
                class="text-[11px] mb-0.5 opacity-70"
                :class="item.side === 'right' ? 'text-right' : 'text-left'"
              >
                {{ item.name }}
              </p>
              <div
                v-if="editable && selectedIndex === i"
                class="relative px-3 py-2 text-[15px] leading-relaxed shadow-sm"
                :style="bubbleInlineStyle(item.isOwner, script.style)"
                @click.stop
              >
                <textarea
                  :value="item.text"
                  rows="2"
                  class="w-full bg-transparent outline-none resize-none text-inherit"
                  @input="updateText(i, $event.target.value)"
                />
              </div>
              <div
                v-else
                class="px-3 py-2.5 text-[15px] leading-relaxed break-words shadow-sm"
                :style="bubbleInlineStyle(item.isOwner, script.style)"
              >
                {{ item.text || (editable ? '点击编辑…' : '') }}
              </div>
            </div>
          </div>
        </div>
      </template>

      <div v-if="editable && !renderItems.length" class="text-center text-sm opacity-50 py-8">
        点击下方 + 添加对话或时间
      </div>
    </div>

    <div
      v-if="editable"
      class="shrink-0 border-t border-black/10 p-3 bg-white/80 backdrop-blur relative"
    >
      <div class="flex flex-wrap gap-2 justify-center">
        <button
          v-for="p in script.participants"
          :key="p.id"
          type="button"
          class="px-2 py-1 text-xs border border-outline-variant rounded-full hover:bg-surface-container-low"
          @click="addMessage(p.id)"
        >
          + {{ p.name }}
        </button>
        <button
          type="button"
          class="px-2 py-1 text-xs border border-dashed border-primary text-primary rounded-full"
          @click="addParticipant"
        >
          + 新用户
        </button>
        <button
          type="button"
          class="px-2 py-1 text-xs border border-outline-variant rounded-full"
          @click="addTimestamp"
        >
          + 时间
        </button>
      </div>

      <div
        v-if="insertMenuOpen"
        class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 bg-white border border-outline-variant rounded-lg shadow-lg p-2 min-w-[160px] z-30"
        @click.stop
      >
        <p class="text-[10px] text-on-surface-variant px-2 pb-1">插入内容</p>
        <button
          v-for="p in script.participants"
          :key="'ins-' + p.id"
          type="button"
          class="block w-full text-left px-2 py-1.5 text-xs hover:bg-surface-container-low rounded"
          @click="confirmInsertMessage(p.id)"
        >
          {{ p.name }}
        </button>
        <button
          type="button"
          class="block w-full text-left px-2 py-1.5 text-xs hover:bg-surface-container-low rounded"
          @click="confirmInsertTimestamp"
        >
          时间戳
        </button>
        <button
          type="button"
          class="block w-full text-left px-2 py-1.5 text-xs text-on-surface-variant"
          @click="insertMenuOpen = false"
        >
          取消
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import {
  avatarInlineStyle,
  avatarInitial,
  bubbleInlineStyle,
  buildRenderableTimeline,
  dialogueBackgroundStyle,
  timestampStyle,
} from '../../utils/dialogueRender.js'
import { genChatId, normalizeChatScript } from '../../utils/chatScript.js'

const props = defineProps({
  modelValue: { type: Object, required: true },
  editable: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

const rootRef = ref(null)
const selectedIndex = ref(-1)
const insertMenuOpen = ref(false)
const insertAtIndex = ref(-1)

const script = computed(() => normalizeChatScript(props.modelValue))
const renderItems = computed(() => buildRenderableTimeline(script.value))

function emitScript(patch) {
  emit('update:modelValue', { ...script.value, ...patch })
}

function selectIndex(i) {
  selectedIndex.value = i
}

function updateText(i, text) {
  const timeline = script.value.timeline.map((t, idx) => (idx === i ? { ...t, text } : t))
  emitScript({ timeline })
}

function removeAt(i) {
  const timeline = script.value.timeline.filter((_, idx) => idx !== i)
  selectedIndex.value = -1
  emitScript({ timeline })
}

function insertAt(i, where) {
  insertAtIndex.value = where === 'above' ? i : i + 1
  insertMenuOpen.value = true
}

function confirmInsertMessage(participantId) {
  const p = script.value.participants.find((x) => x.id === participantId)
  const side = p?.defaultSide || 'left'
  const item = {
    id: genChatId('m'),
    type: 'message',
    participantId,
    side,
    text: '',
  }
  const timeline = [...script.value.timeline]
  const at = insertAtIndex.value >= 0 ? insertAtIndex.value : timeline.length
  timeline.splice(at, 0, item)
  insertMenuOpen.value = false
  selectedIndex.value = at
  emitScript({ timeline })
}

function confirmInsertTimestamp() {
  const item = { id: genChatId('ts'), type: 'timestamp', text: '15:30' }
  const timeline = [...script.value.timeline]
  const at = insertAtIndex.value >= 0 ? insertAtIndex.value : timeline.length
  timeline.splice(at, 0, item)
  insertMenuOpen.value = false
  selectedIndex.value = at
  emitScript({ timeline })
}

function addMessage(participantId) {
  insertAtIndex.value = script.value.timeline.length
  confirmInsertMessage(participantId)
}

function addTimestamp() {
  insertAtIndex.value = script.value.timeline.length
  confirmInsertTimestamp()
}

function addParticipant() {
  const n = script.value.participants.length
  const id = genChatId('p')
  const participants = [
    ...script.value.participants,
    {
      id,
      name: `用户${String.fromCharCode(65 + n)}`,
      avatar: '',
      role: 'guest',
      defaultSide: 'left',
    },
  ]
  emitScript({ participants })
}

defineExpose({ rootRef })
</script>

<style scoped>
.dialogue-preview {
  -webkit-overflow-scrolling: touch;
}
</style>
