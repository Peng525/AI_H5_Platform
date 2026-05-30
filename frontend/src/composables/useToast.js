import { ref } from 'vue'

const toasts = ref([])
let seq = 0

export function useToast() {
  function show(message, { type = 'info', duration = 3200 } = {}) {
    const id = ++seq
    toasts.value.push({ id, message, type })
    if (duration > 0) {
      setTimeout(() => dismiss(id), duration)
    }
    return id
  }

  function success(message, opts) {
    return show(message, { ...opts, type: 'success' })
  }

  function error(message, opts) {
    return show(message, { ...opts, type: 'error', duration: opts?.duration ?? 4500 })
  }

  function dismiss(id) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  return { toasts, show, success, error, dismiss }
}
