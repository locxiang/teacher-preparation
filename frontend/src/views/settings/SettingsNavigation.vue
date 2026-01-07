<template>
  <div class="space-y-4">
    <div class="bg-white border border-gray-200 rounded shadow-sm">
      <nav class="flex flex-col p-2">
        <a
          href="#"
          :class="activeTab === 'voiceprint'
            ? 'px-3 py-2 bg-nanyu-600 text-white font-medium rounded text-sm flex items-center'
            : 'px-3 py-2 text-gray-700 hover:bg-gray-50 rounded text-sm transition-colors flex items-center'"
          @click.prevent="$emit('tab-change', 'voiceprint')"
        >
          <svg
            class="w-4 h-4 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
            />
          </svg>
          <span>教师管理</span>
        </a>
        <a
          href="#"
          :class="activeTab === 'users'
            ? 'px-3 py-2 bg-nanyu-600 text-white font-medium rounded text-sm flex items-center'
            : 'px-3 py-2 text-gray-700 hover:bg-gray-50 rounded text-sm transition-colors flex items-center'"
          @click.prevent="$emit('tab-change', 'users')"
        >
          <svg
            class="w-4 h-4 mr-2"
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
          <span>用户管理</span>
        </a>
        <a
          href="#"
          :class="activeTab === 'api'
            ? 'px-3 py-2 bg-nanyu-600 text-white font-medium rounded text-sm flex items-center'
            : 'px-3 py-2 text-gray-700 hover:bg-gray-50 rounded text-sm transition-colors flex items-center'"
          @click.prevent="$emit('tab-change', 'api')"
        >
          <svg
            class="w-4 h-4 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"
            />
          </svg>
          <span>API 密钥</span>
        </a>
      </nav>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  activeTab: 'voiceprint' | 'users' | 'api'
}>()

defineEmits<{
  'tab-change': [tab: 'voiceprint' | 'users' | 'api']
}>()
</script>

