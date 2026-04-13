import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth.js'

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    // ── Splash ────────────────────────────────────────────
    { path: '/splash', name: 'splash', component: () => import('@/views/SplashView.vue'), meta: { title: '欢迎' } },

    // ── Public ────────────────────────────────────────────
    {
      path: '/',
      component: () => import('@/layouts/PublicLayout.vue'),
      children: [
        { path: '',           name: 'home',           component: () => import('@/views/public/HomeView.vue'),      meta: { title: '首页' } },
        { path: 'articles',   name: 'articles',       component: () => import('@/views/public/ArticlesView.vue'),  meta: { title: '文章' } },
        { path: 'articles/:slug', name: 'article-detail', component: () => import('@/views/public/ArticleDetail.vue'), meta: { title: '文章详情' } },
        { path: 'projects',   name: 'projects',       component: () => import('@/views/public/ProjectsView.vue'),  meta: { title: '项目' } },
        { path: 'playground', name: 'playground',     component: () => import('@/views/public/PlaygroundView.vue'), meta: { title: '代码运行' } },
        { path: 'community',  name: 'community',     component: () => import('@/views/CommunityActivities.vue'),  meta: { title: '社区活动' } },
      ],
    },

    // ── Login ─────────────────────────────────────────────
    { path: '/login', name: 'login', component: () => import('@/views/admin/LoginView.vue'), meta: { title: '登录' } },

    // ── Admin ─────────────────────────────────────────────
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '',           redirect: '/admin/dashboard' },
        { path: 'dashboard',  name: 'admin-dashboard', component: () => import('@/views/admin/DashboardView.vue'),  meta: { title: '概览' } },
        { path: 'profile',    name: 'admin-profile',   component: () => import('@/views/admin/ProfileEditor.vue'),  meta: { title: '个人资料' } },
        { path: 'articles',   name: 'admin-articles',  component: () => import('@/views/admin/ArticleManager.vue'), meta: { title: '文章管理' } },
        { path: 'projects',   name: 'admin-projects',  component: () => import('@/views/admin/ProjectManager.vue'), meta: { title: '项目管理' } },
      ],
    },

    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach((to) => {
  if (to.meta?.title) document.title = `${to.meta.title} | Portfolio`
  if (to.meta?.requiresAuth) {
    const auth = useAuthStore()
    if (!auth.isLoggedIn) return `/login?redirect=${encodeURIComponent(to.fullPath)}`
  }
})

export default router
