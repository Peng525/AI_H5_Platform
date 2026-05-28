/** 编辑器离开/预览前强制保存画布。 */
let flushFn = null

export function registerCanvasFlush(fn) {
  flushFn = fn
}

export function unregisterCanvasFlush() {
  flushFn = null
}

export async function flushCanvasSave() {
  if (flushFn) await flushFn()
}
