<template>
  <button
    type="button"
    class="bgm-player-btn"
    :class="{
      'bgm-player-btn--muted': muted,
      'bgm-player-btn--spinning': spinning,
    }"
    :title="muted ? '开启音乐' : '静音'"
    @click.stop="$emit('toggle')"
  >
    <span class="bgm-player-btn__disc" aria-hidden="true">
      <span class="material-symbols-outlined bgm-player-btn__icon">album</span>
    </span>
  </button>
</template>

<script setup>
defineProps({
  muted: { type: Boolean, default: false },
  spinning: { type: Boolean, default: false },
})

defineEmits(['toggle'])
</script>

<style scoped>
.bgm-player-btn {
  width: 2rem;
  height: 2rem;
  border-radius: 9999px;
  border: 1px solid #c0c7d6;
  background: #fff;
  box-shadow: 0 1px 4px rgba(27, 27, 28, 0.08);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #005daa;
  transition: border-color 0.15s, color 0.15s, background-color 0.15s;
}

.bgm-player-btn:hover {
  border-color: #005daa;
  background: #f8fbff;
}

.bgm-player-btn--muted {
  color: #6b7280;
}

.bgm-player-btn__disc {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 9999px;
  border: 1px solid currentColor;
}

.bgm-player-btn__icon {
  font-size: 14px;
  line-height: 1;
}

.bgm-player-btn--spinning .bgm-player-btn__disc {
  animation: bgm-disc-spin 3.5s linear infinite;
}

@keyframes bgm-disc-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
