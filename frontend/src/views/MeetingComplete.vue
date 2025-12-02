<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部固定栏 - 企业级设计 -->
    <div class="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
      <div class="max-w-[1600px] mx-auto px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-semibold text-gray-900">会议创建完成</h1>
            <p class="text-sm text-gray-500 mt-1">会议已创建，任务已初始化，可以开始会议了</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="max-w-[1600px] mx-auto px-8 py-6">
      <div class="max-w-4xl mx-auto space-y-5">
        <!-- Steps -->
        <div class="mb-6 flex items-center justify-center space-x-4 text-sm font-medium">
          <div class="flex items-center text-gray-400">
            <div class="w-6 h-6 rounded-full border-2 border-gray-300 flex items-center justify-center text-xs mr-2">1</div>
            填写基本信息
          </div>
          <div class="w-12 h-0.5 bg-gray-200"></div>
          <div class="flex items-center text-gray-400">
            <div class="w-6 h-6 rounded-full border-2 border-gray-300 flex items-center justify-center text-xs mr-2">2</div>
            上传资料
          </div>
          <div class="w-12 h-0.5 bg-gray-200"></div>
          <div class="flex items-center text-nanyu-600">
            <div class="w-6 h-6 rounded-full bg-nanyu-600 text-white flex items-center justify-center text-xs mr-2">3</div>
            完成
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="isCreatingTask" class="bg-white border border-gray-200 rounded shadow-sm p-12 text-center">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-nanyu-600"></div>
          <p class="mt-4 text-sm text-gray-600">正在创建任务...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="errorMessage" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
          {{ errorMessage }}
        </div>

        <!-- Success Content -->
        <div v-else-if="meeting && taskInfo" class="space-y-5">
          <!-- 会议信息 -->
          <div class="bg-white border border-gray-200 rounded shadow-sm">
            <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
              <h2 class="text-sm font-semibold text-gray-900">会议信息</h2>
            </div>
            <div class="p-6">
              <div class="space-y-0 divide-y divide-gray-200">
                <div class="flex items-center justify-between py-3">
                  <span class="text-sm font-medium text-gray-600">会议名称</span>
                  <span class="text-sm text-gray-900">{{ meeting.name }}</span>
                </div>
                <div v-if="meeting.description" class="flex items-center justify-between py-3">
                  <span class="text-sm font-medium text-gray-600">会议描述</span>
                  <span class="text-sm text-gray-900">{{ meeting.description }}</span>
                </div>
                <div class="flex items-center justify-between py-3">
                  <span class="text-sm font-medium text-gray-600">会议ID</span>
                  <span class="text-sm text-gray-900 font-mono">{{ meeting.id }}</span>
                </div>
                <div class="flex items-center justify-between py-3">
                  <span class="text-sm font-medium text-gray-600">任务ID</span>
                  <span class="text-sm text-gray-900 font-mono">{{ taskInfo.TaskId }}</span>
                </div>
                <div v-if="meeting.teachers && meeting.teachers.length > 0" class="py-3">
                  <span class="text-sm font-medium text-gray-600 block mb-2">参与教师</span>
                  <div class="flex flex-wrap gap-2">
                    <span
                      v-for="teacher in meeting.teachers"
                      :key="teacher.id"
                      class="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded"
                    >
                      {{ teacher.name }}{{ teacher.is_host ? '（主持人）' : '' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 已上传文档 -->
          <div class="bg-white border border-gray-200 rounded shadow-sm">
            <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
              <h2 class="text-sm font-semibold text-gray-900">已上传文档 ({{ documents.length }})</h2>
            </div>
            <div class="p-6">
              <div v-if="documents.length === 0" class="text-center py-8 text-gray-400">
                <svg class="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p class="text-sm">暂无文档</p>
              </div>
              <div v-else class="space-y-2">
                <div
                  v-for="doc in documents"
                  :key="doc.id"
                  class="flex items-center p-3 border border-gray-200 rounded"
                >
                  <div class="flex items-center space-x-3 flex-1 min-w-0">
                    <div
                      class="w-8 h-8 rounded flex items-center justify-center text-sm font-semibold shrink-0"
                      :class="getFileTypeColorClass(doc.file_type)"
                    >
                      {{ getFileTypeIcon(doc.file_type) }}
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="text-sm font-medium text-gray-800 truncate">{{ doc.original_filename }}</div>
                      <div class="text-xs text-gray-500 mt-0.5">
                        {{ doc.file_size_mb }} MB •
                        <span
                          :class="{
                            'text-green-600': doc.status === 'completed',
                            'text-yellow-600': doc.status === 'processing',
                            'text-red-600': doc.status === 'failed',
                            'text-gray-600': doc.status === 'uploaded'
                          }"
                        >
                          {{
                            doc.status === 'completed' ? '已解析完成' :
                            doc.status === 'processing' ? '解析中' :
                            doc.status === 'failed' ? '解析失败' :
                            '已上传'
                          }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="bg-white border border-gray-200 rounded shadow-sm">
            <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
              <h2 class="text-sm font-semibold text-gray-900">下一步操作</h2>
            </div>
            <div class="p-6">
              <div class="flex justify-end space-x-3">
                <router-link
                  to="/"
                  class="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded transition-colors font-medium"
                >
                  返回列表
                </router-link>
                <router-link
                  :to="`/meeting/${meeting.id}/live`"
                  class="px-4 py-2 text-sm bg-nanyu-600 text-white rounded hover:bg-nanyu-700 transition-colors font-medium"
                >
                  进入会议
                </router-link>
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
import { useRoute, useRouter } from 'vue-router'
import { getMeeting, type Meeting } from '@/services/meeting'
import { getDocuments, getFileTypeIcon, getFileTypeColorClass, type Document } from '@/services/document'

const route = useRoute()
const router = useRouter()
const meetingId = route.params.id as string

const meeting = ref<Meeting | null>(null)
const documents = ref<Document[]>([])
const taskInfo = ref<{ TaskId: string; MeetingJoinUrl: string } | null>(null)
const isCreatingTask = ref(false)
const errorMessage = ref('')

// 加载会议信息
const loadMeeting = async () => {
  try {
    const data = await getMeeting(meetingId)
    meeting.value = data
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '获取会议信息失败'
  }
}

// 加载文档列表
const loadDocuments = async () => {
  try {
    const data = await getDocuments(meetingId)
    documents.value = data
  } catch (error) {
    console.error('Failed to load documents:', error)
  }
}

// 创建任务
const createTask = async () => {
  if (!meeting.value) {
    errorMessage.value = '会议信息不存在'
    return
  }

  isCreatingTask.value = true
  errorMessage.value = ''

  try {
    // 使用相对路径，让浏览器自动使用当前访问的域名/IP
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
    const token = localStorage.getItem('access_token')

    // 根据会议信息计算说话人数
    const teacherCount = meeting.value?.teachers?.length || 0
    const speakerCount = teacherCount > 0 ? teacherCount : 0

    // 创建通义听悟任务
    const createTaskResponse = await fetch(`${API_BASE_URL}/api/tytingwu/create-task`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        audio_format: 'pcm',
        sample_rate: 16000,
        source_language: 'cn',
        task_key: meetingId,
        enable_diarization: true,
        speaker_count: speakerCount,
        enable_summary: true,
        summary_types: ['Paragraph', 'Conversational', 'QuestionsAnswering', 'MindMap'],
        enable_key_points: true,
        meeting_assistance_types: ['Actions', 'KeyInformation'],
        enable_text_polish: true,
      }),
    })

    const taskResult = await createTaskResponse.json()

    if (!createTaskResponse.ok || !taskResult.success) {
      throw new Error(taskResult.message || '创建任务失败')
    }

    const taskId = taskResult.data.TaskId
    const streamUrl = taskResult.data.MeetingJoinUrl

    if (!taskId || !streamUrl) {
      throw new Error('任务创建失败：未获取到任务ID或WebSocket地址')
    }

    taskInfo.value = {
      TaskId: taskId,
      MeetingJoinUrl: streamUrl,
    }

    // 更新会议的任务信息
    const updateResponse = await fetch(`${API_BASE_URL}/api/meetings/${meetingId}/task`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        task_id: taskId,
        stream_url: streamUrl,
      }),
    })

    const updateResult = await updateResponse.json()

    if (!updateResponse.ok || !updateResult.success) {
      throw new Error(updateResult.message || '更新会议任务信息失败')
    }

    // 重新加载会议信息以获取最新的任务ID
    await loadMeeting()
  } catch (error) {
    console.error('创建任务失败:', error)
    errorMessage.value = error instanceof Error ? error.message : '创建任务失败，请重试'
  } finally {
    isCreatingTask.value = false
  }
}

onMounted(async () => {
  await loadMeeting()
  await loadDocuments()

  // 如果会议还没有任务ID，创建任务
  if (meeting.value && !meeting.value.task_id) {
    await createTask()
  } else if (meeting.value && meeting.value.task_id) {
    // 如果已有任务ID，从会议信息中获取
    taskInfo.value = {
      TaskId: meeting.value.task_id,
      MeetingJoinUrl: meeting.value.stream_url || '',
    }
  }
})
</script>

