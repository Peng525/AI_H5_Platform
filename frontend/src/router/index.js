import { createRouter, createWebHistory } from 'vue-router'
import { useAuth, tryRememberLogin } from '../composables/useAuth'
import { canAccessGenerateResult } from '../composables/useAiCreateDraft.js'
import { api } from '../api/client.js'

const PROJECT_PUBLIC_ID_ROUTE_NAMES = new Set(['editor', 'preview', 'publish', 'ai-generate-result'])

const routes = [
  { path: '/login', name: 'login', component: () => import('../views/Login.vue'), meta: { title: '登录', public: true } },
  {
    path: '/',
    component: () => import('../components/WorkbenchShell.vue'),
    meta: { requiresAuth: true, workbench: true },
    children: [
      {
        path: '',
        name: 'home',
        redirect: () => {
          const { user } = useAuth()
          return user.value?.is_admin ? { name: 'admin' } : { name: 'ai-generate-start' }
        },
      },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '首页', workbenchSection: 'home' },
      },
      {
        path: 'templates',
        name: 'templates',
        component: () => import('../views/Templates.vue'),
        meta: { title: '模板库', workbenchSection: 'templates' },
      },
    ],
  },
  { path: '/create', redirect: '/create/generate' },
  { path: '/create/generate', name: 'ai-generate-start', component: () => import('../views/create/AiGenerateStart.vue'), meta: { title: '生成', requiresAuth: true } },
  { path: '/create/generate/prompt', redirect: '/create/generate' },
  { path: '/create/generate/review', name: 'ai-generate-review', component: () => import('../views/create/AiGenerateReview.vue'), meta: { title: '提示编辑器', requiresAuth: true } },
  { path: '/create/generate/result/:publicId', name: 'ai-generate-result', component: () => import('../views/create/AiGenerateResult.vue'), meta: { title: '生成结果', requiresAuth: true, requiresGenerateResult: true } },
  { path: '/create/generate/image', name: 'ai-generate-image', component: () => import('../views/create/AiGenerateImage.vue'), meta: { title: '生成图片', requiresAuth: true } },
  { path: '/create/blank', redirect: '/create/generate' },
  { path: '/editor/:publicId', name: 'editor', component: () => import('../views/EditorStudio.vue'), meta: { title: '编辑器', requiresAuth: true } },
  { path: '/upgrade', name: 'upgrade', component: () => import('../views/Upgrade.vue'), meta: { title: '套餐升级', requiresAuth: true } },
  { path: '/help', name: 'help', component: () => import('../views/Help.vue'), meta: { title: '使用帮助', requiresAuth: true } },
  { path: '/publish/:publicId', name: 'publish', component: () => import('../views/PublishSuccess.vue'), meta: { title: '发布成功', requiresAuth: true } },
  { path: '/preview/:publicId', name: 'preview', component: () => import('../views/Preview.vue'), meta: { title: '演示预览', requiresAuth: true } },
  { path: '/admin', name: 'admin', component: () => import('../views/admin/AdminDashboard.vue'), meta: { title: '管理仪表盘', requiresAuth: true, admin: true } },
  { path: '/admin/users', name: 'admin-users', component: () => import('../views/admin/AdminUsers.vue'), meta: { title: '用户管理', requiresAuth: true, admin: true } },
  { path: '/admin/templates', name: 'admin-templates', component: () => import('../views/admin/AdminTemplates.vue'), meta: { title: 'H5 模板管理', requiresAuth: true, admin: true } },
  { path: '/admin/layouts', name: 'admin-layouts', component: () => import('../views/admin/AdminLayouts.vue'), meta: { title: '版式管理', requiresAuth: true, admin: true } },
  { path: '/admin/prompts', name: 'admin-prompts', component: () => import('../views/admin/AdminPrompts.vue'), meta: { title: '文稿提示词', requiresAuth: true, admin: true } },
  { path: '/admin/image-prompts', name: 'admin-image-prompts', component: () => import('../views/admin/AdminImagePrompts.vue'), meta: { title: '生图提示词', requiresAuth: true, admin: true } },
  { path: '/admin/deck-prompts', name: 'admin-deck-prompts', component: () => import('../views/admin/AdminDeckPrompts.vue'), meta: { title: '演示提示词', requiresAuth: true, admin: true } },
  { path: '/settings', name: 'settings', component: () => import('../views/Settings.vue'), meta: { title: '系统设置', requiresAuth: true, admin: true } },
  { path: '/s/:slug', name: 'share', component: () => import('../views/Share.vue'), meta: { title: '分享预览', public: true } },
  { path: '/:pathMatch(.*)*', redirect: { name: 'login' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

async function waitAuthReady() {
  const { authReady } = useAuth()
  if (authReady.value) return
  await new Promise((resolve) => {
    const timer = setInterval(() => {
      if (authReady.value) {
        clearInterval(timer)
        resolve()
      }
    }, 10)
  })
}

async function ensureAuthenticated() {
  const { isLoggedIn, refreshProfile, logout, getStoredToken } = useAuth()
  if (!isLoggedIn.value) {
    const ok = await tryRememberLogin()
    if (!ok) return false
  }
  const me = await refreshProfile()
  if (!me) {
    if (getStoredToken()) logout()
    return false
  }
  return true
}

router.beforeEach(async (to) => {
  await waitAuthReady()
  const { isLoggedIn, user } = useAuth()

  if (to.meta.public) return

  if (to.name === 'login') {
    if (to.query.from === 'logout') return
    if (isLoggedIn.value) {
      const ok = await ensureAuthenticated()
      if (!ok) return
      if (user.value?.is_admin) return { name: 'admin' }
      const redirect = to.query.redirect
      if (typeof redirect === 'string' && redirect.startsWith('/') && !redirect.startsWith('/admin')) {
        return redirect
      }
      return { name: 'ai-generate-start' }
    }
    return
  }

  const authed = await ensureAuthenticated()
  if (!authed) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.admin && !user.value?.is_admin) {
    return { name: 'ai-generate-start' }
  }

  if (PROJECT_PUBLIC_ID_ROUTE_NAMES.has(to.name)) {
    const ref = to.params.publicId
    if (ref && /^\d+$/.test(String(ref))) {
      try {
        const { public_id: publicId } = await api.resolveProjectRef(ref)
        if (publicId && publicId !== ref) {
          return { name: to.name, params: { ...to.params, publicId }, query: to.query, hash: to.hash, replace: true }
        }
      } catch {
        /* 无法解析则继续，由页面/API 报错 */
      }
    }
  }

  if (to.meta.requiresGenerateResult) {
    const publicId = to.params.publicId
    if (!publicId || !canAccessGenerateResult(publicId)) {
      return { name: 'ai-generate-review' }
    }
  }
})

router.afterEach((to) => {
  document.title = `${to.meta.title || '页面'} · AI智能H5演示平台`
  if (to.meta.requiresAuth || to.meta.admin || to.meta.workbench) {
    fetch('/api/v1/统计/访问', { method: 'POST' }).catch(() => {})
  }
})

export default router
