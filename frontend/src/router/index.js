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
      if (user.value?.is_admin) return { name: 'admin' }
      return { name: 'templates' }
    },
  },
  { path: '/templates', name: 'templates', component: () => import('../views/Templates.vue'), meta: { title: '探索模板', requiresAuth: true } },
  { path: '/dashboard', name: 'dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '我的项目', requiresAuth: true } },
  { path: '/create', name: 'create', component: () => import('../views/Create.vue'), meta: { title: 'AI 创建', requiresAuth: true } },
  { path: '/editor/:id', name: 'editor', component: () => import('../views/EditorStudio.vue'), meta: { title: '编辑器', requiresAuth: true } },
  { path: '/upgrade', name: 'upgrade', component: () => import('../views/Upgrade.vue'), meta: { title: '套餐升级', requiresAuth: true } },
  { path: '/publish/:id', name: 'publish', component: () => import('../views/PublishSuccess.vue'), meta: { title: '发布成功', requiresAuth: true } },
  { path: '/preview/:id', name: 'preview', component: () => import('../views/Preview.vue'), meta: { title: '演示预览', requiresAuth: true } },
  { path: '/admin', name: 'admin', component: () => import('../views/admin/AdminDashboard.vue'), meta: { title: '管理仪表盘', requiresAuth: true, admin: true } },
  { path: '/admin/users', name: 'admin-users', component: () => import('../views/admin/AdminUsers.vue'), meta: { title: '用户管理', requiresAuth: true, admin: true } },
  { path: '/settings', name: 'settings', component: () => import('../views/Settings.vue'), meta: { title: '系统设置', requiresAuth: true, admin: true } },
  { path: '/s/:slug', name: 'share', component: () => import('../views/Share.vue'), meta: { title: '分享预览', public: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const { isLoggedIn, user, authReady, refreshProfile, logout } = useAuth()

  if (!authReady.value) {
    await new Promise((resolve) => {
      const timer = setInterval(() => {
        if (authReady.value) {
          clearInterval(timer)
          resolve()
        }
      }, 10)
    })
  }

  const needsAuth = to.meta.requiresAuth || to.meta.admin

  if (needsAuth && !isLoggedIn.value) {
    const remembered = await tryRememberLogin()
    if (!remembered) {
      return { name: 'login', query: { redirect: to.fullPath } }
    }
  }

  if (needsAuth && isLoggedIn.value) {
    const me = await refreshProfile()
    if (!me) {
      logout()
      return { name: 'login', query: { redirect: to.fullPath } }
    }
  }

  if (to.name === 'login') {
    // 主动退出后必须停留在登录页，不自动跳走
    if (to.query.from === 'logout') {
      return
    }
    if (isLoggedIn.value) {
      if (user.value?.is_admin === undefined) await refreshProfile()
      if (user.value?.is_admin) return { name: 'admin' }
      const redirect = to.query.redirect
      if (typeof redirect === 'string' && redirect.startsWith('/') && !redirect.startsWith('/admin')) {
        return redirect
      }
      return { name: 'templates' }
    }
  }

  if (to.meta.admin) {
    if (user.value?.is_admin === undefined && isLoggedIn.value) {
      await refreshProfile()
    }
    if (!user.value?.is_admin) {
      return { name: 'login', query: { redirect: to.fullPath } }
    }
  }
})

router.afterEach((to) => {
  document.title = `${to.meta.title || '页面'} · AI智能H5演示平台`
  if (to.meta.requiresAuth || to.meta.admin) {
    fetch('/api/v1/统计/访问', { method: 'POST' }).catch(() => {})
  }
})

export default router
