<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full">
      <!-- Logo 和标题 -->
      <div class="text-center mb-8">
        <div class="flex justify-center mb-4">
          <div class="w-16 h-16 bg-nanyu-600 rounded-full flex items-center justify-center text-white font-bold text-2xl">
            南
          </div>
        </div>
        <h1 class="text-2xl font-semibold text-gray-900">
          登录账户
        </h1>
        <p class="mt-2 text-sm text-gray-500">
          还没有账户？
          <router-link
            to="/register"
            class="font-medium text-nanyu-600 hover:text-nanyu-700"
          >
            立即注册
          </router-link>
        </p>
      </div>

      <!-- 登录表单 -->
      <div class="bg-white border border-gray-200 rounded shadow-sm">
        <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
          <h2 class="text-sm font-semibold text-gray-900">
            登录信息
          </h2>
        </div>
        <form
          class="p-6 space-y-5"
          @submit.prevent="handleLogin"
        >
          <!-- 错误提示 -->
          <div
            v-if="errorMessage"
            class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm"
          >
            {{ errorMessage }}
          </div>

          <!-- 用户名/邮箱 -->
          <div>
            <label
              for="username"
              class="block text-sm font-medium text-gray-700 mb-1.5"
            >
              用户名或邮箱
            </label>
            <input
              id="username"
              v-model="usernameOrEmail"
              type="text"
              required
              autocomplete="username"
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-nanyu-500 focus:border-transparent outline-none transition-all"
              placeholder="请输入用户名或邮箱"
            >
          </div>

          <!-- 密码 -->
          <div>
            <label
              for="password"
              class="block text-sm font-medium text-gray-700 mb-1.5"
            >
              密码
            </label>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              autocomplete="current-password"
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-nanyu-500 focus:border-transparent outline-none transition-all"
              placeholder="请输入密码"
            >
          </div>

          <!-- 记住我 -->
          <div class="flex items-center">
            <input
              id="remember-me"
              v-model="rememberMe"
              type="checkbox"
              class="w-4 h-4 text-nanyu-600 border-gray-300 rounded focus:ring-nanyu-500"
            >
            <label
              for="remember-me"
              class="ml-2 block text-sm text-gray-700"
            >
              记住我
            </label>
          </div>

          <!-- 提交按钮 -->
          <div>
            <button
              type="submit"
              :disabled="isLoading"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded text-sm font-medium text-white bg-nanyu-600 hover:bg-nanyu-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-nanyu-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <span v-if="!isLoading">登录</span>
              <span
                v-else
                class="flex items-center"
              >
                <svg
                  class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    class="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="4"
                  />
                  <path
                    class="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                登录中...
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '@/services/auth'
import { useAuthStore } from '@/store'

const router = useRouter()
const authStore = useAuthStore()

const usernameOrEmail = ref('')
const password = ref('')
const rememberMe = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  if (!usernameOrEmail.value || !password.value) {
    errorMessage.value = '请填写用户名和密码'
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await login(usernameOrEmail.value, password.value)

    if (response.success) {
      // 更新用户状态
      authStore.setUser(response.data.user)
      authStore.setToken(response.data.access_token)

      // 跳转到首页或之前访问的页面
      const redirect = router.currentRoute.value.query.redirect as string || '/'
      router.push(redirect)
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '登录失败，请重试'
  } finally {
    isLoading.value = false
  }
}
</script>

