<template>
  <div class="bg-white border border-gray-200 rounded shadow-sm">
    <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
      <div class="flex items-center">
        <svg class="w-5 h-5 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
        </svg>
        <div>
          <h3 class="text-sm font-semibold text-gray-900">API 密钥管理</h3>
          <p class="text-xs text-gray-500 mt-0.5">查看和管理系统配置的API密钥</p>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="p-12 text-center">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-nanyu-600"></div>
      <p class="mt-4 text-sm text-gray-600">加载中...</p>
    </div>

    <div v-else-if="apiKeys" class="p-6 space-y-5">
      <!-- Backend API Keys -->
      <div>
        <h4 class="text-sm font-semibold text-gray-900 mb-4 flex items-center">
          <svg class="w-4 h-4 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
          后端配置
        </h4>

        <!-- 阿里云配置 -->
        <div class="mb-4">
          <h5 class="text-xs font-semibold text-gray-700 mb-3 flex items-center">
            <svg class="w-4 h-4 mr-1.5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
            </svg>
            阿里云
          </h5>
          <div class="space-y-2">
            <div
              v-for="(keyInfo, key) in apiKeys.backend.alibaba_cloud"
              :key="key"
              class="bg-gray-50 rounded p-3 border border-gray-200"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-2">
                    <span class="text-xs font-semibold text-gray-700">{{ keyInfo.name }}</span>
                    <span
                      :class="keyInfo.is_set
                        ? 'px-2 py-0.5 bg-green-50 text-green-700 rounded text-xs font-medium'
                        : 'px-2 py-0.5 bg-gray-100 text-gray-500 rounded text-xs font-medium'"
                    >
                      {{ keyInfo.is_set ? '已配置' : '未配置' }}
                    </span>
                  </div>
                  <div class="flex items-center gap-2 mt-2">
                    <code class="text-xs font-mono bg-white px-2 py-1 rounded border border-gray-300 text-gray-800 flex-1 min-w-0 truncate">
                      {{ getDisplayValue(keyInfo, `backend.alibaba_cloud.${key}`) }}
                    </code>
                    <button
                      v-if="keyInfo.full_value"
                      @click="toggleShowFullValue(`backend.alibaba_cloud.${key}`)"
                      class="px-2 py-1 text-xs bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors shrink-0"
                    >
                      {{ showFullValues[`backend.alibaba_cloud.${key}`] ? '隐藏' : '显示' }}
                    </button>
                    <button
                      v-if="keyInfo.full_value"
                      @click="copyToClipboard(keyInfo.full_value, keyInfo.name)"
                      class="px-2 py-1 text-xs bg-nanyu-600 text-white rounded hover:bg-nanyu-700 transition-colors shrink-0"
                    >
                      复制
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 通义听悟配置 -->
        <div class="mb-4">
          <h5 class="text-xs font-semibold text-gray-700 mb-3 flex items-center">
            <svg class="w-4 h-4 mr-1.5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
            通义听悟
          </h5>
          <div class="space-y-2">
            <div
              v-for="(keyInfo, key) in apiKeys.backend.tytingwu"
              :key="key"
              class="bg-gray-50 rounded p-3 border border-gray-200"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-2">
                    <span class="text-xs font-semibold text-gray-700">{{ keyInfo.name }}</span>
                    <span
                      :class="keyInfo.is_set
                        ? 'px-2 py-0.5 bg-green-50 text-green-700 rounded text-xs font-medium'
                        : 'px-2 py-0.5 bg-gray-100 text-gray-500 rounded text-xs font-medium'"
                    >
                      {{ keyInfo.is_set ? '已配置' : '未配置' }}
                    </span>
                  </div>
                  <div class="flex items-center gap-2 mt-2">
                    <code class="text-xs font-mono bg-white px-2 py-1 rounded border border-gray-300 text-gray-800 flex-1 min-w-0 truncate">
                      {{ getDisplayValue(keyInfo, `backend.tytingwu.${key}`) }}
                    </code>
                    <button
                      v-if="keyInfo.full_value"
                      @click="toggleShowFullValue(`backend.tytingwu.${key}`)"
                      class="px-2 py-1 text-xs bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors shrink-0"
                    >
                      {{ showFullValues[`backend.tytingwu.${key}`] ? '隐藏' : '显示' }}
                    </button>
                    <button
                      v-if="keyInfo.full_value"
                      @click="copyToClipboard(keyInfo.full_value, keyInfo.name)"
                      class="px-2 py-1 text-xs bg-nanyu-600 text-white rounded hover:bg-nanyu-700 transition-colors shrink-0"
                    >
                      复制
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 智能语音交互配置 -->
        <div class="mb-4">
          <h5 class="text-xs font-semibold text-gray-700 mb-3 flex items-center">
            <svg class="w-4 h-4 mr-1.5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
            </svg>
            智能语音交互（TTS）
          </h5>
          <div class="space-y-2">
            <div
              v-for="(keyInfo, key) in apiKeys.backend.nls"
              :key="key"
              class="bg-gray-50 rounded p-3 border border-gray-200"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-2">
                    <span class="text-xs font-semibold text-gray-700">{{ keyInfo.name }}</span>
                    <span
                      :class="keyInfo.is_set
                        ? 'px-2 py-0.5 bg-green-50 text-green-700 rounded text-xs font-medium'
                        : 'px-2 py-0.5 bg-gray-100 text-gray-500 rounded text-xs font-medium'"
                    >
                      {{ keyInfo.is_set ? '已配置' : '未配置' }}
                    </span>
                  </div>
                  <div class="flex items-center gap-2 mt-2">
                    <code class="text-xs font-mono bg-white px-2 py-1 rounded border border-gray-300 text-gray-800 flex-1 min-w-0 truncate">
                      {{ getDisplayValue(keyInfo, `backend.nls.${key}`) }}
                    </code>
                    <button
                      v-if="keyInfo.full_value"
                      @click="toggleShowFullValue(`backend.nls.${key}`)"
                      class="px-2 py-1 text-xs bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors shrink-0"
                    >
                      {{ showFullValues[`backend.nls.${key}`] ? '隐藏' : '显示' }}
                    </button>
                    <button
                      v-if="keyInfo.full_value"
                      @click="copyToClipboard(keyInfo.full_value, keyInfo.name)"
                      class="px-2 py-1 text-xs bg-nanyu-600 text-white rounded hover:bg-nanyu-700 transition-colors shrink-0"
                    >
                      复制
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- DashScope配置 -->
        <div class="mb-4">
          <h5 class="text-xs font-semibold text-gray-700 mb-3 flex items-center">
            <svg class="w-4 h-4 mr-1.5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            阿里云百炼（DashScope）
          </h5>
          <div class="space-y-2">
            <div
              v-for="(keyInfo, key) in apiKeys.backend.dashscope"
              :key="key"
              class="bg-gray-50 rounded p-3 border border-gray-200"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-2">
                    <span class="text-xs font-semibold text-gray-700">{{ keyInfo.name }}</span>
                    <span
                      :class="keyInfo.is_set
                        ? 'px-2 py-0.5 bg-green-50 text-green-700 rounded text-xs font-medium'
                        : 'px-2 py-0.5 bg-gray-100 text-gray-500 rounded text-xs font-medium'"
                    >
                      {{ keyInfo.is_set ? '已配置' : '未配置' }}
                    </span>
                  </div>
                  <div class="flex items-center gap-2 mt-2">
                    <code class="text-xs font-mono bg-white px-2 py-1 rounded border border-gray-300 text-gray-800 flex-1 min-w-0 truncate">
                      {{ getDisplayValue(keyInfo, `backend.dashscope.${key}`) }}
                    </code>
                    <button
                      v-if="keyInfo.full_value"
                      @click="toggleShowFullValue(`backend.dashscope.${key}`)"
                      class="px-2 py-1 text-xs bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors shrink-0"
                    >
                      {{ showFullValues[`backend.dashscope.${key}`] ? '隐藏' : '显示' }}
                    </button>
                    <button
                      v-if="keyInfo.full_value"
                      @click="copyToClipboard(keyInfo.full_value, keyInfo.name)"
                      class="px-2 py-1 text-xs bg-nanyu-600 text-white rounded hover:bg-nanyu-700 transition-colors shrink-0"
                    >
                      复制
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Flask配置 -->
        <div class="mb-4">
          <h5 class="text-xs font-semibold text-gray-700 mb-3 flex items-center">
            <svg class="w-4 h-4 mr-1.5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Flask
          </h5>
          <div class="space-y-2">
            <div
              v-for="(keyInfo, key) in apiKeys.backend.flask"
              :key="key"
              class="bg-gray-50 rounded p-3 border border-gray-200"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-2">
                    <span class="text-xs font-semibold text-gray-700">{{ keyInfo.name }}</span>
                    <span
                      :class="keyInfo.is_set
                        ? 'px-2 py-0.5 bg-green-50 text-green-700 rounded text-xs font-medium'
                        : 'px-2 py-0.5 bg-orange-50 text-orange-700 rounded text-xs font-medium'"
                    >
                      {{ keyInfo.is_set ? '已配置' : '使用默认值（不安全）' }}
                    </span>
                  </div>
                  <div class="flex items-center gap-2 mt-2">
                    <code class="text-xs font-mono bg-white px-2 py-1 rounded border border-gray-300 text-gray-800 flex-1 min-w-0 truncate">
                      {{ getDisplayValue(keyInfo, `backend.flask.${key}`) }}
                    </code>
                    <button
                      v-if="keyInfo.full_value"
                      @click="toggleShowFullValue(`backend.flask.${key}`)"
                      class="px-2 py-1 text-xs bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors shrink-0"
                    >
                      {{ showFullValues[`backend.flask.${key}`] ? '隐藏' : '显示' }}
                    </button>
                    <button
                      v-if="keyInfo.full_value"
                      @click="copyToClipboard(keyInfo.full_value, keyInfo.name)"
                      class="px-2 py-1 text-xs bg-nanyu-600 text-white rounded hover:bg-nanyu-700 transition-colors shrink-0"
                    >
                      复制
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getApiKeys, type ApiKeyInfo } from '../../services/auth'

interface ApiKeysData {
  backend: {
    alibaba_cloud: Record<string, ApiKeyInfo>
    tytingwu: Record<string, ApiKeyInfo>
    nls: Record<string, ApiKeyInfo>
    dashscope: Record<string, ApiKeyInfo>
    flask: Record<string, ApiKeyInfo>
  }
  frontend: {
    xunfei: Record<string, ApiKeyInfo>
  }
}

const apiKeys = ref<ApiKeysData | null>(null)
const isLoading = ref(false)
const showFullValues = ref<Record<string, boolean>>({})

// 加载API密钥信息
const loadApiKeys = async () => {
  isLoading.value = true
  try {
    const data = await getApiKeys()
    apiKeys.value = data
  } catch (error) {
    console.error('Failed to load API keys:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadApiKeys()
})

const toggleShowFullValue = (key: string) => {
  showFullValues.value[key] = !showFullValues.value[key]
}

const getDisplayValue = (keyInfo: ApiKeyInfo, key: string): string => {
  if (showFullValues.value[key] && keyInfo.full_value) {
    return keyInfo.full_value
  }
  return keyInfo.value
}

const copyToClipboard = async (text: string, name: string) => {
  try {
    await navigator.clipboard.writeText(text)
    alert(`${name} 已复制到剪贴板`)
  } catch (error) {
    console.error('复制失败:', error)
    alert('复制失败，请手动复制')
  }
}
</script>

