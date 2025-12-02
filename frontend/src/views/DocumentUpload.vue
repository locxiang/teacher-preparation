<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部固定栏 - 企业级设计 -->
    <div class="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
      <div class="max-w-[1600px] mx-auto px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <router-link to="/meeting/create" class="text-gray-500 hover:text-gray-700 transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </router-link>
            <div>
              <h1 class="text-2xl font-semibold text-gray-900">上传备课资料</h1>
              <p class="text-sm text-gray-500 mt-1">AI助手将分析这些资料，为您提供更精准的建议</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="max-w-[1600px] mx-auto px-8 py-6">
      <div class="max-w-4xl mx-auto">
        <!-- Steps -->
        <div class="mb-6 flex items-center justify-center space-x-4 text-sm font-medium">
          <div class="flex items-center text-gray-400">
            <div class="w-6 h-6 rounded-full border-2 border-gray-300 flex items-center justify-center text-xs mr-2">1</div>
            填写基本信息
          </div>
          <div class="w-12 h-0.5 bg-gray-200"></div>
          <div class="flex items-center text-nanyu-600">
            <div class="w-6 h-6 rounded-full bg-nanyu-600 text-white flex items-center justify-center text-xs mr-2">2</div>
            上传资料
          </div>
          <div class="w-12 h-0.5 bg-gray-200"></div>
          <div class="flex items-center text-gray-400">
            <div class="w-6 h-6 rounded-full border-2 border-gray-300 flex items-center justify-center text-xs mr-2">3</div>
            完成
          </div>
        </div>

        <!-- Upload Area -->
        <div class="bg-white border border-gray-200 rounded shadow-sm">
          <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
            <h2 class="text-sm font-semibold text-gray-900">上传文件</h2>
          </div>
          <div class="p-6">
            <div
              ref="uploadArea"
              @click="triggerFileInput"
              @dragover.prevent="handleDragOver"
              @dragleave.prevent="handleDragLeave"
              @drop.prevent="handleDrop"
              class="border-2 border-dashed rounded p-8 text-center transition-colors cursor-pointer group"
              :class="isDragging ? 'border-nanyu-500 bg-nanyu-50' : 'border-gray-300 hover:border-nanyu-500 hover:bg-nanyu-50'"
            >
              <input
                ref="fileInput"
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.md,.xls,.xlsx"
                @change="handleFileSelect"
                class="hidden"
              />
              <div class="text-5xl mb-3 text-gray-300 group-hover:text-nanyu-400 transition-colors">📄</div>
              <h3 class="text-sm font-medium text-gray-700 mb-1">点击或拖拽文件到此处上传</h3>
              <p class="text-gray-400 text-xs">支持 PDF, Word, PPT, TXT 格式，单个文件不超过 20MB</p>
              <p v-if="uploadError" class="text-red-500 text-xs mt-2">{{ uploadError }}</p>
            </div>
          </div>

          <!-- File List -->
          <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
            <h3 class="text-sm font-semibold text-gray-900">
              已上传文件 ({{ documents.length }})
            </h3>
          </div>
          <div class="p-6">
            <!-- Creating Meeting -->
            <div v-if="isCreatingMeeting" class="text-center py-8">
              <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-nanyu-600"></div>
              <p class="mt-4 text-sm text-gray-600">正在创建会议...</p>
            </div>

            <!-- Loading -->
            <div v-else-if="isLoading" class="text-center py-8">
              <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-nanyu-600"></div>
              <p class="mt-4 text-sm text-gray-600">加载中...</p>
            </div>

            <!-- Empty State -->
            <div v-else-if="documents.length === 0" class="text-center py-8 text-gray-400">
              <svg class="w-12 h-12 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p class="text-sm">还没有上传文件</p>
            </div>

            <!-- File List -->
            <div v-else class="space-y-3">
              <div
                v-for="doc in documents"
                :key="doc.id"
                class="flex items-center p-3 border border-gray-200 rounded hover:border-gray-300 hover:bg-gray-50 transition-colors"
              >
                <div
                  class="w-8 h-8 rounded flex items-center justify-center text-sm mr-3 font-semibold shrink-0"
                  :class="getFileTypeColorClass(doc.file_type)"
                >
                  {{ getFileTypeIcon(doc.file_type) }}
                </div>
                <div class="grow min-w-0">
                  <h4 class="text-sm font-medium text-gray-800 truncate">{{ doc.original_filename }}</h4>
                  <div v-if="doc.status === 'processing'" class="mt-2">
                    <div class="w-full bg-gray-200 rounded-full h-1">
                      <div
                        class="bg-nanyu-500 h-1 rounded-full transition-all"
                        :style="`width: ${doc.parse_progress}%`"
                      ></div>
                    </div>
                    <p class="text-xs text-gray-500 mt-1">解析中... {{ doc.parse_progress }}%</p>
                  </div>
                  <p v-else class="text-xs text-gray-500 mt-0.5">
                    {{ doc.file_size_mb }} MB •
                    <span
                      :class="{
                        'text-green-600': doc.status === 'completed',
                        'text-red-600': doc.status === 'failed',
                        'text-gray-600': doc.status === 'uploaded'
                      }"
                    >
                      {{
                        doc.status === 'completed' ? '已解析完成' :
                        doc.status === 'failed' ? '解析失败' :
                        '已上传'
                      }}
                    </span>
                    <span v-if="doc.error_message" class="text-red-500 ml-2">
                      ({{ doc.error_message }})
                    </span>
                  </p>
                </div>
                <button
                  @click="handleDeleteDocument(doc.id)"
                  :disabled="isDeleting === doc.id"
                  class="text-gray-400 hover:text-red-500 p-1.5 transition-colors disabled:opacity-50 shrink-0"
                  title="删除文件"
                >
                  <span v-if="isDeleting === doc.id" class="inline-block animate-spin text-xs">⏳</span>
                  <span v-else class="text-lg">&times;</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Footer Actions -->
          <div class="px-6 py-4 border-t border-gray-200 bg-gray-50 flex justify-between items-center">
            <div class="flex space-x-3">
              <router-link
                to="/meeting/create"
                class="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded transition-colors font-medium"
              >
                上一步
              </router-link>
              <button
                @click="handleNext"
                :disabled="isCreatingMeeting || !meetingId"
                class="px-4 py-2 text-sm bg-nanyu-600 text-white rounded hover:bg-nanyu-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ isCreatingMeeting ? '正在创建会议...' : '下一步：完成' }}
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
import { useRouter, useRoute } from 'vue-router'
import {
  uploadDocument,
  getDocuments,
  deleteDocument,
  getFileTypeIcon,
  getFileTypeColorClass,
  type Document,
} from '@/services/document'
import { createMeeting, getMeeting, type Meeting } from '@/services/meeting'

const router = useRouter()
const route = useRoute()
const meetingId = ref<string>('')
const formData = ref<{
  name: string
  description?: string
  subject?: string
  grade?: string
  teacherIds: number[]
  hostTeacherId: number
  teachers: Array<{ id: number; name: string; subject: string }>
} | null>(null)

const fileInput = ref<HTMLInputElement | null>(null)
const uploadArea = ref<HTMLDivElement | null>(null)
const documents = ref<Document[]>([])
const isLoading = ref(false)
const isDragging = ref(false)
const uploadError = ref('')
const isDeleting = ref<number | null>(null)
const isCreatingMeeting = ref(false)
const meeting = ref<Meeting | null>(null)

// 初始化会议：从路由参数获取已有会议，或从 sessionStorage 创建新会议
const initializeMeeting = async () => {
  // 如果路由中有 meetingId，加载已有会议
  const routeMeetingId = route.params.id as string
  if (routeMeetingId) {
    try {
      isLoading.value = true
      meetingId.value = routeMeetingId
      meeting.value = await getMeeting(routeMeetingId)

      // 加载文档列表
      await loadDocuments()
      return
    } catch (error) {
      console.error('Failed to load meeting:', error)
      alert(error instanceof Error ? error.message : '加载会议失败')
      router.push('/')
      return
    } finally {
      isLoading.value = false
    }
  }

  // 如果没有路由参数，使用原来的逻辑：从 sessionStorage 读取表单数据并创建会议
  const savedFormData = sessionStorage.getItem('meetingFormData')
  if (!savedFormData) {
    router.push('/meeting/create')
    return
  }

  try {
    formData.value = JSON.parse(savedFormData)
    if (!formData.value) {
      router.push('/meeting/create')
      return
    }

    isCreatingMeeting.value = true

    // 创建会议
    const teacherIds = formData.value.teacherIds
    const meetingData = await createMeeting(
      formData.value.name,
      formData.value.description,
      formData.value.subject,
      teacherIds,
      formData.value.hostTeacherId,
    )

    meetingId.value = meetingData.id
    meeting.value = meetingData

    // 加载文档列表
    await loadDocuments()
  } catch (error) {
    console.error('Failed to create meeting:', error)
    alert(error instanceof Error ? error.message : '创建会议失败')
    router.push('/meeting/create')
  } finally {
    isCreatingMeeting.value = false
  }
}

// 加载文档列表
const loadDocuments = async () => {
  if (!meetingId.value) return

  isLoading.value = true
  uploadError.value = ''

  try {
    const data = await getDocuments(meetingId.value)
    documents.value = data
  } catch (error) {
    uploadError.value = error instanceof Error ? error.message : '获取文档列表失败'
  } finally {
    isLoading.value = false
  }
}

// 跳转到完成页面
const handleNext = () => {
  if (!meetingId.value) {
    alert('会议未创建，请刷新页面重试')
    return
  }
  // 保存会议ID到 sessionStorage，供完成页面使用
  sessionStorage.setItem('createdMeetingId', meetingId.value)
  router.push(`/meeting/${meetingId.value}/complete`)
}

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value?.click()
}

// 处理文件选择
const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files && files.length > 0) {
    await uploadFiles(Array.from(files))
    // 清空input，以便可以重复选择同一文件
    if (target) {
      target.value = ''
    }
  }
}

// 上传文件
const uploadFiles = async (files: File[]) => {
  if (!meetingId.value) {
    uploadError.value = '会议未创建，请刷新页面重试'
    return
  }

  uploadError.value = ''

  for (const file of files) {
    // 检查文件大小（20MB）
    if (file.size > 20 * 1024 * 1024) {
      uploadError.value = `文件 ${file.name} 超过20MB限制`
      continue
    }

    try {
      const doc = await uploadDocument(meetingId.value, file)
      documents.value.unshift(doc) // 添加到列表开头
    } catch (error) {
      uploadError.value = error instanceof Error ? error.message : `上传文件 ${file.name} 失败`
    }
  }

  // 3秒后清除错误信息
  if (uploadError.value) {
    setTimeout(() => {
      uploadError.value = ''
    }, 3000)
  }
}

// 拖拽处理
const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = true
}

const handleDragLeave = () => {
  isDragging.value = false
}

const handleDrop = async (e: DragEvent) => {
  isDragging.value = false
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    await uploadFiles(Array.from(files))
  }
}

// 删除文档
const handleDeleteDocument = async (documentId: number) => {
  if (!confirm('确定要删除这个文档吗？')) {
    return
  }

  isDeleting.value = documentId

  try {
    await deleteDocument(documentId)
    documents.value = documents.value.filter(doc => doc.id !== documentId)
  } catch (error) {
    alert(error instanceof Error ? error.message : '删除文档失败')
  } finally {
    isDeleting.value = null
  }
}

onMounted(async () => {
  await initializeMeeting()

  // 定期刷新文档状态（如果正在处理）
  const interval = setInterval(() => {
    if (meetingId.value) {
      const hasProcessing = documents.value.some(doc => doc.status === 'processing')
      if (hasProcessing) {
        loadDocuments()
      }
    }
  }, 3000) // 每3秒刷新一次

  // 组件卸载时清除定时器
  return () => {
    clearInterval(interval)
  }
})
</script>

