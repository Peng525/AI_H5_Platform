import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const routes = [
  { path: '/login', name: 'login', component: () => import('../views/Login.vue'), meta: { title: '登录', public: true } },
  { path: '/', redirect: '/templates' },
  { path: '/templates', name: 'templates', component: () => import('../views/Templates.vue'), meta: { title: '探索模板' } },
  { path: '/dashboard', name: 'dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '我的项目' } },
  { path: '/create', name: 'create', component: () => import('../views/Create.vue'), meta: { title: 'AI 创建' } },
  { path: '/editor/:id', name: 'editor', component: () => import('../views/EditorStudio.vue'), meta: { title: '编辑器' } },
  { path: '/upgrade', name: 'upgrade', component: () => import('../views/Upgrade.vue'), meta: { title: '套餐升级' } },
  { path: '/publish/:id', name: 'publish', component: () => import('../views/PublishSuccess.vue'), meta: { title: '发布成功' } },
  { path: '/preview/:id', name: 'preview', component: () => import('../views/Preview.vue'), meta: { title: '演示预览' } },
  { path: '/admin', name: 'admin', component: () => import('../views/admin/AdminDashboard.vue'), meta: { title: '管理仪表盘', admin: true } },
  { path: '/admin/users', name: 'admin-users', component: () => import('../views/admin/AdminUsers.vue'), meta: { title: '用户管理', admin: true } },
  { path: '/settings', name: 'settings', component: () => import('../views/Settings.vue'), meta: { title: '系统设置', admin: true } },
  { path: '/s/:slug', name: 'share', component: () => import('../views/Share.vue'), meta: { title: '分享预览', public: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const { isLoggedIn, user, refreshProfile } = useAuth()
  if (!to.meta.public && !isLoggedIn.value) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.name === 'login' && isLoggedIn.value) {
    if (user.value?.is_admin === undefined) await refreshProfile()
    if (user.value?.is_admin) return { name: 'admin' }
    return { name: 'templates' }
  }
  if (to.meta.admin) {
    if (user.value?.is_admin === undefined && isLoggedIn.value) {
      await refreshProfile()
    }
    if (!user.value?.is_admin) {
      return { name: 'templates' }
    }
  }
})

router.afterEach((to) => {
  document.title = `${to.meta.title || '页面'} · AI智能H5演示平台`
  if (!to.meta.public && to.name !== 'login') {
    fetch('/api/v1/统计/访问', { method: 'POST' }).catch(() => {})
  }
})

export default router
