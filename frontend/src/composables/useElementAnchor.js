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

/**
 * 计算浮动条位置样式（fixed）。
 * @param {object} options
 * @param {boolean} [options.compact] - 宽度随内容，水平居中对齐选中元素
 * @param {number} [options.barHeight=40] - 用于 above 时判断视口翻转
 * @param {number} [options.barWidth=560] - 非 compact 时的固定宽度
 */
export function floatingBarStyle(anchorRect, placement = 'below', offset = 8, options = {}) {
  if (!anchorRect) return { display: 'none' }

  const vw = typeof window !== 'undefined' ? window.innerWidth : 1024
  const vh = typeof window !== 'undefined' ? window.innerHeight : 768
  const edge = 8
  const barHeight = options.barHeight ?? 40
  const compact = options.compact === true

  const style = {
    position: 'fixed',
    zIndex: 1200,
  }

  if (compact) {
    let centerX = anchorRect.left + anchorRect.width / 2
    centerX = Math.max(edge, Math.min(centerX, vw - edge))
    style.left = `${centerX}px`
    style.maxWidth = `${vw - edge * 2}px`
    style.width = 'max-content'
  } else {
    const barW = Math.min(options.barWidth ?? 560, vw - edge * 2)
    let left = anchorRect.left + anchorRect.width / 2 - barW / 2
    left = Math.max(edge, Math.min(left, vw - barW - edge))
    style.left = `${left}px`
    style.width = `${barW}px`
  }

  const useAbove =
    placement === 'above' && anchorRect.top - offset - barHeight >= edge

  if (useAbove) {
    style.top = `${anchorRect.top - offset}px`
    style.transform = compact ? 'translateX(-50%) translateY(-100%)' : 'translateY(-100%)'
    return style
  }

  const top = Math.min(vh - barHeight - edge, anchorRect.bottom + offset)
  style.top = `${Math.max(edge, top)}px`
  if (compact) style.transform = 'translateX(-50%)'
  return style
}
