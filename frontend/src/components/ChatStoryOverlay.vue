<template>
  <div
    v-if="active && script?.enabled && timeline.length"
    class="chat-overlay absolute inset-0 z-30 flex flex-col backdrop-blur-[2px] cursor-pointer select-none"
    :style="overlayBgStyle"
    @click="onTap"
    @contextmenu.prevent="skipAll"
  >
    <div class="flex-1 overflow-y-auto px-3 py-4 space-y-3 min-h-0 chat-messages">
      <TransitionGroup name="chat-msg">
        <template v-for="(item, i) in visibleItems" :key="item.id || i">
          <div
            v-if="item.type === 'timestamp'"
            class="text-center text-xs py-1"
            :style="timestampStyle(script.style)"
          >
            {{ item.text }}
          </div>
          <div
            v-else
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
                class="px-3 py-2.5 text-[15px] leading-relaxed break-words shadow-sm"
                :style="bubbleInlineStyle(item.isOwner, script.style)"
              >
                {{ item.text }}
              </div>
            </div>
          </div>
        </template>
      </TransitionGroup>
    </div>

    <div class="shrink-0 py-3 text-center text-xs opacity-60 animate-pulse" :style="{ color: script.style?.dateTextColor || '#666' }">
      {{ hintText }}
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { normalizeChatScript } from '../utils/chatScript.js'
import {
  avatarInlineStyle,
  avatarInitial,
  bubbleInlineStyle,
  buildRenderableTimeline,
  dialogueBackgroundStyle,
  timestampStyle,
} from '../utils/dialogueRender.js'

const props = defineProps({
  script: { type: Object, default: null },
  active: { type: Boolean, default: false },
})

const emit = defineEmits(['complete', 'progress'])

const visibleCount = ref(0)
let autoTimer = null

const normalized = computed(() => normalizeChatScript(props.script || {}))
const script = computed(() => normalized.value)
const timeline = computed(() => buildRenderableTimeline(normalized.value))
const visibleItems = computed(() => timeline.value.slice(0, visibleCount.value))
const allVisible = computed(() => visibleCount.value >= timeline.value.length)

const overlayBgStyle = computed(() => ({
  ...dialogueBackgroundStyle(script.value.style),
  backgroundColor: `${dialogueBackgroundStyle(script.value.style).background}f2`,
}))

const hintText = computed(() => {
  if (!timeline.value.length) return ''
  if (visibleCount.value === 0) return '点击开始对话'
  if (!allVisible.value) return '点击继续'
  return '点击进入下一页'
})

function clearAutoTimer() {
  if (autoTimer) {
    clearTimeout(autoTimer)
    autoTimer = null
  }
}

function scheduleAutoAdvance() {
  clearAutoTimer()
  const ms = Number(script.value.autoAdvanceMs || 0)
  if (!ms || !props.active || allVisible.value) return
  autoTimer = setTimeout(() => {
    if (visibleCount.value < timeline.value.length) {
      visibleCount.value += 1
      emit('progress', visibleCount.value)
      scheduleAutoAdvance()
    }
  }, ms)
}

function reset() {
  clearAutoTimer()
  visibleCount.value = 0
  if (props.active && timeline.value.length && Number(script.value.autoAdvanceMs || 0) > 0) {
    visibleCount.value = 1
    emit('progress', 1)
    scheduleAutoAdvance()
  }
}

function onTap() {
  if (!timeline.value.length) {
    emit('complete')
    return
  }
  if (visibleCount.value < timeline.value.length) {
    visibleCount.value += 1
    emit('progress', visibleCount.value)
    scheduleAutoAdvance()
    return
  }
  emit('complete')
}

function skipAll() {
  visibleCount.value = timeline.value.length
  emit('progress', visibleCount.value)
  clearAutoTimer()
}

watch(
  () => [props.active, props.script],
  () => reset(),
  { immediate: true, deep: true }
)
</script>

<style scoped>
.chat-msg-enter-active {
  transition: opacity 0.28s ease, transform 0.28s ease;
}
.chat-msg-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.chat-messages {
  -webkit-overflow-scrolling: touch;
}
</style>
