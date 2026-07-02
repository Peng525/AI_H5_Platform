<template>
  <div
    class="relative rounded px-1 py-0.5 min-h-[1.5rem] cursor-text"
    :class="{
      'ring-2 ring-primary/40 bg-primary/5': selected,
      'hover:bg-surface-container-low/80': !selected,
    }"
    :data-resume-bind="bind"
    @click.stop="onClick"
  >
    <label v-if="label" class="text-[11px] text-on-surface-variant block">{{ label }}</label>
    <textarea
      v-if="editing"
      ref="inputRef"
      :value="modelValue"
      rows="1"
      class="w-full text-sm border border-primary/30 rounded px-1 py-0.5 bg-white resize-none focus:outline-none"
      :style="inlineStyle"
      @input="$emit('update:modelValue', $event.target.value)"
      @blur="$emit('blur')"
      @keydown.enter.exact.prevent="$emit('blur')"
    />
    <div
      v-else
      class="text-sm whitespace-pre-wrap break-words"
      :style="inlineStyle"
    >
      {{ displayValue }}
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'

const props = defineProps({
  bind: { type: String, required: true },
  label: { type: String, default: '' },
  modelValue: { type: String, default: '' },
  stylePatch: { type: Object, default: () => ({}) },
  selected: { type: Boolean, default: false },
  editing: { type: Boolean, default: false },
  placeholder: { type: String, default: '点击编辑' },
})

const emit = defineEmits(['select', 'edit', 'update:modelValue', 'blur'])

const inputRef = ref(null)

const displayValue = computed(() => props.modelValue || props.placeholder)

const inlineStyle = computed(() => ({
  fontSize: props.stylePatch.fontSize ? `${props.stylePatch.fontSize}px` : undefined,
  fontWeight: props.stylePatch.fontWeight || undefined,
  color: props.stylePatch.color || undefined,
  textAlign: props.stylePatch.textAlign || undefined,
  fontFamily: props.stylePatch.fontFamily || undefined,
}))

function onClick() {
  emit('select', props.bind)
  emit('edit', props.bind)
}

watch(
  () => props.editing,
  async (v) => {
    if (v) {
      await nextTick()
      inputRef.value?.focus()
      inputRef.value?.select()
    }
  },
)
</script>
