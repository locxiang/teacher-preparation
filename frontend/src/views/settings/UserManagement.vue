<template>
  <div class="bg-white border border-gray-200 rounded shadow-sm">
    <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div class="flex items-center">
          <svg
            class="w-5 h-5 mr-2 text-gray-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
            />
          </svg>
          <div>
            <h3 class="text-sm font-semibold text-gray-900">
              用户列表
            </h3>
            <p class="text-xs text-gray-500 mt-0.5">
              共 {{ users.length }} 位用户
            </p>
          </div>
        </div>
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索用户..."
            class="pl-8 pr-3 py-1.5 text-sm bg-white border border-gray-300 rounded focus:ring-2 focus:ring-nanyu-500 focus:border-transparent outline-none w-full sm:w-64 transition-all"
          >
          <svg
            class="absolute left-2.5 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
      </div>
    </div>

    <div
      v-if="isLoading"
      class="p-12 text-center"
    >
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-nanyu-600" />
      <p class="mt-4 text-sm text-gray-600">
        加载中...
      </p>
    </div>

    <div
      v-else-if="filteredUsers.length === 0"
      class="p-12 text-center"
    >
      <svg
        class="w-12 h-12 mx-auto mb-3 text-gray-300"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
        />
      </svg>
      <p class="text-sm text-gray-500 font-medium">
        暂无用户
      </p>
    </div>

    <div
      v-else
      class="divide-y divide-gray-200"
    >
      <div
        v-for="user in filteredUsers"
        :key="user.id"
        class="p-4 hover:bg-gray-50 transition-colors"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-start space-x-3 flex-1 min-w-0">
            <!-- Avatar -->
            <div
              class="shrink-0 w-10 h-10 rounded flex items-center justify-center text-sm font-bold"
              :class="user.is_active
                ? 'bg-nanyu-600 text-white'
                : 'bg-gray-200 text-gray-500'"
            >
              {{ user.username[0].toUpperCase() }}
            </div>

            <!-- Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1.5">
                <h4 class="text-sm font-semibold text-gray-900">
                  {{ user.username }}
                </h4>
                <span
                  :class="user.is_active
                    ? 'px-2 py-0.5 bg-green-50 text-green-700 rounded text-xs font-medium'
                    : 'px-2 py-0.5 bg-gray-100 text-gray-500 rounded text-xs font-medium'"
                >
                  {{ user.is_active ? '已激活' : '已禁用' }}
                </span>
              </div>

              <!-- Details -->
              <div class="space-y-1">
                <div class="text-xs text-gray-500">
                  <span class="font-medium">邮箱:</span>
                  <span class="ml-1 text-gray-700">{{ user.email }}</span>
                </div>

                <div class="flex flex-col gap-0.5 text-xs text-gray-500">
                  <div>
                    <span class="font-medium">用户ID:</span>
                    <span class="ml-1 font-mono text-gray-700">{{ user.id }}</span>
                  </div>
                  <div>
                    <span class="font-medium">注册时间:</span>
                    <span class="ml-1 text-gray-700">{{ formatDate(user.created_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2 ml-4 shrink-0">
            <button
              class="px-3 py-1.5 text-xs rounded transition-colors font-medium"
              :class="user.is_active
                ? 'bg-white text-orange-600 border border-orange-200 hover:border-orange-400 hover:bg-orange-50'
                : 'bg-green-600 text-white hover:bg-green-700'"
              @click="handleToggleStatus(user)"
            >
              {{ user.is_active ? '禁用' : '激活' }}
            </button>
            <button
              class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors rounded"
              title="删除用户"
              @click="handleDelete(user.id)"
            >
              <svg
                class="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getUsers, updateUserStatus, deleteUser, type User } from '../../services/auth'

const users = ref<User[]>([])
const isLoading = ref(false)
const searchQuery = ref('')

// 加载用户列表
const loadUsers = async () => {
  isLoading.value = true
  try {
    const data = await getUsers()
    users.value = data
  } catch (error) {
    console.error('Failed to load users:', error)
    alert(error instanceof Error ? error.message : '获取用户列表失败')
  } finally {
    isLoading.value = false
  }
}

// 切换用户状态
const handleToggleStatus = async (user: User) => {
  const action = user.is_active ? '禁用' : '激活'
  if (confirm(`确定要${action}该用户吗？`)) {
    try {
      await updateUserStatus(user.id, !user.is_active)
      await loadUsers()
    } catch (error) {
      alert(error instanceof Error ? error.message : `${action}用户失败`)
    }
  }
}

// 删除用户
const handleDelete = async (userId: number) => {
  if (confirm('确定要删除该用户吗？此操作不可恢复！')) {
    try {
      await deleteUser(userId)
      await loadUsers()
    } catch (error) {
      alert(error instanceof Error ? error.message : '删除用户失败')
    }
  }
}

const filteredUsers = computed(() => {
  if (!searchQuery.value) {
    return users.value
  }
  const query = searchQuery.value.toLowerCase()
  return users.value.filter(user =>
    user.username.toLowerCase().includes(query) ||
    user.email.toLowerCase().includes(query) ||
    user.id.toString().includes(query),
  )
})

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  loadUsers()
})
</script>

