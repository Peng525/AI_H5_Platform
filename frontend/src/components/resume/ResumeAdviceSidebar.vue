<template>
  <aside
    class="h-full border-l border-outline-variant bg-white flex flex-col shrink-0 transition-all duration-200"
    :class="compact ? 'w-16' : 'w-72'"
  >
    <button
      type="button"
      class="p-2 text-xs text-on-surface-variant border-b border-outline-variant hover:bg-surface-container-low"
      @click="compact = !compact"
    >
      {{ compact ? '展开' : '收起' }}
    </button>
    <div v-if="!compact" class="flex-1 overflow-y-auto p-4 space-y-4 text-sm">
      <section>
        <h3 class="font-semibold text-on-surface mb-2">下一步建议</h3>
        <ul class="space-y-2 text-on-surface-variant">
          <li v-for="(step, i) in nextSteps" :key="i" class="flex gap-2">
            <span class="text-primary">•</span>
            <span>{{ step }}</span>
          </li>
        </ul>
      </section>
      <section v-if="advice.apply_strategy">
        <h3 class="font-semibold text-on-surface mb-1">投递策略</h3>
        <p class="text-on-surface-variant leading-relaxed">{{ advice.apply_strategy }}</p>
      </section>
      <section v-if="advice.interview_prep">
        <h3 class="font-semibold text-on-surface mb-1">面试准备</h3>
        <p class="text-on-surface-variant leading-relaxed">{{ advice.interview_prep }}</p>
      </section>
      <section v-if="advice.skill_gaps">
        <h3 class="font-semibold text-on-surface mb-1">能力提升</h3>
        <p class="text-on-surface-variant leading-relaxed">{{ advice.skill_gaps }}</p>
      </section>
    </div>
    <div v-else class="flex-1 p-2 text-[10px] text-on-surface-variant writing-vertical text-center">
      建议
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  advice: { type: Object, default: () => ({}) },
  nextSteps: { type: Array, default: () => [] },
  generating: { type: Boolean, default: false },
})

const compact = ref(false)
</script>

<style scoped>
.writing-vertical {
  writing-mode: vertical-rl;
  text-orientation: mixed;
}
</style>
