import { ref, watch, onMounted, onUnmounted, unref } from 'vue'

/**
 * 跟踪画布元素在视口中的 DOM 矩形，供浮动工具栏定位。
 */
export function useElementAnchor({
  elementId,
  slideId,
  resolveElementEl,
  enabled = true,
  scrollRootRef = null,
}) {
  const anchorRect = ref(null)

  let rafId = null

  function readEnabled() {
    const v = unref(enabled)
    return v !== false
  }

  function updateRect() {
    if (!readEnabled()) {
      anchorRect.value = null
      return
    }
    const eid = unref(elementId)
    const sid = unref(slideId)
    if (!eid || sid == null || !resolveElementEl) {
      anchorRect.value = null
      return
    }
    const el = resolveElementEl(sid, eid)
    if (!el) {
      anchorRect.value = null
      return
    }
    const r = el.getBoundingClientRect()
    anchorRect.value = {
      left: r.left,
      top: r.top,
      width: r.width,
      height: r.height,
      bottom: r.bottom,
      right: r.right,
    }
  }

  function scheduleUpdate() {
    if (rafId != null) cancelAnimationFrame(rafId)
    rafId = requestAnimationFrame(() => {
      rafId = null
      updateRect()
    })
  }

  watch([() => unref(elementId), () => unref(slideId), () => unref(enabled)], scheduleUpdate, {
    immediate: true,
  })

  onMounted(() => {
    window.addEventListener('scroll', scheduleUpdate, true)
    window.addEventListener('resize', scheduleUpdate)
    const root = unref(scrollRootRef)
    root?.addEventListener?.('scroll', scheduleUpdate)
  })

  onUnmounted(() => {
    if (rafId != null) cancelAnimationFrame(rafId)
    window.removeEventListener('scroll', scheduleUpdate, true)
    window.removeEventListener('resize', scheduleUpdate)
    const root = unref(scrollRootRef)
    root?.removeEventListener?.('scroll', scheduleUpdate)
  })

  return { anchorRect, refresh: scheduleUpdate }
}

/** 计算浮动条位置样式（fixed） */
export function floatingBarStyle(anchorRect, placement = 'below', offset = 8) {
  if (!anchorRect) return { display: 'none' }
  const vw = window.innerWidth
  const vh = window.innerHeight
  const barW = Math.min(560, vw - 16)
  let left = anchorRect.left + anchorRect.width / 2 - barW / 2
  left = Math.max(8, Math.min(left, vw - barW - 8))

  if (placement === 'above') {
    const top = Math.max(8, anchorRect.top - offset)
    return {
      position: 'fixed',
      left: `${left}px`,
      bottom: `${vh - top}px`,
      width: `${barW}px`,
      zIndex: 1200,
    }
  }

  const top = Math.min(vh - 48, anchorRect.bottom + offset)
  return {
    position: 'fixed',
    left: `${left}px`,
    top: `${top}px`,
    width: `${barW}px`,
    zIndex: 1200,
  }
}
