import { useAuth } from '../composables/useAuth'

const BASE = ''

let authRedirectPending = false

function redirectToLogin() {
  if (authRedirectPending) return
  if (window.location.pathname.startsWith('/login')) return
  authRedirectPending = true
  const { logout } = useAuth()
  logout()
  const redirect = encodeURIComponent(window.location.pathname + window.location.search)
  window.location.replace(`/login?redirect=${redirect}`)
}

async function request(path, options = {}) {
  const { authHeaders } = useAuth()
  const res = await fetch(`${BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(),
      ...(options.headers || {}),
    },
    ...options,
  })
  const data = await res.json().catch(() => ({}))
  if (res.status === 401 && !path.includes('/认证/')) {
    redirectToLogin()
    throw new Error('登录已过期，请重新登录')
  }
  if (!res.ok) {
    let detail = data.detail ?? data.message
    if (Array.isArray(detail)) {
      detail = detail.map((d) => d.msg || JSON.stringify(d)).join('；')
    }
    throw new Error(detail || `请求失败 (${res.status})`)
  }
  return data
}

async function uploadForm(path, formData) {
  const { authHeaders } = useAuth()
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { ...authHeaders() },
    body: formData,
  })
  const data = await res.json().catch(() => ({}))
  if (res.status === 401) {
    redirectToLogin()
    throw new Error('登录已过期，请重新登录')
  }
  if (!res.ok) {
    let detail = data.detail ?? data.message
    if (Array.isArray(detail)) {
      detail = detail.map((d) => d.msg || JSON.stringify(d)).join('；')
    }
    throw new Error(detail || `请求失败 (${res.status})`)
  }
  return data
}

export const api = {
  health: () => request('/api/v1/健康'),
  listBgmTracks: () => request('/api/v1/bgm/曲目'),
  getCaptchaConfig: () => request('/api/v1/认证/验证码/配置'),
  sendSmsCode: (body) =>
    request('/api/v1/认证/验证码/发送', { method: 'POST', body: JSON.stringify(body) }),
  login: (body) => request('/api/v1/认证/登录', { method: 'POST', body: JSON.stringify(body) }),
  register: (body) => request('/api/v1/认证/注册', { method: 'POST', body: JSON.stringify(body) }),
  getQuota: () => request('/api/v1/认证/配额'),
  getTemplateCategories: () => request('/api/v1/模板库/分类'),
  listTemplates: (category = '全部', q = '', device = '全部') => {
    const params = new URLSearchParams()
    params.set('category', category)
    params.set('q', q)
    if (device) params.set('device', device)
    return request(`/api/v1/模板库?${params.toString()}`)
  },
  previewTemplate: (id) => request(`/api/v1/模板库/${encodeURIComponent(id)}/预览`),
  getPlans: () => request('/api/v1/模板库/套餐'),
  quotePack: (quota) => request(`/api/v1/模板库/套餐/计价?quota=${quota}`),
  listProjects: () => request('/api/v1/项目'),
  createProject: (body) =>
    request('/api/v1/项目', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  getProject: (id) => request(`/api/v1/项目/${id}`),
  updateProjectSettings: (id, body) =>
    request(`/api/v1/项目/${id}/设置`, { method: 'PUT', body: JSON.stringify(body) }),
  updateProject: (id, body) =>
    request(`/api/v1/项目/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  updateSlide: (projectId, slideId, body) =>
    request(`/api/v1/项目/${projectId}/页面/${slideId}`, {
      method: 'PUT',
      body: JSON.stringify(body),
    }),
  saveSlideCanvas: (projectId, slideId, elements) =>
    request(`/api/v1/项目/${projectId}/页面/${slideId}/画布`, {
      method: 'PUT',
      body: JSON.stringify({ elements }),
    }),
  deleteProject: (id) => request(`/api/v1/项目/${id}`, { method: 'DELETE' }),
  generateImage: (projectId, body) =>
    request(`/api/v1/项目/${projectId}/生成/配图`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  addSlide: (projectId, body) =>
    request(`/api/v1/项目/${projectId}/页面`, { method: 'POST', body: JSON.stringify(body) }),
  deleteSlide: (projectId, slideId) =>
    request(`/api/v1/项目/${projectId}/页面/${slideId}`, { method: 'DELETE' }),
  getPromptTemplates: () => request('/api/v1/设置/模板列表'),
  getPromptTemplate: (id) => request(`/api/v1/设置/提示词模板/${encodeURIComponent(id)}`),
  createPromptTemplate: (body) =>
    request('/api/v1/设置/提示词模板', { method: 'POST', body: JSON.stringify(body) }),
  updatePromptTemplate: (id, body) =>
    request(`/api/v1/设置/提示词模板/${encodeURIComponent(id)}`, {
      method: 'PUT',
      body: JSON.stringify(body),
    }),
  deletePromptTemplate: (id) =>
    request(`/api/v1/设置/提示词模板/${encodeURIComponent(id)}`, { method: 'DELETE' }),
  getLlmSettings: () => request('/api/v1/设置/大模型'),
  updateLlmSettings: (body) =>
    request('/api/v1/设置/大模型', { method: 'PUT', body: JSON.stringify(body) }),
  getMe: () => request('/api/v1/认证/我'),
  recordVisit: () => request('/api/v1/统计/访问', { method: 'POST' }),
  createOrder: (body) => request('/api/v1/订单/创建', { method: 'POST', body: JSON.stringify(body) }),
  claimOrderPaid: (orderId, remark = '') =>
    request(`/api/v1/订单/${orderId}/申报已付`, {
      method: 'POST',
      body: JSON.stringify({ remark }),
    }),
  getWechatQrConfig: () => request('/api/v1/支付/微信收款码'),
  getOrder: (id) => request(`/api/v1/订单/${id}`),
  listOrders: () => request('/api/v1/订单'),
  getAdminDashboard: () => request('/api/v1/管理/仪表盘'),
  getRelayLink: () => request('/api/v1/管理/中转充值'),
  confirmAdminOrder: (id, admin_remark = '') =>
    request(`/api/v1/管理/订单/${id}/确认收款`, {
      method: 'POST',
      body: JSON.stringify({ admin_remark }),
    }),
  rejectAdminOrder: (id, admin_remark = '') =>
    request(`/api/v1/管理/订单/${id}/拒绝收款`, {
      method: 'POST',
      body: JSON.stringify({ admin_remark }),
    }),
  listAdminOrders: (params = {}) => {
    const q = new URLSearchParams()
    if (params.status) q.set('status', params.status)
    if (params.limit) q.set('limit', String(params.limit))
    const qs = q.toString()
    return request(`/api/v1/管理/订单${qs ? `?${qs}` : ''}`)
  },
  deleteExpiredAdminOrders: () => request('/api/v1/管理/订单/超时', { method: 'DELETE' }),
  listAdminUsers: (q = '') => request(`/api/v1/管理/用户?q=${encodeURIComponent(q)}`),
  createAdminUser: (body) => request('/api/v1/管理/用户', { method: 'POST', body: JSON.stringify(body) }),
  updateAdminUser: (id, body) => request(`/api/v1/管理/用户/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
  listAdminTemplates: () => request('/api/v1/管理/模板'),
  getAdminTemplate: (id) => request(`/api/v1/管理/模板/${encodeURIComponent(id)}`),
  createAdminTemplate: (body) => request('/api/v1/管理/模板', { method: 'POST', body: JSON.stringify(body) }),
  updateAdminTemplate: (id, body) =>
    request(`/api/v1/管理/模板/${encodeURIComponent(id)}`, { method: 'PUT', body: JSON.stringify(body) }),
  deleteAdminTemplate: (id) =>
    request(`/api/v1/管理/模板/${encodeURIComponent(id)}`, { method: 'DELETE' }),
  startTemplateDraft: (templateId) =>
    request(`/api/v1/管理/模板/${encodeURIComponent(templateId)}/编辑草稿`, { method: 'POST' }),
  quickCreateAdminTemplate: () => request('/api/v1/管理/模板/快速创建', { method: 'POST' }),
  saveTemplatePreset: (templateId, body) =>
    request(`/api/v1/管理/模板/${encodeURIComponent(templateId)}/保存预设`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  importPptxToTemplateDraft: (templateId, formData) =>
    uploadForm(`/api/v1/管理/模板/${encodeURIComponent(templateId)}/导入-pptx`, formData),
  parseAdminPptxTemplate: (formData) => uploadForm('/api/v1/管理/模板/解析-pptx', formData),
  importAdminPptxTemplate: (formData) => uploadForm('/api/v1/管理/模板/导入-pptx', formData),
  listLayoutBlocks: () => request('/api/v1/版式'),
  getLayoutBlock: (id) => request(`/api/v1/版式/${encodeURIComponent(id)}`),
  listAdminLayouts: () => request('/api/v1/管理/版式'),
  getAdminLayout: (id) => request(`/api/v1/管理/版式/${encodeURIComponent(id)}`),
  createAdminLayout: (body) => request('/api/v1/管理/版式', { method: 'POST', body: JSON.stringify(body) }),
  updateAdminLayout: (id, body) =>
    request(`/api/v1/管理/版式/${encodeURIComponent(id)}`, { method: 'PUT', body: JSON.stringify(body) }),
  deleteAdminLayout: (id) => request(`/api/v1/管理/版式/${encodeURIComponent(id)}`, { method: 'DELETE' }),
  listImagePromptTemplates: () => request('/api/v1/生图提示词'),
  listAdminImagePrompts: () => request('/api/v1/管理/生图提示词'),
  getAdminImagePrompt: (id) => request(`/api/v1/管理/生图提示词/${encodeURIComponent(id)}`),
  createAdminImagePrompt: (body) =>
    request('/api/v1/管理/生图提示词', { method: 'POST', body: JSON.stringify(body) }),
  updateAdminImagePrompt: (id, body) =>
    request(`/api/v1/管理/生图提示词/${encodeURIComponent(id)}`, { method: 'PUT', body: JSON.stringify(body) }),
  deleteAdminImagePrompt: (id) =>
    request(`/api/v1/管理/生图提示词/${encodeURIComponent(id)}`, { method: 'DELETE' }),
  testLlm: (channel, tier = 'free') => {
    const q = new URLSearchParams()
    if (channel) q.set('channel', channel)
    if (tier) q.set('tier', tier)
    const qs = q.toString()
    return request(`/api/v1/设置/大模型/测试${qs ? `?${qs}` : ''}`, { method: 'POST' })
  },
  sharePreview: (slug) => request(`/api/v1/分享/${slug}`),
}
