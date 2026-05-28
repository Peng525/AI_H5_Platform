const BASE = ''

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(data.detail || data.message || `请求失败 (${res.status})`)
  }
  return data
}

export const api = {
  health: () => request('/api/v1/健康'),
  listProjects: () => request('/api/v1/项目'),
  createProject: (body) => request('/api/v1/项目', { method: 'POST', body: JSON.stringify(body) }),
  getProject: (id) => request(`/api/v1/项目/${id}`),
  updateProject: (id, body) =>
    request(`/api/v1/项目/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  updateSlide: (projectId, slideId, body) =>
    request(`/api/v1/项目/${projectId}/页面/${slideId}`, {
      method: 'PUT',
      body: JSON.stringify(body),
    }),
  deleteProject: (id) => request(`/api/v1/项目/${id}`, { method: 'DELETE' }),
  generateFull: (id, body) =>
    request(`/api/v1/项目/${id}/生成/全量`, { method: 'POST', body: JSON.stringify(body) }),
  generatePage: (id, slideId, body) =>
    request(`/api/v1/项目/${id}/页面/${slideId}/生成/单页`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  getLlmSettings: () => request('/api/v1/设置/大模型'),
  testLlm: (channel, tier = 'free') => {
    const q = new URLSearchParams()
    if (channel) q.set('channel', channel)
    if (tier) q.set('tier', tier)
    const qs = q.toString()
    return request(`/api/v1/设置/大模型/测试${qs ? `?${qs}` : ''}`, { method: 'POST' })
  },
  getTemplates: () => request('/api/v1/模板'),
  sharePreview: (slug) => request(`/api/v1/分享/${slug}`),
}
