/** 页面画布默认背景与浅色预设 */
export const DEFAULT_CANVAS_BG = '#DCEEFB'

/** AI 生成向导「经典白粉」背景，与后端 BACKGROUND_COLORS.classic_white 一致 */
export const CLASSIC_WHITE_PINK_BG = '#fafafa'

export const BACKGROUND_PRESET_COLORS = {
  classic_white: CLASSIC_WHITE_PINK_BG,
  light_gray: '#f0f2f5',
}

export const CANVAS_BACKGROUND_PRESETS = [
  { label: '浅蓝', value: '#DCEEFB' },
  { label: '浅粉', value: '#FCE8F0' },
  { label: '浅灰', value: '#F0F0F0' },
  { label: '肤色', value: '#F5E6D8' },
  { label: '经典白粉', value: CLASSIC_WHITE_PINK_BG },
]
