/** 演示文稿提示词模板（要素 → 内容） */

export const DECK_PROMPT_FIELD_LABELS = ['主题', '受众', '结构', '风格']

/**
 * @typedef {{ label: string, value: string }} DeckPromptField
 * @typedef {{
 *   id: string
 *   title: string
 *   description?: string
 *   fields: DeckPromptField[]
 *   preview_url?: string
 * }} DeckPromptTemplate
 */

/** @type {DeckPromptTemplate[]} */
export const DECK_PROMPT_TEMPLATES = [
  {
    id: 'coral-reef-edu',
    title: '珊瑚礁生态保护',
    description: '面向本科生的科普演示',
    fields: [
      { label: '主题', value: '珊瑚礁生态保护与海洋生物多样性' },
      { label: '受众', value: '本科生与环境科学入门读者' },
      { label: '结构', value: '问题引入、生态价值、威胁因素、保护行动、结语' },
      { label: '风格', value: '科普友好、图文并重、数据可视化点缀' },
    ],
  },
  {
    id: 'coffee-brew-guide',
    title: '完美手冲咖啡',
    description: '生活技巧类短演示',
    fields: [
      { label: '主题', value: '如何冲泡一杯完美的特浓咖啡' },
      { label: '受众', value: '咖啡爱好者与居家入门者' },
      { label: '结构', value: '选豆、研磨、水温、萃取步骤、拉花技巧' },
      { label: '风格', value: '步骤清晰、温暖生活感、配图说明' },
    ],
  },
  {
    id: 'product-roadshow',
    title: '智能 H5 平台路演',
    description: '新产品功能介绍',
    fields: [
      { label: '主题', value: '智能 H5 演示平台功能与价值介绍' },
      { label: '受众', value: '潜在用户、合作伙伴与投资人' },
      { label: '结构', value: '痛点、产品亮点、核心功能、案例、行动号召' },
      { label: '风格', value: '商务专业、简洁大气、数据支撑' },
    ],
  },
  {
    id: 'digital-transform-report',
    title: '数字化转型复盘',
    description: '企业季度汇报',
    fields: [
      { label: '主题', value: '2025 企业数字化转型季度复盘' },
      { label: '受众', value: '管理层与业务负责人' },
      { label: '结构', value: '目标回顾、关键指标、项目进展、问题与下一步' },
      { label: '风格', value: '数据驱动、图表为主、结论先行' },
    ],
  },
  {
    id: 'decision-psychology',
    title: '决策心理学研讨',
    description: '团队培训工作坊',
    fields: [
      { label: '主题', value: '决策心理学：认知偏差与团队决策' },
      { label: '受众', value: '产品经理与团队负责人' },
      { label: '结构', value: '常见偏差、案例讨论、改进框架、练习' },
      { label: '风格', value: '互动研讨、案例故事、要点提炼' },
    ],
  },
  {
    id: 'campus-recruitment',
    title: '校园社团招新',
    description: '活动宣传方案',
    fields: [
      { label: '主题', value: '校园社团招新宣传与全年活动规划' },
      { label: '受众', value: '在校新生与社团成员' },
      { label: '结构', value: '社团介绍、亮点活动、加入方式、时间线' },
      { label: '风格', value: '年轻活力、色彩明快、信息清晰' },
    ],
  },
]

/** 将模板格式化为填入对话框的文本 */
export function formatDeckPromptTemplate(template) {
  if (!template?.fields?.length) return ''
  return template.fields.map((f) => `${f.label}：${f.value}`).join('\n')
}
