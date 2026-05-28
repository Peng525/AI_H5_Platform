<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/40"
        @click.self="$emit('cancel')"
      >
        <div class="bg-white rounded-xl shadow-elevated border border-outline-variant w-full max-w-sm overflow-hidden" role="dialog">
          <div class="p-6">
            <div class="flex items-start gap-3">
              <div class="w-10 h-10 rounded-full bg-primary/10 text-primary flex items-center justify-center shrink-0">
                <span class="material-symbols-outlined">logout</span>
              </div>
              <div>
                <h2 class="font-semibold">退出登录</h2>
                <p class="text-sm text-on-surface-variant mt-2 leading-relaxed">
                  退出后将返回登录页。是否在本地<strong class="text-on-surface">保留账号和密码</strong>，以便下次自动登录？
                </p>
              </div>
            </div>
          </div>
          <div class="flex flex-col gap-2 px-6 py-4 bg-surface-container-low border-t border-outline-variant">
            <button
              type="button"
              class="w-full py-2.5 rounded-lg bg-primary text-on-primary text-sm font-medium"
              @click="$emit('confirm', true)"
            >
              保留密码并退出
            </button>
            <button
              type="button"
              class="w-full py-2.5 rounded-lg border border-outline-variant text-sm font-medium hover:bg-white"
              @click="$emit('confirm', false)"
            >
              不保留，退出
            </button>
            <button
              type="button"
              class="w-full py-2 text-sm text-on-surface-variant hover:text-on-surface"
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
})

defineEmits(['confirm', 'cancel'])
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
