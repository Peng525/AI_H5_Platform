/** 全局只允许一个颜色面板打开，并在画布上下文切换时统一关闭 */
let activeClose = null

export function openColorPickerSession(closeFn) {
  if (activeClose && activeClose !== closeFn) {
    activeClose()
  }
  activeClose = closeFn
}

export function closeColorPickerSession(closeFn) {
  if (activeClose === closeFn) {
    activeClose = null
  }
}

export function closeActiveColorPicker() {
  if (activeClose) {
    activeClose()
    activeClose = null
  }
}
