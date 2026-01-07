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
          创建账户
        </h1>
        <p class="mt-2 text-sm text-gray-500">
          已有账户？
          <router-link
            to="/login"
            class="font-medium text-nanyu-600 hover:text-nanyu-700"
          >
            立即登录
          </router-link>
        </p>
      </div>

      <!-- 注册表单 -->
      <div class="bg-white border border-gray-200 rounded shadow-sm">
        <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
          <h2 class="text-sm font-semibold text-gray-900">
            注册信息
          </h2>
        </div>
        <form
          class="p-6 space-y-5"
          @submit.prevent="handleRegister"
        >
          <!-- 错误提示 -->
          <div
            v-if="errorMessage"
            class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm"
          >
            {{ errorMessage }}
          </div>

          <!-- 成功提示 -->
          <div
            v-if="successMessage"
            class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded text-sm"
          >
            {{ successMessage }}
          </div>

          <!-- 用户名 -->
          <div>
            <label
              for="username"
              class="block text-sm font-medium text-gray-700 mb-1.5"
            >
              用户名 <span class="text-red-500">*</span>
            </label>
            <input
              id="username"
              v-model="username"
              type="text"
              required
              autocomplete="username"
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-nanyu-500 focus:border-transparent outline-none transition-all"
              placeholder="请输入用户名"
            >
          </div>

          <!-- 邮箱 -->
          <div>
            <label
              for="email"
              class="block text-sm font-medium text-gray-700 mb-1.5"
            >
              邮箱 <span class="text-red-500">*</span>
            </label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              autocomplete="email"
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-nanyu-500 focus:border-transparent outline-none transition-all"
              placeholder="请输入邮箱地址"
            >
          </div>

          <!-- 密码 -->
          <div>
            <label
              for="password"
              class="block text-sm font-medium text-gray-700 mb-1.5"
            >
              密码 <span class="text-red-500">*</span>
            </label>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              autocomplete="new-password"
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-nanyu-500 focus:border-transparent outline-none transition-all"
              placeholder="请输入密码（至少6位）"
              minlength="6"
            >
            <p class="mt-1 text-xs text-gray-500">
              密码长度至少6位
            </p>
          </div>

          <!-- 确认密码 -->
          <div>
            <label
              for="confirmPassword"
              class="block text-sm font-medium text-gray-700 mb-1.5"
            >
              确认密码 <span class="text-red-500">*</span>
            </label>
            <input
              id="confirmPassword"
              v-model="confirmPassword"
              type="password"
              required
              autocomplete="new-password"
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-nanyu-500 focus:border-transparent outline-none transition-all"
              placeholder="请再次输入密码"
            >
          </div>

          <!-- 提交按钮 -->
          <div>
            <button
              type="submit"
              :disabled="isLoading"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded text-sm font-medium text-white bg-nanyu-600 hover:bg-nanyu-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-nanyu-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <span v-if="!isLoading">注册</span>
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
                注册中...
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
import { register } from '@/services/auth'
import { useAuthStore } from '@/store'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const handleRegister = async () => {
  // 验证输入
  if (!username.value || !email.value || !password.value || !confirmPassword.value) {
    errorMessage.value = '请填写所有必填项'
    return
  }

  if (password.value.length < 6) {
    errorMessage.value = '密码长度至少6位'
    return
  }

  if (password.value !== confirmPassword.value) {
    errorMessage.value = '两次输入的密码不一致'
    return
  }

  // 邮箱格式验证
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email.value)) {
    errorMessage.value = '请输入有效的邮箱地址'
    return
  }

  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await register(username.value, email.value, password.value)

    if (response.success) {
      successMessage.value = '注册成功！正在跳转...'

      // 更新用户状态
      authStore.setUser(response.data.user)
      authStore.setToken(response.data.access_token)

      // 延迟跳转，让用户看到成功消息
      setTimeout(() => {
        router.push('/')
      }, 1500)
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '注册失败，请重试'
  } finally {
    isLoading.value = false
  }
}
</script>

