import { createRouter, createWebHistory } from 'vue-router'
import { useAuth, tryRememberLogin } from '../composables/useAuth'

const routes = [
  { path: '/login', name: 'login', component: () => import('../views/Login.vue'), meta: { title: '登录', public: true } },
  {
    path: '/',
    name: 'home',
    redirect: () => {
      const { isLoggedIn, user } = useAuth()
      if (!isLoggedIn.value) return { name: 'login' }
      return user.value?.is_admin ? { name: 'admin' } : { name: 'templates' }
    },
  },
  { path: '/templates', name: 'templates', component: () => import('../views/Templates.vue'), meta: { title: '探索模板', requiresAuth: true } },
  { path: '/dashboard', name: 'dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '我的项目', requiresAuth: true } },
  { path: '/create', name: 'create', component: () => import('../views/Create.vue'), meta: { title: '新建演示', requiresAuth: true } },
  { path: '/editor/:id', name: 'editor', component: () => import('../views/EditorStudio.vue'), meta: { title: '编辑器', requiresAuth: true } },
  { path: '/upgrade', name: 'upgrade', component: () => import('../views/Upgrade.vue'), meta: { title: '套餐升级', requiresAuth: true } },
  { path: '/help', name: 'help', component: () => import('../views/Help.vue'), meta: { title: '使用帮助', requiresAuth: true } },
  { path: '/publish/:id', name: 'publish', component: () => import('../views/PublishSuccess.vue'), meta: { title: '发布成功', requiresAuth: true } },
  { path: '/preview/:id', name: 'preview', component: () => import('../views/Preview.vue'), meta: { title: '演示预览', requiresAuth: true } },
  { path: '/admin', name: 'admin', component: () => import('../views/admin/AdminDashboard.vue'), meta: { title: '管理仪表盘', requiresAuth: true, admin: true } },
  { path: '/admin/users', name: 'admin-users', component: () => import('../views/admin/AdminUsers.vue'), meta: { title: '用户管理', requiresAuth: true, admin: true } },
  { path: '/admin/templates', name: 'admin-templates', component: () => import('../views/admin/AdminTemplates.vue'), meta: { title: 'H5 模板管理', requiresAuth: true, admin: true } },
  { path: '/admin/layouts', name: 'admin-layouts', component: () => import('../views/admin/AdminLayouts.vue'), meta: { title: '版式管理', requiresAuth: true, admin: true } },
  { path: '/admin/prompts', name: 'admin-prompts', component: () => import('../views/admin/AdminPrompts.vue'), meta: { title: '文稿提示词', requiresAuth: true, admin: true } },
  { path: '/admin/image-prompts', name: 'admin-image-prompts', component: () => import('../views/admin/AdminImagePrompts.vue'), meta: { title: '生图提示词', requiresAuth: true, admin: true } },
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

/** 确保已登录；未登录时仅在有「记住密码」时尝试静默登录 */
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

  // 公开页：分享
  if (to.meta.public) return

  // 登录页
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
      return { name: 'templates' }
    }
    return
  }

  // 所有受保护路由（含 /admin、/editor 等）
  const authed = await ensureAuthenticated()
  if (!authed) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.admin && !user.value?.is_admin) {
    return { name: 'templates' }
  }
})

router.afterEach((to) => {
  document.title = `${to.meta.title || '页面'} · AI智能H5演示平台`
  if (to.meta.requiresAuth || to.meta.admin) {
    fetch('/api/v1/统计/访问', { method: 'POST' }).catch(() => {})
  }
})

export default router
