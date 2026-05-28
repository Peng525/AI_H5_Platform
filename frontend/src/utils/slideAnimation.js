/** 根据动效 id 返回 Vue transition 使用的 class 前缀 */
export function animationEnterClass(id) {
  const map = {
    fade: 'anim-fade',
    'slide-left': 'anim-slide-left',
    'slide-right': 'anim-slide-right',
    'slide-up': 'anim-slide-up',
    zoom: 'anim-zoom',
    flip: 'anim-flip',
    none: 'anim-none',
  }
  return map[id] || 'anim-fade'
}

export function getSlideAnimation(slide) {
  return slide?.animation || 'fade'
}
