<template>
  <div
    v-if="active && script?.enabled && messages.length"
    class="chat-overlay absolute inset-0 z-30 flex flex-col bg-[#ededed]/95 backdrop-blur-[2px] cursor-pointer select-none"
    @click="onTap"
    @contextmenu.prevent="skipAll"
  >
    <div class="flex-1 overflow-y-auto px-3 py-4 space-y-4 min-h-0 chat-messages">
      <TransitionGroup name="chat-msg">
        <div
          v-for="(msg, i) in visibleMessages"
          :key="msg.id || i"
          class="flex gap-2 items-start"
          :class="msg.side === 'right' ? 'flex-row-reverse' : 'flex-row'"
        >
          <div
            class="shrink-0 w-10 h-10 rounded overflow-hidden bg-gray-300 flex items-center justify-center text-sm font-semibold text-gray-700"
            :class="msg.side === 'right' ? 'bg-[#95EC69]/30' : 'bg-white'"
          >
            <img
              v-if="msg.avatar"
              :src="msg.avatar"
              alt=""
              class="w-full h-full object-cover"
              @error="($event.target.style.display = 'none')"
            />
            <span v-else>{{ avatarInitial(msg) }}</span>
          </div>
          <div class="max-w-[72%] min-w-0">
            <p
              v-if="msg.name"
              class="text-[11px] text-gray-500 mb-0.5"
              :class="msg.side === 'right' ? 'text-right' : 'text-left'"
            >
              {{ msg.name }}
            </p>
            <div
              class="relative px-3 py-2.5 text-[15px] leading-relaxed break-words shadow-sm"
              :class="bubbleClass(msg.side)"
            >
              {{ msg.text }}
            </div>
          </div>
        </div>
      </TransitionGroup>
    </div>

    <div class="shrink-0 py-3 text-center text-xs text-gray-500 animate-pulse">
      {{ hintText }}
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  script: { type: Object, default: null },
  active: { type: Boolean, default: false },
})

const emit = defineEmits(['complete', 'progress'])

const visibleCount = ref(0)
let autoTimer = null

const messages = computed(() => {
  const list = props.script?.messages
  return Array.isArray(list) ? list : []
})

const visibleMessages = computed(() => messages.value.slice(0, visibleCount.value))

const allVisible = computed(() => visibleCount.value >= messages.value.length)

const hintText = computed(() => {
  if (!messages.value.length) return ''
  if (visibleCount.value === 0) return '点击开始对话'
  if (!allVisible.value) return '点击继续'
  return '点击进入下一页'
})

function avatarInitial(msg) {
  const name = (msg.name || (msg.side === 'right' ? '我' : 'TA')).trim()
  return name.slice(0, 1).toUpperCase()
}

function bubbleClass(side) {
  if (side === 'right') {
    return 'bg-[#95EC69] text-gray-900 rounded-lg rounded-tr-sm'
  }
  return 'bg-white text-gray-900 rounded-lg rounded-tl-sm'
}

function clearAutoTimer() {
  if (autoTimer) {
    clearTimeout(autoTimer)
    autoTimer = null
  }
}

function scheduleAutoAdvance() {
  clearAutoTimer()
  const ms = Number(props.script?.autoAdvanceMs || 0)
  if (!ms || !props.active || allVisible.value) return
  autoTimer = setTimeout(() => {
    if (visibleCount.value < messages.value.length) {
      visibleCount.value += 1
      emit('progress', visibleCount.value)
      scheduleAutoAdvance()
    }
  }, ms)
}

function reset() {
  clearAutoTimer()
  visibleCount.value = 0
  if (props.active && messages.value.length && Number(props.script?.autoAdvanceMs || 0) > 0) {
    visibleCount.value = 1
    emit('progress', 1)
    scheduleAutoAdvance()
  }
}

function onTap() {
  if (!messages.value.length) {
    emit('complete')
    return
  }
  if (visibleCount.value < messages.value.length) {
    visibleCount.value += 1
    emit('progress', visibleCount.value)
    scheduleAutoAdvance()
    return
  }
  emit('complete')
}

function skipAll() {
  visibleCount.value = messages.value.length
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
