/** 画布分辨率预设 */
export const VIEWPORT_PRESETS = [
  { id: 'mobile-375', label: '手机 · iPhone', width: 375, height: 812, device: 'mobile' },
  { id: 'mobile-390', label: '手机 · 全面屏', width: 390, height: 844, device: 'mobile' },
  { id: 'mobile-360', label: '手机 · 安卓', width: 360, height: 780, device: 'mobile' },
  /** Gamma 风格宽屏卡片：参考截图 1024×401，约 2.55:1 */
  { id: 'web-wide-1024', label: '网页 · 1024×401', width: 1024, height: 401, device: 'web', aspect: 'wide' },
  { id: 'web-1280', label: '网页 · 1280×720', width: 1280, height: 720, device: 'web' },
  { id: 'web-1920', label: '网页 · 1920×1080', width: 1920, height: 1080, device: 'web' },
  { id: 'web-1024', label: '网页 · 1024×768', width: 1024, height: 768, device: 'web' },
]

/** AI 演示默认画布（标准 16:9 PPT 比例） */
export const DEFAULT_WEB_VIEWPORT_ID = 'web-1280'

/** 宽屏阈值：宽/高 ≥ 此值视为 Gamma 风格横条卡片 */
export const WIDE_VIEWPORT_RATIO = 2.2

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
  { id: 'vertical', label: '纵向滚动', desc: '同一页面内下滑，无感切换每一屏' },
  { id: 'horizontal', label: '横向滑动', desc: '左右滑动切换页面' },
  { id: 'snap', label: '滚动吸附', desc: '滚动时自动吸附到每一页' },
]

export function getViewportPreset(id) {
  return VIEWPORT_PRESETS.find((v) => v.id === id) || getViewportPreset(DEFAULT_WEB_VIEWPORT_ID)
}

export function getLayoutCanvasSize(viewportId) {
  const vp = getViewportPreset(viewportId)
  return {
    width: vp.width,
    height: vp.height,
    aspectRatio: vp.width / vp.height,
  }
}

export function isWideWebViewport(viewportId) {
  const { aspectRatio } = getLayoutCanvasSize(viewportId)
  return String(viewportId || '').startsWith('web') && aspectRatio >= WIDE_VIEWPORT_RATIO
}

/** AI 生图分辨率分组（与画布预设 id 一致） */
export const IMAGE_GEN_PRESET_GROUPS = [
  { label: '苹果', ids: ['mobile-375', 'mobile-390'] },
  { label: '安卓', ids: ['mobile-360'] },
  { label: '网页', ids: ['web-wide-1024', 'web-1280', 'web-1920', 'web-1024'] },
]

export const IMAGE_GEN_PRESET_IDS = IMAGE_GEN_PRESET_GROUPS.flatMap((g) => g.ids)

/** 画布可编辑内容区（扣除手机状态栏 / 网页标题栏） */
export function getCanvasContentSize(viewport) {
  const chrome = viewport?.device === 'mobile' ? 28 : 0
  const width = viewport?.width ?? 375
  const height = (viewport?.height ?? 812) - chrome
  return { width, height, chrome }
}
