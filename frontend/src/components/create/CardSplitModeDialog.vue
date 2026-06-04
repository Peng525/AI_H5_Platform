<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/40"
        @click.self="$emit('cancel')"
      >
        <div
          class="bg-white rounded-xl shadow-elevated border border-outline-variant w-full max-w-md overflow-hidden"
          role="dialog"
          aria-modal="true"
          aria-labelledby="card-split-title"
        >
          <div class="p-6">
            <div class="flex items-start gap-3">
              <div class="w-10 h-10 rounded-full flex items-center justify-center shrink-0 bg-primary/10 text-primary">
                <span class="material-symbols-outlined">view_carousel</span>
              </div>
              <div class="min-w-0">
                <h2 id="card-split-title" class="font-semibold text-on-surface">按页数分页</h2>
                <p class="text-sm text-on-surface mt-2 leading-relaxed">
                  是否按当前的 <strong>{{ pageCount }}</strong> 张卡片进行分页？
                </p>
              </div>
            </div>
          </div>
          <div class="flex items-center justify-between gap-6 px-6 py-4 bg-surface-container-low border-t border-outline-variant">
            <div class="flex items-center gap-2">
              <button
                type="button"
                class="px-4 py-2.5 rounded-lg bg-primary text-on-primary text-sm font-medium hover:bg-primary-container transition whitespace-nowrap"
                @click="$emit('auto')"
              >
                自动分页
              </button>
              <button
                type="button"
                class="px-4 py-2.5 rounded-lg border border-outline-variant bg-white text-sm font-medium hover:bg-white transition whitespace-nowrap"
                @click="$emit('manual')"
              >
                自行分页
              </button>
            </div>
            <button
              type="button"
              class="shrink-0 px-4 py-2.5 rounded-lg bg-red-600 text-white text-sm font-medium hover:bg-red-700 transition whitespace-nowrap"
              @click="$emit('cancel')"
            >
              取消
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  open: { type: Boolean, default: false },
  pageCount: { type: Number, default: 10 },
})

defineEmits(['auto', 'manual', 'cancel'])
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
