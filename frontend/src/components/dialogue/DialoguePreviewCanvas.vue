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
          <input
            v-if="editable && selectedIndex === i"
            :value="item.text"
            class="bg-transparent text-center outline-none border-b border-primary/40 w-20"
            @click.stop
            @input="updateTimestamp(i, $event.target.value)"
          />
          <span v-else @click.stop="editable && selectIndex(i)">{{ item.text }}</span>
        </div>

        <div
          v-else
          class="message-row relative"
          :class="[
            editable ? 'cursor-pointer' : '',
            editable && selectedIndex === i ? 'message-row--selected' : '',
          ]"
          @click.stop="editable && selectIndex(i)"
        >
          <div
            v-if="editable && selectedIndex === i"
            class="message-row__tools"
          >
            <button
              type="button"
              class="message-row__fab message-row__fab--top"
              title="在上方插入"
              @click.stop="openInsertMenu($event, i, 'above')"
            >
              +
            </button>
            <button
              type="button"
              class="message-row__fab message-row__fab--bottom"
              title="在下方插入"
              @click.stop="openInsertMenu($event, i, 'below')"
            >
              +
            </button>
            <button
              type="button"
              class="message-row__fab message-row__fab--delete"
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
            <div class="max-w-[78%] min-w-0" :class="item.side === 'right' ? 'items-end' : 'items-start'">
              <p
                v-if="item.name && editable"
                class="text-[11px] mb-0.5 opacity-60 px-1"
                :class="item.side === 'right' ? 'text-right' : 'text-left'"
              >
                {{ item.name }}
              </p>
              <div
                :class="bubbleClass(item.side)"
                :style="bubbleInlineStyle(item.isOwner, script.style)"
              >
                <textarea
                  v-if="editable && selectedIndex === i"
                  :value="item.text"
                  rows="1"
                  class="dialogue-bubble__input"
                  @click.stop
                  @input="updateText(i, $event.target.value)"
                />
                <span v-else class="dialogue-bubble__text">{{ item.text || (editable ? '点击编辑…' : '') }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>

      <div v-if="editable && !renderItems.length" class="text-center py-10 space-y-2">
        <p class="text-sm opacity-50 mb-3">暂无对话内容</p>
        <div class="flex flex-wrap justify-center gap-2">
          <button
            type="button"
            class="px-4 py-2 text-sm border border-outline-variant rounded-full hover:bg-white/80"
            @click="addTimestampAt(0)"
          >
            添加时间戳
          </button>
          <button
            type="button"
            class="px-4 py-2 text-sm bg-primary text-on-primary rounded-full"
            @click="addMessageAt(0)"
          >
            添加消息
          </button>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="insertMenuOpen">
        <div class="fixed inset-0 z-[280]" @click="closeInsertMenu" />
        <div
          class="fixed z-[290] bg-white border border-outline-variant rounded-lg shadow-xl py-1 min-w-[148px]"
          :style="insertMenuStyle"
          @click.stop
        >
          <p class="text-[10px] text-on-surface-variant px-3 py-1">插入</p>
          <button
            type="button"
            class="block w-full text-left px-3 py-2 text-sm hover:bg-surface-container-low"
            @click="confirmAddTimestamp"
          >
            添加时间戳
          </button>
          <button
            type="button"
            class="block w-full text-left px-3 py-2 text-sm hover:bg-surface-container-low"
            @click="confirmAddMessage"
          >
            添加消息
          </button>
          <button
            type="button"
            class="block w-full text-left px-3 py-2 text-sm text-on-surface-variant hover:bg-surface-container-low"
            @click="closeInsertMenu"
          >
            取消
          </button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import {
  avatarInlineStyle,
  avatarInitial,
  bubbleClass,
  bubbleInlineStyle,
  buildRenderableTimeline,
  dialogueBackgroundStyle,
  timestampStyle,
} from '../../utils/dialogueRender.js'
import {
  createParticipantAtIndex,
  genChatId,
  nextTimestampAfterTimeline,
  normalizeChatScript,
  sideForParticipantIndex,
} from '../../utils/chatScript.js'

const props = defineProps({
  modelValue: { type: Object, required: true },
  editable: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'select-index'])

const rootRef = ref(null)
const selectedIndex = ref(-1)
const insertMenuOpen = ref(false)
const insertAtIndex = ref(-1)
const insertMenuPos = ref({ top: 0, left: 0 })

const script = computed(() => normalizeChatScript(props.modelValue))
const renderItems = computed(() => buildRenderableTimeline(script.value))

const insertMenuStyle = computed(() => ({
  top: `${insertMenuPos.value.top}px`,
  left: `${insertMenuPos.value.left}px`,
  transform: 'translateX(-50%)',
}))

function emitScript(patch) {
  emit('update:modelValue', { ...script.value, ...patch })
}

function selectIndex(i) {
  selectedIndex.value = i
  emit('select-index', i)
}

function updateText(i, text) {
  const timeline = script.value.timeline.map((t, idx) => (idx === i ? { ...t, text } : t))
  emitScript({ timeline })
}

function updateTimestamp(i, text) {
  const timeline = script.value.timeline.map((t, idx) => (idx === i ? { ...t, text } : t))
  emitScript({ timeline })
}

function removeAt(i) {
  const timeline = script.value.timeline.filter((_, idx) => idx !== i)
  selectedIndex.value = -1
  emit('select-index', -1)
  emitScript({ timeline })
}

function openInsertMenu(e, i, where) {
  const rect = e.currentTarget.getBoundingClientRect()
  insertAtIndex.value = where === 'above' ? i : i + 1
  insertMenuPos.value = {
    top: rect.bottom + 6,
    left: rect.left + rect.width / 2,
  }
  insertMenuOpen.value = true
}

function closeInsertMenu() {
  insertMenuOpen.value = false
}

function insertIndex() {
  return insertAtIndex.value >= 0 ? insertAtIndex.value : script.value.timeline.length
}

function addTimestampAt(at) {
  const timeline = [...script.value.timeline]
  const insertAt = at >= 0 ? at : timeline.length
  const tsText = nextTimestampAfterTimeline(timeline, insertAt)
  timeline.splice(insertAt, 0, { id: genChatId('ts'), type: 'timestamp', text: tsText })
  selectedIndex.value = insertAt
  emit('select-index', insertAt)
  emitScript({ timeline })
}

function addMessageAt(at) {
  const participants = [...script.value.participants]
  const participant = createParticipantAtIndex(participants.length)
  participants.push(participant)
  const timeline = [...script.value.timeline]
  const insertAt = at >= 0 ? at : timeline.length
  const message = {
    id: genChatId('m'),
    type: 'message',
    participantId: participant.id,
    side: sideForParticipantIndex(participants.length - 1),
    text: '',
  }
  timeline.splice(insertAt, 0, message)
  selectedIndex.value = insertAt
  emit('select-index', insertAt)
  emitScript({ participants, timeline })
}

function confirmAddTimestamp() {
  addTimestampAt(insertIndex())
  closeInsertMenu()
}

function confirmAddMessage() {
  addMessageAt(insertIndex())
  closeInsertMenu()
}

defineExpose({ rootRef, selectedIndex, selectIndex })
</script>

<style scoped>
.dialogue-preview {
  -webkit-overflow-scrolling: touch;
}

.message-row {
  padding: 4px 2px;
  border-radius: 8px;
}

.message-row--selected {
  box-shadow: 0 0 0 2px rgba(0, 93, 170, 0.45);
  background: rgba(0, 93, 170, 0.04);
}

.message-row__tools {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 5;
}

.message-row__fab {
  pointer-events: auto;
  position: absolute;
  width: 24px;
  height: 24px;
  border-radius: 999px;
  background: #005daa;
  color: #fff;
  font-size: 16px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.18);
}

.message-row__fab--top {
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
}

.message-row__fab--bottom {
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
}

.message-row__fab--delete {
  top: -4px;
  right: -4px;
  width: 20px;
  height: 20px;
  font-size: 14px;
  background: #dc2626;
}

:deep(.dialogue-bubble) {
  position: relative;
  display: inline-block;
  max-width: 100%;
  padding: 9px 13px;
  font-size: 15px;
  line-height: 1.45;
  word-break: break-word;
  box-shadow: 0 1px 1px rgba(0, 0, 0, 0.06);
}

:deep(.dialogue-bubble--right) {
  border-radius: 18px 6px 18px 18px;
}

:deep(.dialogue-bubble--right::after) {
  content: '';
  position: absolute;
  right: -5px;
  top: 12px;
  border: 5px solid transparent;
  border-left-color: var(--bubble-bg, #95ec69);
}

:deep(.dialogue-bubble--left) {
  border-radius: 6px 18px 18px 18px;
}

:deep(.dialogue-bubble--left::after) {
  content: '';
  position: absolute;
  left: -5px;
  top: 12px;
  border: 5px solid transparent;
  border-right-color: var(--bubble-bg, #fff);
}

:deep(.dialogue-bubble__input) {
  width: 100%;
  min-width: 4rem;
  background: transparent;
  border: 0;
  outline: none;
  resize: none;
  color: inherit;
  font: inherit;
  line-height: inherit;
  padding: 0;
}

:deep(.dialogue-bubble__text) {
  display: block;
  white-space: pre-wrap;
}
</style>
