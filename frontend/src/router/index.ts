import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/projects' },
    { path: '/login', component: () => import('../views/LoginView.vue') },
    { path: '/register', component: () => import('../views/RegisterView.vue') },
    { path: '/projects', component: () => import('../views/ProjectsView.vue'), meta: { requiresAuth: true } },
    { path: '/boards/:id', component: () => import('../views/BoardView.vue'), meta: { requiresAuth: true } },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.user && auth.token) {
    await auth.fetchMe()
  }
  if (to.meta.requiresAuth && !auth.token) {
    return '/login'
  }
  if ((to.path === '/login' || to.path === '/register') && auth.token) {
    return '/projects'
  }
})

export default router
