/**
 * 从版式块生成完整模板 slides_json（供 Node 脚本写入 backend/data/h5_templates）
 */
import { buildBlock, getDefaultBlockBackground, resetLayoutBlockIds } from './layoutBlocks.js'

function slide(title, layout, blockId, viewportId, themeId, copy = {}, animation = 'fade') {
  resetLayoutBlockIds()
  return {
    title,
    subtitle: '',
    layout,
    animation,
    canvas_background: getDefaultBlockBackground(themeId),
    canvas_elements: buildBlock(blockId, viewportId, themeId, copy),
    bullets: [],
  }
}

export function buildMinimalZjySlides(viewportId, themeId = 'zjy-minimal') {
  const web = viewportId.startsWith('web')
  return [
    slide('封面', 'cover', 'cover-minimal', viewportId, themeId, {
      title: web ? '年度工作汇报' : '工作汇报',
      subtitle: '简约 · 专业 · 清晰',
    }, 'fade'),
    slide('目录', 'title', 'section-title', viewportId, themeId, {
      title: '今日议程',
      body: '用三个章节，讲清核心成果与下一步计划。',
    }, 'slide-up'),
    slide('要点一', 'bullets', 'bullets-three', viewportId, themeId, {
      title: '核心成果',
      items: ['目标达成率超出预期', '关键指标稳步提升', '团队协作效率提高'],
    }, 'fade'),
    slide('对比', 'bullets', 'two-column', viewportId, themeId, {
      leftTitle: '现状',
      leftBody: '流程清晰，交付稳定，客户反馈积极。',
      rightTitle: '目标',
      rightBody: '持续优化体验，扩大服务覆盖范围。',
    }, 'slide-up'),
    slide('数据', 'bullets', 'stat-highlight', viewportId, themeId, {
      stat: '128%',
      desc: '年度核心 KPI 完成率',
    }, 'fade'),
    slide('引用', 'title', 'quote-center', viewportId, themeId, {
      quote: '「把复杂的事情做简单，把简单的事做到位。」',
      author: '— 团队共识',
    }, 'slide-up'),
    slide('流程', 'bullets', 'steps-horizontal', viewportId, themeId, {
      title: '推进路径',
      steps: ['调研分析', '方案落地', '复盘迭代'],
    }, 'fade'),
    slide('小结', 'bullets', 'bullets-three', viewportId, themeId, {
      title: '下一步',
      items: ['巩固现有成果', '拓展重点场景', '建立长效机制'],
    }, 'slide-up'),
    slide('致谢', 'cover', 'closing-minimal', viewportId, themeId, {
      title: '谢谢',
      contact: '欢迎交流 · contact@company.com',
    }, 'fade'),
  ]
}

export function buildStoryVolunteerSlides(viewportId, themeId = 'eqxiu-story') {
  const anims = ['fade', 'slide-up', 'fade', 'slide-up', 'fade', 'slide-up', 'fade', 'slide-up', 'fade', 'slide-up']
  const specs = [
    ['封面', 'cover', 'story-cover', { title: '广州大学生志愿服务的烦恼', subtitle: '一份关于期待与现实的叙事' }],
    ['提问', 'title', 'question-hook', { question: '他们期待什么样的志愿服务？', hint: '点击继续 ↓' }],
    ['期待', 'bullets', 'icon-list-four', {
      title: '四项期待',
      items: [
        { icon: 'school', text: '技能提升' },
        { icon: 'favorite', text: '有意义的体验' },
        { icon: 'emoji_objects', text: '有趣有挑战' },
        { icon: 'groups', text: '组织靠谱、沟通顺畅' },
      ],
    }],
    ['烦恼', 'bullets', 'icon-list-four', {
      title: '四项烦恼',
      items: [
        { icon: 'schedule', text: '时间冲突难协调' },
        { icon: 'help', text: '培训不足难上手' },
        { icon: 'sentiment_dissatisfied', text: '活动形式单一' },
        { icon: 'link_off', text: '反馈慢、体验差' },
      ],
    }],
    ['数据', 'bullets', 'big-stat-one', { stat: '73%', desc: '大学生希望志愿服务带来真实成长' }],
    ['案例', 'title', 'case-card', {
      title: '案例：校园志愿周',
      body: '通过线上招募与分层培训，参与人数提升 2 倍，满意度显著提高。',
    }],
    ['价值', 'bullets', 'values-four', { title: '志愿精神', values: ['奉献', '友爱', '互助', '进步'] }],
    ['小结', 'title', 'section-title', { title: '我们可以做什么', body: '从组织方、高校与学生三方协同，改善志愿体验。' }],
    ['行动', 'bullets', 'bullets-three', {
      title: '三条建议',
      items: ['设计有挑战的任务包', '建立透明沟通机制', '用数据衡量活动成效'],
    }],
    ['致谢', 'cover', 'closing-minimal', { title: '谢谢观看', contact: '欢迎加入志愿者行列' }],
  ]
  return specs.map(([title, layout, blockId, copy], i) =>
    slide(title, layout, blockId, viewportId, themeId, copy, anims[i] || 'fade')
  )
}

export function buildTechLaunchSlides(viewportId, themeId = 'zjy-minimal') {
  return [
    slide('发布', 'cover', 'cover-minimal', viewportId, themeId, { title: '产品发布', subtitle: '极简科技 · 聚焦核心价值' }, 'fade'),
    slide('痛点', 'title', 'section-title', viewportId, themeId, { title: '用户真正需要什么', body: '从场景出发，解决最关键的问题。' }, 'slide-up'),
    slide('特性', 'bullets', 'bullets-three', viewportId, themeId, {
      title: '三大特性',
      items: ['更快：秒级响应', '更稳：企业级可靠', '更易用：零学习成本'],
    }, 'fade'),
    slide('对比', 'bullets', 'two-column', viewportId, themeId, {
      leftTitle: '传统方案',
      leftBody: '复杂、昂贵、部署周期长。',
      rightTitle: '我们的方案',
      rightBody: '轻量、灵活、即开即用。',
    }, 'slide-up'),
    slide('数据', 'bullets', 'stat-highlight', viewportId, themeId, { stat: '10×', desc: '效率提升（内测数据）' }, 'fade'),
    slide('流程', 'bullets', 'steps-horizontal', viewportId, themeId, {
      title: '如何开始',
      steps: ['注册账号', '选择模板', '一键发布'],
    }, 'slide-up'),
    slide('引用', 'title', 'quote-center', viewportId, themeId, {
      quote: '「好的产品，让用户忘记产品本身。」',
      author: '— 产品理念',
    }, 'fade'),
    slide('致谢', 'cover', 'closing-minimal', viewportId, themeId, { title: '立即体验', contact: 'www.example.com' }, 'slide-up'),
  ]
}

export function buildCorpIntroSlides(viewportId, themeId = 'zjy-minimal') {
  return [
    slide('封面', 'cover', 'cover-minimal', viewportId, themeId, { title: '企业品牌介绍', subtitle: '专业 · 可信 · 长期主义' }, 'fade'),
    slide('关于', 'title', 'section-title', viewportId, themeId, { title: '我们是谁', body: '专注为客户创造可持续价值的团队。' }, 'slide-up'),
    slide('业务', 'bullets', 'bullets-three', viewportId, themeId, {
      title: '核心业务',
      items: ['数字化解决方案', '行业咨询与交付', '持续运营支持'],
    }, 'fade'),
    slide('优势', 'bullets', 'two-column', viewportId, themeId, {
      leftTitle: '我们的优势',
      leftBody: '深度行业理解 + 成熟方法论。',
      rightTitle: '客户价值',
      rightBody: '降本增效，提升品牌与体验。',
    }, 'slide-up'),
    slide('数据', 'bullets', 'stat-highlight', viewportId, themeId, { stat: '500+', desc: '服务客户（示例数据）' }, 'fade'),
    slide('案例', 'title', 'case-card', viewportId, themeId, {
      title: '标杆案例',
      body: '助力某行业客户完成数字化升级，项目按期交付并获得持续合作。',
    }, 'slide-up'),
    slide('文化', 'bullets', 'values-four', viewportId, themeId, {
      title: '价值观',
      values: ['诚信', '创新', '协作', '共赢'],
    }, 'fade'),
    slide('联系', 'cover', 'closing-minimal', viewportId, themeId, {
      title: '期待合作',
      contact: 'hello@company.com',
    }, 'slide-up'),
  ]
}

export function templateMeta(id, title, description, category, device, viewportId, themeId, slides, extraSettings = {}) {
  return {
    id,
    title,
    description,
    category,
    device,
    pages: slides.length,
    premium: false,
    featured: true,
    cover_gradient: themeId === 'eqxiu-story' ? 'from-orange-100 to-teal-100' : 'from-slate-50 to-teal-100',
    default_viewport: viewportId,
    settings_json: {
      viewportId,
      scrollEffect: themeId === 'eqxiu-story' ? 'vertical' : 'page',
      themeId,
      showScrollHint: themeId === 'eqxiu-story',
      defaultChatTapToContinue: true,
      bgm: {
        enabled: false,
        trackId: '',
        url: '',
        loop: true,
        volume: themeId === 'eqxiu-story' ? 0.32 : 0.35,
      },
      ...extraSettings,
    },
    slides_json: slides,
  }
}
