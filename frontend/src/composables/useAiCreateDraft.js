const STORAGE_KEY = 'ai_create_draft'

export const DEFAULT_DRAFT = {
  type: 'deck',
  pageCount: 10,
  background: 'classic_white',
  viewportMode: 'auto',
  language: '简体中文',
  topic: '',
  audience: '',
  tone: '专业、清晰、具说服力',
  textDensity: '精炼',
  extraContent: '',
  extraInstructions: '',
}

export function loadDraft() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return { ...DEFAULT_DRAFT }
    return { ...DEFAULT_DRAFT, ...JSON.parse(raw) }
  } catch {
    return { ...DEFAULT_DRAFT }
  }
}

export function saveDraft(patch) {
  const next = { ...loadDraft(), ...patch }
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(next))
  return next
}

export function clearDraft() {
  sessionStorage.removeItem(STORAGE_KEY)
}

export function requireDeckDraft(router) {
  const draft = loadDraft()
  if (draft.type !== 'deck') {
    router.replace('/create/generate')
    return null
  }
  return draft
}

export function applyProjectSettingsLocal(projectId, settings) {
  const prefix = 'ai_h5_project_settings_'
  localStorage.setItem(
    prefix + projectId,
    JSON.stringify({
      viewportId: settings.viewportId || 'mobile-375',
      scrollEffect: settings.scrollEffect || 'vertical',
      themeId: settings.themeId || 'zjy-minimal',
      showScrollHint: settings.showScrollHint === true,
      slideBackgrounds: settings.slideBackgrounds || {},
      bgm: settings.bgm || { enabled: false, trackId: '', url: '', loop: true, volume: 0.35 },
      defaultChatTapToContinue: settings.defaultChatTapToContinue !== false,
    })
  )
}

export const EXAMPLE_PROMPT_GROUPS = [
  [
    '面向本科生的珊瑚礁生态保护科普演示',
    '如何冲泡一杯完美的特浓咖啡：从选豆到拉花',
    '自由职业者服务的定价策略与案例分享',
    '2025 企业数字化转型季度复盘报告',
    '决策心理学：认知偏差与团队决策研讨会',
    '营销绩效指标看板与增长实验方法论',
  ],
  [
    '新产品路演：智能 H5 演示平台功能介绍',
    '校园社团招新宣传与活动规划方案',
    '健康饮食一周计划与营养搭配指南',
    'AI 在教育培训行业的落地应用场景',
    '跨境电商品牌出海首年运营总结',
    '团队 OKR 制定与季度复盘工作坊',
  ],
]
