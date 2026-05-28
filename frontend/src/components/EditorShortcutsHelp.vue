<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/40"
        @click.self="close"
      >
        <div
          class="bg-white rounded-xl shadow-elevated border border-outline-variant w-full max-w-lg max-h-[85vh] overflow-hidden flex flex-col"
          role="dialog"
          aria-modal="true"
          aria-labelledby="shortcuts-help-title"
          @keydown.esc="close"
        >
          <div class="flex items-center justify-between gap-3 px-5 py-4 border-b border-outline-variant shrink-0">
            <div class="flex items-center gap-2 min-w-0">
              <span class="material-symbols-outlined text-primary">keyboard</span>
              <h2 id="shortcuts-help-title" class="font-semibold text-on-surface">快捷键说明</h2>
            </div>
            <button
              type="button"
              class="p-1.5 rounded-lg hover:bg-surface-container-low text-on-surface-variant"
              aria-label="关闭"
              @click="close"
            >
              <span class="material-symbols-outlined text-[20px]">close</span>
            </button>
          </div>

          <div class="overflow-y-auto px-5 py-4 space-y-5">
            <p class="text-xs text-on-surface-variant">
              Mac 用户可将 <kbd class="kbd">Ctrl</kbd> 换为 <kbd class="kbd">⌘</kbd>。在输入框内编辑文字时，撤回等快捷键不会触发。
            </p>

            <section v-for="group in EDITOR_SHORTCUT_GROUPS" :key="group.title">
              <h3 class="text-xs font-semibold text-on-surface-variant uppercase tracking-wide mb-2">
                {{ group.title }}
              </h3>
              <ul class="divide-y divide-outline-variant/60 border border-outline-variant rounded-lg overflow-hidden">
                <li
                  v-for="(item, idx) in group.items"
                  :key="`${group.title}-${idx}`"
                  class="flex items-center justify-between gap-4 px-3 py-2.5 text-sm bg-white"
                >
                  <span class="text-on-surface">{{ item.label }}</span>
                  <span class="flex flex-wrap items-center justify-end gap-1 shrink-0">
                    <template v-for="(key, ki) in item.keys" :key="ki">
                      <span v-if="ki > 0" class="text-on-surface-variant text-xs">+</span>
                      <kbd class="kbd">{{ key }}</kbd>
                    </template>
                  </span>
                </li>
              </ul>
            </section>
          </div>

          <div class="px-5 py-3 border-t border-outline-variant bg-surface-container-low shrink-0">
            <button
              type="button"
              class="w-full py-2 rounded-lg bg-primary text-on-primary text-sm font-medium"
              @click="close"
            >
              知道了
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { watch } from 'vue'
import { EDITOR_SHORTCUT_GROUPS } from '../constants/editorShortcuts'

const open = defineModel('open', { type: Boolean, default: false })

function close() {
  open.value = false
}

watch(open, (v) => {
  if (v) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})
</script>

<style scoped>
.kbd {
  display: inline-block;
  padding: 0.125rem 0.375rem;
  font-size: 11px;
  font-family: ui-monospace, monospace;
  line-height: 1.4;
  color: #1b1b1c;
  background: #f3f4f6;
  border: 1px solid #c0c7d6;
  border-radius: 4px;
  white-space: nowrap;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
