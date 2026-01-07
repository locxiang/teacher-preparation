<template>
  <div class="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
    <div class="max-w-[1600px] mx-auto px-8 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <div>
            <h1 class="text-2xl font-semibold text-gray-900 flex items-center">
              {{ meeting?.name || '会议进行中' }}
              <span class="ml-3 text-xs px-2 py-1 rounded bg-green-100 text-green-700 font-medium animate-pulse">● 进行中</span>
            </h1>
            <p class="text-sm text-gray-500 mt-1">
              {{ formatTime(new Date()) }} | {{ messageCount }}条记录
              <span
                v-if="meeting?.task_id"
                class="ml-2 font-mono text-xs"
              >Task ID: {{ meeting.task_id.substring(0, 8) }}...</span>
            </p>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <!-- 任务状态提示 -->
          <div
            v-if="!taskInfo?.MeetingJoinUrl"
            class="text-xs text-red-600 px-3 py-1.5 rounded bg-red-50 border border-red-200"
          >
            ⚠️ 未找到任务信息
          </div>

          <!-- 麦克风授权按钮 -->
          <button
            v-else-if="!hasMicrophonePermission"
            :disabled="isRequestingPermission"
            class="px-3 py-1.5 text-xs bg-blue-50 text-blue-700 hover:bg-blue-100 rounded border border-blue-200 transition-colors flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
            @click="$emit('request-permission')"
          >
            <span class="mr-1">🎤</span>
            {{ isRequestingPermission ? '请求授权中...' : '授权麦克风' }}
          </button>

          <!-- 开始/停止录音按钮 -->
          <button
            v-else
            :class="isRecording
              ? 'bg-yellow-50 text-yellow-700 hover:bg-yellow-100 border-yellow-200'
              : 'bg-green-50 text-green-700 hover:bg-green-100 border-green-200'"
            class="px-3 py-1.5 text-xs rounded border transition-colors flex items-center"
            @click="$emit('toggle-recording')"
          >
            <span class="mr-1">{{ isRecording ? '⏸️' : '▶️' }}</span>
            {{ isRecording ? '暂停录音' : '开始录音' }}
          </button>

          <router-link
            :to="`/meeting/${meetingId}/summary`"
            class="px-3 py-1.5 text-xs bg-red-50 text-red-700 hover:bg-red-100 rounded border border-red-200 transition-colors"
          >
            结束会议
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Meeting } from '@/services/meeting'

interface Props {
  meeting: Meeting | null
  meetingId: string
  messageCount: number
  taskInfo: { TaskId?: string; MeetingJoinUrl?: string; TaskStatus?: string } | null
  hasMicrophonePermission: boolean
  isRequestingPermission: boolean
  isRecording: boolean
}

defineProps<Props>()

defineEmits<{
  'request-permission': []
  'toggle-recording': []
}>()

const formatTime = (date: Date): string => {
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}`
}
</script>

