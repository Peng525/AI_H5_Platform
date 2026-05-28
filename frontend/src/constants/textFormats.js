/** 字体列表（类似 Word） */
export const FONT_FAMILIES = [
  { id: 'yahei', label: '微软雅黑', value: '"Microsoft YaHei", "PingFang SC", sans-serif' },
  { id: 'song', label: '宋体', value: '"SimSun", "Songti SC", serif' },
  { id: 'hei', label: '黑体', value: '"SimHei", "Heiti SC", sans-serif' },
  { id: 'kaiti', label: '楷体', value: '"KaiTi", "STKaiti", serif' },
  { id: 'inter', label: 'Inter', value: 'Inter, sans-serif' },
  { id: 'arial', label: 'Arial', value: 'Arial, sans-serif' },
]

/** Word 风格主题色 + 标准色 */
export const THEME_COLORS = [
  '#000000', '#44546A', '#4472C4', '#ED7D31', '#A5A5A5', '#FFC000', '#5B9BD5', '#70AD47',
]

export const STANDARD_COLORS = [
  '#C00000', '#FF0000', '#FFC000', '#FFFF00', '#92D050', '#00B050',
  '#00B0F0', '#0070C0', '#7030A0', '#FFFFFF', '#000000', '#E7E6E6',
  '#44546A', '#5B9BD5', '#ED7D31', '#70AD47', '#264478', '#9E480E',
]

export const FONT_SIZES = [10, 11, 12, 14, 16, 18, 20, 22, 24, 28, 32, 36, 48]

export const LINE_HEIGHTS = [
  { label: '1.0', value: 1 },
  { label: '1.15', value: 1.15 },
  { label: '1.5', value: 1.5 },
  { label: '1.75', value: 1.75 },
  { label: '2.0', value: 2 },
]

export const LETTER_SPACINGS = [
  { label: '默认', value: 0 },
  { label: '加宽', value: 1 },
  { label: '更宽', value: 2 },
  { label: '紧凑', value: -0.5 },
]

/** 一键套用：标题 / 正文 / 小字 */
export const TEXT_PRESETS = {
  title: {
    label: '标题',
    style: {
      fontSize: 28,
      fontWeight: 'bold',
      lineHeight: 1.3,
      letterSpacing: 0,
    },
  },
  body: {
    label: '正文',
    style: {
      fontSize: 16,
      fontWeight: 'normal',
      lineHeight: 1.6,
      letterSpacing: 0,
    },
  },
  caption: {
    label: '小字',
    style: {
      fontSize: 12,
      fontWeight: 'normal',
      lineHeight: 1.5,
      letterSpacing: 0,
    },
  },
}
