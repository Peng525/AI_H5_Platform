<template>
  <div
    class="relative rounded px-1 py-0.5 min-h-[1.5rem] cursor-text"
    :class="{
      'ring-2 ring-inset ring-primary/40 bg-primary/5': selected,
      'hover:bg-surface-container-low/80': !selected,
    }"
    :data-resume-bind="bind"
    @click.stop="onClick"
  >
    <label v-if="label" class="text-[11px] text-on-surface-variant block mb-0.5">{{ label }}</label>
    <div class="grid grid-cols-1 grid-rows-1 w-full">
      <div
        class="col-start-1 row-start-1 invisible pointer-events-none whitespace-pre-wrap break-words text-sm leading-5 px-1 py-0.5 border border-transparent rounded"
        :style="inlineStyle"
        aria-hidden="true"
      >{{ ghostText }}</div>
      <div
        v-show="!editing"
        class="col-start-1 row-start-1 text-sm leading-5 whitespace-pre-wrap break-words px-1 py-0.5 border border-transparent rounded"
        :class="isEmpty ? 'text-on-surface-variant/50' : ''"
        :style="inlineStyle"
      >{{ displayValue }}</div>
      <textarea
        v-show="editing"
        ref="inputRef"
        :value="modelValue"
        rows="1"
        class="col-start-1 row-start-1 w-full h-full min-h-0 text-sm leading-5 px-1 py-0.5 border border-primary/30 rounded bg-white resize-none overflow-hidden focus:outline-none field-sizing-content"
        :style="inlineStyle"
        @input="onInput"
        @blur="$emit('blur')"
        @keydown.enter.exact.prevent="$emit('blur')"
      />
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

const isEmpty = computed(() => !props.modelValue?.trim())

const ghostText = computed(() => props.modelValue || props.placeholder || '\u00a0')

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

function syncTextareaHeight() {
  const el = inputRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${el.scrollHeight}px`
}

function onInput(e) {
  emit('update:modelValue', e.target.value)
  syncTextareaHeight()
}

watch(
  () => props.editing,
  async (v) => {
    if (v) {
      await nextTick()
      syncTextareaHeight()
      inputRef.value?.focus()
      inputRef.value?.select()
    }
  },
)

watch(
  () => props.modelValue,
  async () => {
    if (!props.editing) return
    await nextTick()
    syncTextareaHeight()
  },
)
</script>
