<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部固定栏 - 企业级设计 -->
    <div class="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
      <div class="max-w-[1600px] mx-auto px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-semibold text-gray-900">个人中心</h1>
            <p class="text-sm text-gray-500 mt-1">查看和管理您的账户信息</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="max-w-[1600px] mx-auto px-8 py-6">
      <div class="max-w-4xl mx-auto">
        <!-- 加载状态 -->
        <div v-if="isLoading" class="bg-white border border-gray-200 rounded shadow-sm p-12 text-center">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-nanyu-600"></div>
          <p class="mt-4 text-sm text-gray-600">加载中...</p>
        </div>

        <!-- 错误提示 -->
        <div v-else-if="errorMessage" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
          {{ errorMessage }}
        </div>

        <!-- 用户信息 -->
        <div v-else-if="user" class="space-y-5">
          <!-- 基本信息卡片 -->
          <div class="bg-white border border-gray-200 rounded shadow-sm">
            <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
              <h3 class="text-sm font-semibold text-gray-900">基本信息</h3>
            </div>
            <div class="p-6">
              <div class="space-y-0 divide-y divide-gray-200">
                <!-- 用户ID -->
                <div class="flex items-center justify-between py-3">
                  <span class="text-sm font-medium text-gray-600">用户ID</span>
                  <span class="text-sm text-gray-900 font-mono">{{ user.id }}</span>
                </div>

                <!-- 用户名 -->
                <div class="flex items-center justify-between py-3">
                  <span class="text-sm font-medium text-gray-600">用户名</span>
                  <span class="text-sm text-gray-900">{{ user.username }}</span>
                </div>

                <!-- 邮箱 -->
                <div class="flex items-center justify-between py-3">
                  <span class="text-sm font-medium text-gray-600">邮箱</span>
                  <span class="text-sm text-gray-900">{{ user.email }}</span>
                </div>

                <!-- 账户状态 -->
                <div class="flex items-center justify-between py-3">
                  <span class="text-sm font-medium text-gray-600">账户状态</span>
                  <span class="text-sm">
                    <span v-if="user.is_active" class="px-2 py-1 bg-green-50 text-green-700 rounded text-xs font-medium">正常</span>
                    <span v-else class="px-2 py-1 bg-red-50 text-red-700 rounded text-xs font-medium">已禁用</span>
                  </span>
                </div>

                <!-- 注册时间 -->
                <div class="flex items-center justify-between py-3">
                  <span class="text-sm font-medium text-gray-600">注册时间</span>
                  <span class="text-sm text-gray-900">{{ formatDate(user.created_at) }}</span>
                </div>

                <!-- 最后更新 -->
                <div class="flex items-center justify-between py-3">
                  <span class="text-sm font-medium text-gray-600">最后更新</span>
                  <span class="text-sm text-gray-900">{{ formatDate(user.updated_at) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="bg-white border border-gray-200 rounded shadow-sm">
            <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
              <h3 class="text-sm font-semibold text-gray-900">账户操作</h3>
            </div>
            <div class="p-6">
              <button
                @click="handleLogout"
                class="w-full px-4 py-2 text-sm bg-red-600 text-white rounded hover:bg-red-700 transition-colors font-medium"
              >
                退出登录
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCurrentUser, logout } from '@/services/auth'
import { useAuthStore } from '@/store'
import type { User } from '@/services/auth'

const router = useRouter()
const authStore = useAuthStore()

const user = ref<User | null>(null)
const isLoading = ref(true)
const errorMessage = ref('')

const formatDate = (dateString: string): string => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const loadUserInfo = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const userData = await getCurrentUser()
    user.value = userData
    authStore.setUser(userData)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '获取用户信息失败'
    // 如果未授权，跳转到登录页
    if (errorMessage.value.includes('未授权') || errorMessage.value.includes('401')) {
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    }
  } finally {
    isLoading.value = false
  }
}

const handleLogout = () => {
  if (confirm('确定要退出登录吗？')) {
    logout()
    authStore.logout()
    router.push('/login')
  }
}

onMounted(() => {
  loadUserInfo()
})
</script>

