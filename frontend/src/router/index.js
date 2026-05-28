import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const routes = [
  { path: '/login', name: 'login', component: () => import('../views/Login.vue'), meta: { title: '登录', public: true } },
  { path: '/', redirect: '/templates' },
  { path: '/templates', name: 'templates', component: () => import('../views/Templates.vue'), meta: { title: '探索模板' } },
  { path: '/create', name: 'create', component: () => import('../views/Create.vue'), meta: { title: 'AI 创建' } },
  { path: '/editor/:id', name: 'editor', component: () => import('../views/EditorStudio.vue'), meta: { title: '编辑器' } },
  { path: '/upgrade', name: 'upgrade', component: () => import('../views/Upgrade.vue'), meta: { title: '套餐升级' } },
  { path: '/publish/:id', name: 'publish', component: () => import('../views/PublishSuccess.vue'), meta: { title: '发布成功' } },
  { path: '/preview/:id', name: 'preview', component: () => import('../views/Preview.vue'), meta: { title: '演示预览' } },
  { path: '/settings', name: 'settings', component: () => import('../views/Settings.vue'), meta: { title: '系统设置' } },
  { path: '/s/:slug', name: 'share', component: () => import('../views/Share.vue'), meta: { title: '分享预览', public: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const { isLoggedIn } = useAuth()
  if (!to.meta.public && !isLoggedIn.value) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.name === 'login' && isLoggedIn.value) {
    return { name: 'templates' }
  }
})

router.afterEach((to) => {
  document.title = `${to.meta.title || '页面'} · AI智能H5演示平台`
})

export default router
