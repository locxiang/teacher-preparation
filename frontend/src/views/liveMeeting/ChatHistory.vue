<template>
  <div class="bg-white border border-gray-200 rounded shadow-sm flex flex-col overflow-hidden flex-grow min-h-0">
    <div class="px-5 py-3 border-b border-gray-200 bg-gray-50 flex justify-between items-center shrink-0">
      <h3 class="text-sm font-semibold text-gray-900 flex items-center">
        <svg class="w-4 h-4 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
        对话记录
      </h3>
      <div class="flex space-x-2">
        <button class="text-gray-500 hover:text-gray-700 p-1.5 rounded hover:bg-gray-100 transition-colors" title="搜索">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </button>
        <button class="text-gray-500 hover:text-gray-700 p-1.5 rounded hover:bg-gray-100 transition-colors" title="导出">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
        </button>
      </div>
    </div>

    <div
      ref="messagesContainer"
      class="flex-grow overflow-y-auto p-4 space-y-4 scroll-smooth"
    >
      <!-- Messages (倒序显示，最新的在上面) -->
      <div v-for="message in reversedMessages" :key="message.id" class="flex space-x-3">
        <div
          class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border shrink-0"
          :class="message.type === 'ai'
            ? 'bg-nanyu-600 text-white border-nanyu-600'
            : message.speaker === '张老师'
              ? 'bg-blue-100 text-blue-600 border-blue-200'
              : message.speaker === '李老师'
                ? 'bg-pink-100 text-pink-600 border-pink-200'
                : 'bg-gray-100 text-gray-600 border-gray-200'"
        >
          {{ message.type === 'ai' ? '🤖' : message.speaker[0] }}
        </div>
        <div class="flex-1">
          <div class="flex items-center mb-1">
            <span class="text-sm font-semibold mr-2" :class="message.type === 'ai' ? 'text-nanyu-700' : 'text-gray-800'">
              {{ message.speaker }}
            </span>
            <span v-if="message.relativeTime !== undefined" class="text-xs text-gray-500 mr-1">
              {{ formatRelativeTime(message.relativeTime) }}
            </span>
            <span class="text-xs text-gray-400">{{ formatTime(message.timestamp) }}</span>
            <span v-if="message.stageIndex !== currentStageIndex" class="ml-2 text-xs bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded">
              {{ stages[message.stageIndex]?.name }}
            </span>
          </div>
          <div
            class="rounded rounded-tl-none border p-3 text-sm"
            :class="[
              message.type === 'ai'
                ? 'bg-nanyu-50 border-nanyu-100 text-gray-800'
                : message.isFinal === false
                  ? 'bg-gray-100 border-gray-200 text-gray-500 italic'
                  : 'bg-white border-gray-200 text-gray-700'
            ]"
          >
            {{ message.content }}
            <span v-if="message.isFinal === false" class="ml-2 text-xs text-gray-400">(识别中...)</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick } from 'vue'

interface Stage {
  id: string
  name: string
  description: string
}

interface Message {
  id: string
  type: 'human' | 'ai'
  speaker: string
  content: string
  timestamp: number // 绝对时间戳（真实时间）
  relativeTime?: number // 相对时间（从录音开始的毫秒数）
  stageIndex: number
  isFinal?: boolean
}

interface Props {
  messages: Message[]
  stages: Stage[]
  currentStageIndex: number
}

const props = defineProps<Props>()

const messagesContainer = ref<HTMLElement | null>(null)

// 倒序显示消息（最新的在上面）
const reversedMessages = computed(() => {
  return [...props.messages].reverse()
})

// 当有新消息时，滚动到顶部（因为倒序显示，最新的在上面）
watch(() => props.messages.length, () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = 0
    }
  })
})

// 格式化绝对时间（真实时间）
const formatTime = (timestamp: number): string => {
  const date = new Date(timestamp)
  if (isNaN(date.getTime())) {
    return '00:00:00'
  }
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}`
}

// 格式化相对时间（从录音开始的时长）
const formatRelativeTime = (milliseconds: number): string => {
  const totalSeconds = Math.floor(milliseconds / 1000)
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60

  if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  } else {
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }
}
</script>

