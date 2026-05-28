import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Create from '../views/Create.vue'
import Editor from '../views/Editor.vue'
import Preview from '../views/Preview.vue'
import Settings from '../views/Settings.vue'
import Share from '../views/Share.vue'

const routes = [
  { path: '/', name: 'dashboard', component: Dashboard, meta: { title: '项目列表' } },
  { path: '/create', name: 'create', component: Create, meta: { title: 'AI 创建' } },
  { path: '/editor/:id', name: 'editor', component: Editor, meta: { title: '编辑器' } },
  { path: '/preview/:id', name: 'preview', component: Preview, meta: { title: '演示预览' } },
  { path: '/settings', name: 'settings', component: Settings, meta: { title: '系统设置' } },
  { path: '/s/:slug', name: 'share', component: Share, meta: { title: '分享预览' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach((to) => {
  document.title = `${to.meta.title || '页面'} · AI智能H5演示平台`
})

export default router
