import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import { routes } from './routes'
import { useAuthStore } from './store'
import { getCurrentUser } from './services/auth'
import './index.css'

const app = createApp(App)

const router = createRouter({
  history: createWebHistory(),
  routes: routes,
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  // 明确检查 requiresAuth，只有明确设置为 true 才需要认证
  // 如果未设置或为 false，则不需要认证
  const requiresAuth = to.meta.requiresAuth === true

  // 如果路由需要认证
  if (requiresAuth) {
    // 如果没有 token，直接跳转到登录页
    if (!authStore.token.value) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }

    // 如果有 token 但没有用户信息，尝试获取用户信息
    if (!authStore.user.value) {
      try {
        const user = await getCurrentUser()
        authStore.setUser(user)
        next()
      } catch {
        // 获取用户信息失败，清除无效 token 并跳转到登录页
        authStore.logout()
        next({ name: 'Login', query: { redirect: to.fullPath } })
      }
    } else {
      next()
    }
  } else {
    // 如果已经登录，访问登录/注册页时跳转到首页
    if ((to.name === 'Login' || to.name === 'Register') && authStore.isAuthenticated.value) {
      next('/')
    } else {
      next()
    }
  }
})

app.use(router)
app.mount('#app')
