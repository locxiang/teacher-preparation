<template>
  <div class="min-h-screen flex flex-col bg-gray-50 font-sans">
    <!-- Header -->
    <header class="bg-nanyu-600 text-white shadow-lg">
      <div class="container mx-auto px-4 h-16 flex items-center justify-between">
        <router-link to="/" class="flex items-center space-x-4 hover:opacity-90 transition-opacity cursor-pointer">
          <!-- Logo Placeholder -->
          <div class="w-10 h-10 bg-white rounded-full flex items-center justify-center text-nanyu-600 font-bold text-xl">
            南
          </div>
          <div>
            <h1 class="text-xl font-bold tracking-wide">南渝中学</h1>
            <p class="text-xs text-nanyu-100 opacity-90">集体备课 AI 助手</p>
          </div>
        </router-link>

        <nav class="hidden md:flex items-center space-x-6">
          <template v-if="authStore.isAuthenticated.value">
            <router-link to="/" class="hover:text-nanyu-100 transition-colors font-medium">首页</router-link>
            <router-link to="/ai-chat" class="hover:text-nanyu-100 transition-colors font-medium">AI对话</router-link>
            <router-link to="/demo-ali" class="hover:text-nanyu-100 transition-colors font-medium">语音识别</router-link>
            <router-link to="/settings" class="hover:text-nanyu-100 transition-colors font-medium">设置</router-link>

            <!-- 用户信息 -->
            <div class="flex items-center space-x-2 ml-4 pl-4 border-l border-nanyu-500">
              <router-link to="/profile" class="flex items-center space-x-2 hover:text-nanyu-100 transition-colors cursor-pointer">
                <div class="w-8 h-8 rounded-full bg-nanyu-500 flex items-center justify-center border border-nanyu-400">
                  <span class="text-sm">{{ userInitial }}</span>
                </div>
                <span class="text-sm">{{ authStore.user.value?.username || '用户' }}</span>
              </router-link>
              <button
                @click="handleLogout"
                class="ml-2 text-sm text-nanyu-100 hover:text-white transition-colors"
                title="退出登录"
              >
                退出
              </button>
            </div>
          </template>

          <!-- 未登录时显示登录按钮 -->
          <template v-else>
            <router-link to="/login" class="hover:text-nanyu-100 transition-colors font-medium">登录</router-link>
            <router-link
              to="/register"
              class="px-4 py-2 bg-nanyu-500 hover:bg-nanyu-400 rounded-lg text-sm font-medium transition-colors"
            >
              注册
            </router-link>
          </template>
        </nav>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 min-h-0 overflow-hidden flex flex-col">
      <div class="container mx-auto px-4 h-full flex flex-col">
        <slot />
      </div>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-gray-400 py-6 mt-auto">
      <div class="container mx-auto px-4 text-center">
        <p class="text-sm">&copy; {{ new Date().getFullYear() }} 重庆南渝中学. All rights reserved.</p>
        <p class="text-xs mt-1 opacity-60">Powered by AI Teaching Assistant System</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store'
import { logout } from '@/services/auth'

const router = useRouter()
const authStore = useAuthStore()

const userInitial = computed(() => {
  const username = authStore.user.value?.username || ''
  return username ? username.charAt(0).toUpperCase() : '用'
})

const handleLogout = () => {
  if (confirm('确定要退出登录吗？')) {
    logout()
    authStore.logout()
    router.push('/login')
  }
}
</script>

