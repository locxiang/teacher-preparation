<template>
  <div class="flex flex-col h-full bg-gray-50">
    <!-- 删除确认对话框 -->
    <ConfirmDialog
      v-model:visible="showDeleteDialog"
      :message="deleteMessage"
      :details="deleteDetails"
      :loading="isDeleting !== null"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />

    <!-- 顶部固定栏 - 企业级设计 -->
    <div class="bg-white border-b border-gray-200 shrink-0 shadow-sm">
      <div class="max-w-[1600px] mx-auto px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-semibold text-gray-900">备课会议</h1>
            <p class="text-sm text-gray-500 mt-1">管理和查看您的所有集体备课记录</p>
          </div>
          <router-link
            to="/meeting/create"
            class="px-4 py-2 text-sm bg-nanyu-600 text-white rounded font-medium hover:bg-nanyu-700 transition-colors flex items-center space-x-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            <span>创建新会议</span>
          </router-link>
        </div>
      </div>
    </div>

    <!-- 主内容区域 - 可滚动，设置最小高度为0以确保flex-1生效 -->
    <div class="flex-1 overflow-y-auto max-w-[1600px] mx-auto px-8 py-6 w-full min-h-0">
      <!-- Loading State -->
      <div v-if="isLoading" class="bg-white border border-gray-200 rounded shadow-sm p-12 text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-nanyu-600"></div>
        <p class="mt-4 text-sm text-gray-600">加载中...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="errorMessage" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
        {{ errorMessage }}
      </div>

      <!-- Empty State -->
      <div v-else-if="meetings.length === 0" class="bg-white border border-gray-200 rounded shadow-sm p-12 text-center">
        <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <p class="text-sm text-gray-500 mb-4">还没有会议记录</p>
        <router-link
          to="/meeting/create"
          class="inline-block px-4 py-2 text-sm bg-nanyu-600 text-white rounded font-medium hover:bg-nanyu-700 transition-colors"
        >
          创建第一个会议
        </router-link>
      </div>

      <!-- Meeting List - 表格布局 -->
      <div v-else class="bg-white border border-gray-200 rounded shadow-sm">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">会议名称</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">科目类型</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">老师数量</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">状态</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">创建时间</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">时长</th>
                <th class="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="meeting in meetings"
                :key="meeting.id"
                class="hover:bg-gray-50 transition-colors"
              >
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="shrink-0 w-2 h-2 rounded-full mr-3"
                      :class="{
                        'bg-green-500': meeting.status === 'running',
                        'bg-yellow-400': meeting.status === 'pending',
                        'bg-gray-300': meeting.status === 'stopped' || meeting.status === 'completed'
                      }"
                    ></div>
                    <div>
                      <div class="text-sm font-medium text-gray-900">{{ meeting.name }}</div>
                      <div v-if="meeting.description" class="text-xs text-gray-500 mt-0.5 line-clamp-1">
                        {{ meeting.description }}
                      </div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ getSubjectText(meeting) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ getTeacherCount(meeting) }}人
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    class="text-xs font-semibold px-2 py-1 rounded"
                    :class="{
                      'bg-green-50 text-green-700 border border-green-100': meeting.status === 'running',
                      'bg-yellow-50 text-yellow-700 border border-yellow-100': meeting.status === 'pending',
                      'bg-gray-100 text-gray-600': meeting.status === 'stopped' || meeting.status === 'completed'
                    }"
                  >
                    {{ getStatusText(meeting.status) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(meeting.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ calculateDuration(meeting) }}分钟
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div class="flex items-center justify-end space-x-2">
                    <router-link
                      v-if="meeting.status === 'running'"
                      :to="`/meeting/${meeting.id}/live`"
                      class="px-3 py-1.5 text-xs bg-nanyu-50 text-nanyu-700 rounded hover:bg-nanyu-100 transition-colors"
                    >
                      进入会议
                    </router-link>
                    <router-link
                      v-else-if="meeting.status === 'pending'"
                      :to="`/meeting/${meeting.id}/upload`"
                      class="px-3 py-1.5 text-xs bg-nanyu-600 text-white rounded hover:bg-nanyu-700 transition-colors"
                    >
                      开始会议
                    </router-link>
                    <router-link
                      v-else
                      :to="`/meeting/${meeting.id}/summary`"
                      class="px-3 py-1.5 text-xs border border-gray-200 text-gray-600 rounded hover:bg-gray-50 transition-colors"
                    >
                      查看总结
                    </router-link>
                    <button
                      @click="handleDelete(meeting.id, meeting.name)"
                      :disabled="isDeleting === meeting.id"
                      class="px-3 py-1.5 text-xs text-red-600 hover:bg-red-50 border border-red-200 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      title="删除会议"
                    >
                      {{ isDeleting === meeting.id ? '删除中...' : '删除' }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getMeetings, formatDate, calculateDuration, deleteMeeting, type Meeting } from '@/services/meeting'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const meetings = ref<Meeting[]>([])
const isLoading = ref(true)
const errorMessage = ref('')
const isDeleting = ref<string | null>(null)
const showDeleteDialog = ref(false)
const pendingDeleteMeeting = ref<{ id: string; name: string } | null>(null)

const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    pending: '待开始',
    running: '进行中',
    stopped: '已停止',
    completed: '已完成',
  }
  return statusMap[status] || status
}

// 获取科目类型（使用会议的学科字段）
const getSubjectText = (meeting: Meeting): string => {
  return meeting.subject || '-'
}

// 获取老师数量
const getTeacherCount = (meeting: Meeting): number => {
  return meeting.teachers?.length || 0
}

const loadMeetings = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const data = await getMeetings()
    meetings.value = data
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '获取会议列表失败'
    console.error('Failed to load meetings:', error)
  } finally {
    isLoading.value = false
  }
}

const deleteMessage = ref('')
const deleteDetails = ref('')

const handleDelete = (meetingId: string, meetingName: string) => {
  pendingDeleteMeeting.value = { id: meetingId, name: meetingName }
  deleteMessage.value = `确定要删除会议"${meetingName}"吗？`
  deleteDetails.value = '此操作不可恢复，将同时删除所有相关的转写记录、摘要数据和文档文件。'
  showDeleteDialog.value = true
}

const confirmDelete = async () => {
  if (!pendingDeleteMeeting.value) return

  const { id, name } = pendingDeleteMeeting.value
  isDeleting.value = id
  errorMessage.value = ''

  try {
    await deleteMeeting(id)
    // 删除成功后关闭对话框并重新加载列表
    showDeleteDialog.value = false
    pendingDeleteMeeting.value = null
    await loadMeetings()
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '删除会议失败'
    console.error('Failed to delete meeting:', error)
    // 显示错误提示，但不关闭对话框
  } finally {
    isDeleting.value = null
  }
}

const cancelDelete = () => {
  pendingDeleteMeeting.value = null
  showDeleteDialog.value = false
}

onMounted(() => {
  loadMeetings()
})
</script>

