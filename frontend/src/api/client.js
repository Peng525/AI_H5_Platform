import { useAuth } from '../composables/useAuth'

const BASE = ''

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
    const { logout } = useAuth()
    logout()
    const redirect = encodeURIComponent(window.location.pathname + window.location.search)
    window.location.replace(`/login?redirect=${redirect}`)
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
  login: (body) => request('/api/v1/认证/登录', { method: 'POST', body: JSON.stringify(body) }),
  register: (body) => request('/api/v1/认证/注册', { method: 'POST', body: JSON.stringify(body) }),
  getQuota: (userId) => request(`/api/v1/认证/配额?user_id=${userId || 1}`),
  getTemplateCategories: () => request('/api/v1/模板库/分类'),
  listTemplates: (category = '全部', q = '') =>
    request(`/api/v1/模板库?category=${encodeURIComponent(category)}&q=${encodeURIComponent(q)}`),
  getPlans: () => request('/api/v1/模板库/套餐'),
  listProjects: () => request('/api/v1/项目'),
  createProject: (body, userId) =>
    request(`/api/v1/项目${userId ? `?user_id=${userId}` : ''}`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  getProject: (id) => request(`/api/v1/项目/${id}`),
  updateProject: (id, body) =>
    request(`/api/v1/项目/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  updateSlide: (projectId, slideId, body) =>
    request(`/api/v1/项目/${projectId}/页面/${slideId}`, {
      method: 'PUT',
      body: JSON.stringify(body),
    }),
  deleteProject: (id) => request(`/api/v1/项目/${id}`, { method: 'DELETE' }),
  generateFull: (id, body, userId) =>
    request(`/api/v1/项目/${id}/生成/全量${userId ? `?user_id=${userId}` : ''}`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  generatePage: (id, slideId, body, userId) =>
    request(`/api/v1/项目/${id}/页面/${slideId}/生成/单页${userId ? `?user_id=${userId}` : ''}`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  addSlide: (projectId, body) =>
    request(`/api/v1/项目/${projectId}/页面`, { method: 'POST', body: JSON.stringify(body) }),
  deleteSlide: (projectId, slideId) =>
    request(`/api/v1/项目/${projectId}/页面/${slideId}`, { method: 'DELETE' }),
  getPromptTemplates: () => request('/api/v1/设置/模板列表'),
  getLlmSettings: () => request('/api/v1/设置/大模型'),
  updateLlmSettings: (body) =>
    request('/api/v1/设置/大模型', { method: 'PUT', body: JSON.stringify(body) }),
  getMe: () => request('/api/v1/认证/我'),
  recordVisit: () => request('/api/v1/统计/访问', { method: 'POST' }),
  createOrder: (body) => request('/api/v1/订单/创建', { method: 'POST', body: JSON.stringify(body) }),
  getAdminDashboard: () => request('/api/v1/管理/仪表盘'),
  listAdminOrders: () => request('/api/v1/管理/订单'),
  listAdminUsers: (q = '') => request(`/api/v1/管理/用户?q=${encodeURIComponent(q)}`),
  createAdminUser: (body) => request('/api/v1/管理/用户', { method: 'POST', body: JSON.stringify(body) }),
  updateAdminUser: (id, body) => request(`/api/v1/管理/用户/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
  testLlm: (channel, tier = 'free') => {
    const q = new URLSearchParams()
    if (channel) q.set('channel', channel)
    if (tier) q.set('tier', tier)
    const qs = q.toString()
    return request(`/api/v1/设置/大模型/测试${qs ? `?${qs}` : ''}`, { method: 'POST' })
  },
  sharePreview: (slug) => request(`/api/v1/分享/${slug}`),
}
