/** 画布分辨率预设 */
export const VIEWPORT_PRESETS = [
  { id: 'mobile-375', label: '手机 · iPhone', width: 375, height: 812, device: 'mobile' },
  { id: 'mobile-390', label: '手机 · 全面屏', width: 390, height: 844, device: 'mobile' },
  { id: 'mobile-360', label: '手机 · 安卓', width: 360, height: 780, device: 'mobile' },
  { id: 'web-1280', label: '网页 · 1280×720', width: 1280, height: 720, device: 'web' },
  { id: 'web-1920', label: '网页 · 1920×1080', width: 1920, height: 1080, device: 'web' },
  { id: 'web-1024', label: '网页 · 1024×768', width: 1024, height: 768, device: 'web' },
]

/** 页面切换动效（对应 slide.animation） */
export const PAGE_ANIMATIONS = [
  { id: 'fade', label: '淡入淡出', icon: 'blur_on' },
  { id: 'slide-left', label: '向左滑入', icon: 'arrow_back' },
  { id: 'slide-right', label: '向右滑入', icon: 'arrow_forward' },
  { id: 'slide-up', label: '向上滑入', icon: 'arrow_upward' },
  { id: 'zoom', label: '缩放进入', icon: 'zoom_in' },
  { id: 'flip', label: '翻转切换', icon: 'flip' },
  { id: 'none', label: '无动效', icon: 'block' },
]

/** 页面滚动/浏览模式（存 project settings） */
export const SCROLL_EFFECTS = [
  { id: 'page', label: '翻页模式', desc: '点击或按键切换整页' },
  { id: 'vertical', label: '纵向滚动', desc: '上下滚动浏览内容' },
  { id: 'horizontal', label: '横向滑动', desc: '左右滑动切换页面' },
  { id: 'snap', label: '滚动吸附', desc: '滚动时自动吸附到每一页' },
]

export function getViewportPreset(id) {
  return VIEWPORT_PRESETS.find((v) => v.id === id) || VIEWPORT_PRESETS[0]
}
