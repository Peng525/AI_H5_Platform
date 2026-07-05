import { ref } from 'vue'

const DRAG_THRESHOLD = 4

/**
 * 画布框选（marquee）逻辑，供 EditorPhoneCanvas 与 ResultSlideCardCanvas 共用。
 */
export function useMarqueeSelect({ clientToLocal, getElements, onDeselect, onMarqueeSelect }) {
  const marqueeRect = ref(null)

  function onCanvasPointerDown(e) {
    if (e.button !== 0) return
    e.preventDefault()
    e.stopPropagation()

    const startClient = { x: e.clientX, y: e.clientY }
    const startLocal = clientToLocal(startClient.x, startClient.y)
    let dragging = false

    marqueeRect.value = { x: startLocal.x, y: startLocal.y, w: 0, h: 0 }

    function onMove(ev) {
      const dx = ev.clientX - startClient.x
      const dy = ev.clientY - startClient.y
      if (!dragging && Math.hypot(dx, dy) < DRAG_THRESHOLD) return
      dragging = true
      const cur = clientToLocal(ev.clientX, ev.clientY)
      const x = Math.min(startLocal.x, cur.x)
      const y = Math.min(startLocal.y, cur.y)
      marqueeRect.value = {
        x,
        y,
        w: Math.abs(cur.x - startLocal.x),
        h: Math.abs(cur.y - startLocal.y),
      }
    }

    function onUp(ev) {
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
      const rect = marqueeRect.value
      marqueeRect.value = null

      if (!dragging) {
        onDeselect?.()
        return
      }

      if (!rect || rect.w < 2 || rect.h < 2) {
        onDeselect?.()
        return
      }

      const elements = getElements?.() || []
      const ids = elements.filter((el) => elementIntersectsRect(el, rect)).map((el) => el.id)
      onMarqueeSelect?.({
        ids,
        additive: ev.ctrlKey || ev.metaKey || ev.shiftKey,
      })
    }

    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
  }

  return { marqueeRect, onCanvasPointerDown }
}

function elementIntersectsRect(el, rect) {
  const ex = el.x ?? 0
  const ey = el.y ?? 0
  const ew = el.width ?? 0
  const eh = el.height ?? 0
  return !(ex + ew < rect.x || rect.x + rect.w < ex || ey + eh < rect.y || rect.y + rect.h < ey)
}
