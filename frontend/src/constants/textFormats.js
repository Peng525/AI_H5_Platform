import { getTheme, getThemePalette } from './designThemes.js'
export const FONT_FAMILIES = [
  { id: 'dengxian', label: '等线', value: '"DengXian", "等线", "Microsoft YaHei", sans-serif' },
  { id: 'yahei', label: '微软雅黑', value: '"Microsoft YaHei", "PingFang SC", sans-serif' },
  { id: 'song', label: '宋体', value: '"SimSun", "Songti SC", serif' },
  { id: 'hei', label: '黑体', value: '"SimHei", "Heiti SC", sans-serif' },
  { id: 'kaiti', label: '楷体', value: '"KaiTi", "STKaiti", serif' },
  { id: 'inter', label: 'Inter', value: 'Inter, sans-serif' },
  { id: 'arial', label: 'Arial', value: 'Arial, sans-serif' },
]

/** Word 风格主题色 + 标准色 */
export const THEME_COLORS = [
  '#0E2841', '#156082', '#44546A', '#E8E8E8', '#FFFFFF', '#5B9BD5', '#E17055', '#00B894',
]

export const STANDARD_COLORS = [
  '#C00000', '#FF0000', '#FFC000', '#FFFF00', '#92D050', '#00B050',
  '#00B0F0', '#0070C0', '#7030A0', '#FFFFFF', '#000000', '#E7E6E6',
  '#44546A', '#5B9BD5', '#ED7D31', '#70AD47', '#264478', '#9E480E',
]

export function themePaletteColors(themeId = 'zjy-minimal') {
  return getThemePalette(themeId)
}

export const FONT_SIZES = [10, 11, 12, 14, 16, 17, 18, 20, 22, 24, 26, 28, 32, 36, 40, 48, 52]

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

/** 一键套用：Display / 大标题 / 小标题 / 正文 / 注释 */
export const TEXT_PRESETS = {
  display: {
    label: '大标题',
    style: { fontSize: 36, fontWeight: 'bold', lineHeight: 1.2, letterSpacing: 0, color: '#0E2841' },
  },
  title: {
    label: '标题',
    style: { fontSize: 28, fontWeight: 'bold', lineHeight: 1.3, letterSpacing: 0, color: '#0E2841' },
  },
  subtitle: {
    label: '小标题',
    style: { fontSize: 22, fontWeight: '600', lineHeight: 1.35, letterSpacing: 0, color: '#0E2841' },
  },
  body: {
    label: '正文',
    style: { fontSize: 16, fontWeight: 'normal', lineHeight: 1.6, letterSpacing: 0, color: '#44546A' },
  },
  caption: {
    label: '注释',
    style: { fontSize: 13, fontWeight: 'normal', lineHeight: 1.5, letterSpacing: 0, color: '#44546A' },
  },
}

/** 按设计主题生成文字样式预设 */
export function getThemeTextPresets(themeId = 'zjy-minimal', viewportId = 'mobile-375') {
  const theme = getTheme(themeId)
  const scale = viewportId.startsWith('web') ? theme.typeScale.web : theme.typeScale.mobile
  const { colors, fonts } = theme
  return {
    display: {
      label: '大标题',
      style: {
        fontSize: scale.display,
        fontWeight: 'bold',
        lineHeight: 1.2,
        color: colors.text,
        fontFamily: fonts.display,
      },
    },
    title: {
      label: '标题',
      style: {
        fontSize: scale.h1,
        fontWeight: 'bold',
        lineHeight: 1.3,
        color: colors.text,
        fontFamily: fonts.display,
      },
    },
    subtitle: {
      label: '小标题',
      style: {
        fontSize: scale.h2,
        fontWeight: '600',
        lineHeight: 1.35,
        color: colors.text,
        fontFamily: fonts.body,
      },
    },
    body: {
      label: '正文',
      style: {
        fontSize: scale.body,
        fontWeight: 'normal',
        lineHeight: 1.6,
        color: colors.textMuted,
        fontFamily: fonts.body,
      },
    },
    caption: {
      label: '注释',
      style: {
        fontSize: scale.caption,
        fontWeight: 'normal',
        lineHeight: 1.5,
        color: colors.textMuted,
        fontFamily: fonts.body,
      },
    },
  }
}
