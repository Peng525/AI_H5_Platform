/** 设计主题：zjy 商务简约 + eqxiu 叙事公益 */
export const DESIGN_THEMES = {
  'zjy-minimal': {
    id: 'zjy-minimal',
    label: 'ZJY 商务简约',
    fonts: {
      display: '"DengXian", "等线", "Microsoft YaHei", sans-serif',
      body: '"DengXian", "等线 Light", "Microsoft YaHei", sans-serif',
    },
    colors: {
      bg: '#FFFFFF',
      bgMuted: '#E8E8E8',
      text: '#0E2841',
      textMuted: '#44546A',
      accent: '#156082',
      accent2: '#5B9BD5',
      onAccent: '#FFFFFF',
    },
    typeScale: {
      mobile: { display: 36, h1: 28, h2: 22, body: 16, caption: 13 },
      web: { display: 52, h1: 40, h2: 28, body: 20, caption: 15 },
    },
    margins: {
      mobile: { x: 32, contentWidth: 311 },
      web: { x: 80, contentWidth: 1120 },
    },
    gradients: [
      { id: 'zjy-white', label: '纯白', value: 'linear-gradient(180deg, #FFFFFF 0%, #FFFFFF 100%)' },
      { id: 'zjy-soft', label: '浅灰渐变', value: 'linear-gradient(180deg, #FFFFFF 0%, #E8E8E8 100%)' },
      { id: 'zjy-accent', label: '青蓝淡染', value: 'linear-gradient(135deg, #FFFFFF 0%, #E8F4F8 100%)' },
      { id: 'zjy-muted', label: '灰白', value: 'linear-gradient(180deg, #F5F5F5 0%, #E8E8E8 100%)' },
    ],
    palette: ['#0E2841', '#156082', '#44546A', '#E8E8E8', '#FFFFFF', '#5B9BD5'],
  },
  'eqxiu-story': {
    id: 'eqxiu-story',
    label: '易企秀叙事',
    fonts: {
      display: '"Microsoft YaHei", "PingFang SC", sans-serif',
      body: '"Microsoft YaHei", "PingFang SC", sans-serif',
    },
    colors: {
      bg: '#FFF8F3',
      bgMuted: '#FFE8D6',
      text: '#2D3436',
      textMuted: '#636E72',
      accent: '#E17055',
      accent2: '#00B894',
      onAccent: '#FFFFFF',
    },
    typeScale: {
      mobile: { display: 34, h1: 26, h2: 20, body: 17, caption: 14 },
      web: { display: 48, h1: 36, h2: 26, body: 22, caption: 16 },
    },
    margins: {
      mobile: { x: 28, contentWidth: 319 },
      web: { x: 72, contentWidth: 1136 },
    },
    gradients: [
      { id: 'eq-warm', label: '暖白', value: 'linear-gradient(180deg, #FFF8F3 0%, #FFE8D6 100%)' },
      { id: 'eq-peach', label: '蜜桃', value: 'linear-gradient(135deg, #FFF8F3 0%, #FFDAB9 100%)' },
      { id: 'eq-mint', label: '青绿淡染', value: 'linear-gradient(180deg, #FFF8F3 0%, #E8FFF8 100%)' },
      { id: 'eq-sunset', label: '夕照', value: 'linear-gradient(135deg, #FFE8D6 0%, #FFF8F3 50%, #E8FFF8 100%)' },
    ],
    palette: ['#2D3436', '#E17055', '#00B894', '#636E72', '#FFF8F3', '#FFE8D6'],
  },
}

export function getTheme(themeId) {
  return DESIGN_THEMES[themeId] || DESIGN_THEMES['zjy-minimal']
}

export function getThemePalette(themeId) {
  return getTheme(themeId).palette
}

export function isWebViewport(viewportId) {
  return String(viewportId || '').startsWith('web')
}

export function getThemeTypeScale(themeId, viewportId) {
  const theme = getTheme(themeId)
  return isWebViewport(viewportId) ? theme.typeScale.web : theme.typeScale.mobile
}

export function getThemeMargins(themeId, viewportId) {
  const theme = getTheme(themeId)
  return isWebViewport(viewportId) ? theme.margins.web : theme.margins.mobile
}

export function getThemeGradients(themeId) {
  return getTheme(themeId).gradients || []
}

export function getThemeTextPreset(themeId, role) {
  const theme = getTheme(themeId)
  const colors = theme.colors
  const roles = {
    display: { fontWeight: 'bold', color: colors.text },
    h1: { fontWeight: 'bold', color: colors.text },
    h2: { fontWeight: '600', color: colors.text },
    body: { fontWeight: 'normal', color: colors.textMuted },
    caption: { fontWeight: 'normal', color: colors.textMuted },
    accent: { fontWeight: '600', color: colors.accent },
    onAccent: { fontWeight: 'normal', color: colors.onAccent },
  }
  return roles[role] || roles.body
}
