/**
 * 图标自动匹配引擎
 * 根据中文文本内容，通过关键词映射自动选择合适的 Material Symbol 图标
 * 无需 AI 参与 — 纯前端规则匹配
 */

/**
 * 关键词 → 图标映射表（按优先级排序）
 * 格式：{ keywords: '关键词1|关键词2', icon: 'material_symbol_name' }
 * 匹配时按数组顺序优先匹配
 */
const ICON_RULES = [
  // ── 增长/趋势 ──
  { keywords: '增长|增速|上升|提升|涨幅|上涨|攀升|翻倍|激增|爆发|腾飞', icon: 'trending_up' },
  { keywords: '下降|下滑|降低|减少|跌幅|回落|收缩|衰退', icon: 'trending_down' },

  // ── 技术/创新 ──
  { keywords: '智能|AI|人工智能|算法|机器学习|深度学习|神经网络|大模型|GPT|自动驾驶|自动|智慧', icon: 'smart_toy' },
  { keywords: '创新|突破|首创|领先|前沿|革命|颠覆|开创|原创', icon: 'rocket_launch' },
  { keywords: '技术|科技|研发|专利|核心技术|黑科技|硬科技|工程', icon: 'precision_manufacturing' },

  // ── 数据/分析 ──
  { keywords: '数据|大数据|分析|统计|指标|数字|量化|检测|监控|仪表盘', icon: 'bar_chart' },
  { keywords: '图表|报表|报告|趋势图|看板|可视化', icon: 'dashboard' },

  // ── 安全/防护 ──
  { keywords: '安全|防护|保护|保障|加密|防火墙|隐私|合规|风控|风险|防御|盾', icon: 'shield' },
  { keywords: '认证|检测|验证|审核|鉴定|测试|检验|把关', icon: 'verified' },

  // ── 成本/财务 ──
  { keywords: '成本|费用|价格|预算|节省|节约|降本|省钱|经济|廉价|低成本', icon: 'payments' },
  { keywords: '收入|利润|盈利|收益|营收|赚钱|变现|回报|ROI|投资|融资', icon: 'account_balance' },

  // ── 效率/速度 ──
  { keywords: '效率|高效|提速|快速|速度|加速|敏捷|灵活|响应|实时|即时', icon: 'bolt' },
  { keywords: '优化|改善|提升|改进|升级|迭代|进化|进步|精进', icon: 'auto_fix_high' },

  // ── 产品/服务 ──
  { keywords: '产品|商品|新品|发布|上市|推出|上架|SKU|品类', icon: 'inventory_2' },
  { keywords: '服务|售后|支持|客服|运维|维护|保障服务', icon: 'support_agent' },

  // ── 用户/客户 ──
  { keywords: '用户|客户|消费者|会员|粉丝|流量|DAU|MAU|留存|活跃', icon: 'groups' },
  { keywords: '体验|满意度|NPS|口碑|评价|反馈|好评|推荐', icon: 'thumb_up' },

  // ── 市场/竞争 ──
  { keywords: '市场|行业|份额|占有率|规模|赛道|垂直|领域', icon: 'pie_chart' },
  { keywords: '竞争|对手|竞品|差异化|壁垒|护城河|优势|领先', icon: 'swords' },

  // ── 合作/生态 ──
  { keywords: '合作|协作|伙伴|生态|联盟|共赢|协同|联动|配合|搭档', icon: 'handshake' },
  { keywords: '平台|连接|桥梁|打通|整合|集成|汇聚|融合', icon: 'hub' },

  // ── 品牌/营销 ──
  { keywords: '品牌|形象|IP|知名度|声誉|影响力|声量|曝光|传播', icon: 'campaign' },
  { keywords: '营销|推广|广告|促销|活动|拉新|获客|转化|增长黑客', icon: 'ads_click' },

  // ── 组织/管理 ──
  { keywords: '管理|治理|制度|流程|规范|标准|体系|机制|框架|架构', icon: 'account_tree' },
  { keywords: '团队|组织|人力|人才|招聘|培训|文化|价值观|使命', icon: 'diversity_3' },
  { keywords: '目标|OKR|KPI|规划|战略|路线图|蓝图|愿景|方向', icon: 'target' },

  // ── 能源/环境 ──
  { keywords: '能源|电池|续航|充电|电动|新能源|光伏|风电|氢能|储能|电力|绿色|清洁', icon: 'bolt' },
  { keywords: '环保|低碳|碳中和|减排|节能|可持续|循环|回收|降解|绿色', icon: 'eco' },

  // ── 制造/供应链 ──
  { keywords: '制造|生产|工厂|产线|车间|工艺|加工|装配|产能|量产', icon: 'factory' },
  { keywords: '供应链|物流|仓储|配送|运输|快递|货运|干线|城配|冷链', icon: 'local_shipping' },

  // ── 医疗/健康 ──
  { keywords: '医疗|健康|医院|临床|诊断|治疗|药物|疫苗|患者|疾病|康复|护理', icon: 'local_hospital' },
  { keywords: '生物|基因|细胞|蛋白|分子|DNA|RNA|干细胞|免疫', icon: 'biotech' },

  // ── 教育/学习 ──
  { keywords: '教育|学习|教学|培训|课程|学生|教师|校园|学术|科研|论文', icon: 'school' },

  // ── 通信/网络 ──
  { keywords: '5G|通信|网络|连接|互联|物联网|IOT|云端|边缘计算|传输', icon: 'cloud_sync' },

  // ── 设计/美学 ──
  { keywords: '设计|美学|外观|造型|颜值|风格|艺术|时尚|潮流', icon: 'palette' },

  // ── 开始/启动 ──
  { keywords: '开始|启动|开启|出发|起航|起跑|开端|起点|序幕', icon: 'play_circle' },
  { keywords: '结束|完成|达成|收官|总结|结论|成果|收获|终点', icon: 'check_circle' },

  // ── 通用默认 ──
  { keywords: '方案|解决|能力|功能|特性|亮点|优势|价值|意义|作用|用途', icon: 'star' },
]

/** 缓存：已匹配过的文本 → 图标名 */
const matchCache = new Map()

/**
 * 根据中文文本自动匹配最合适的 Material Symbol 图标
 * @param {string} text - 中文文本（标题或正文）
 * @returns {string} Material Symbol 的 snake_case 图标名
 */
export function matchIcon(text) {
  if (!text || typeof text !== 'string') return 'circle'

  const key = text.slice(0, 40)
  if (matchCache.has(key)) return matchCache.get(key)

  for (const rule of ICON_RULES) {
    if (new RegExp(rule.keywords).test(text)) {
      matchCache.set(key, rule.icon)
      return rule.icon
    }
  }

  // 无匹配 → 默认图标
  matchCache.set(key, 'circle')
  return 'circle'
}

/**
 * 为要点/卡片数组批量匹配图标
 * @param {Array<{text?: string, title?: string, body?: string}>} items
 * @returns {Array} 带 icon 字段的新数组
 */
export function assignIcons(items) {
  if (!Array.isArray(items)) return []
  return items.map((item) => ({
    ...item,
    icon: matchIcon((item.text || item.title || item.body || '')),
  }))
}

/**
 * 清除匹配缓存（调试用）
 */
export function clearIconCache() {
  matchCache.clear()
}
