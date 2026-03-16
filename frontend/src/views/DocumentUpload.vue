<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部固定栏 - 企业级设计 -->
    <div class="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
      <div class="max-w-[1600px] mx-auto px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <router-link
              to="/meeting/create"
              class="text-gray-500 hover:text-gray-700 transition-colors"
            >
              <svg
                class="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
            </router-link>
            <div>
              <h1 class="text-2xl font-semibold text-gray-900">
                上传备课资料
              </h1>
              <p class="text-sm text-gray-500 mt-1">
                南博士将分析这些资料，为您提供更精准的建议
              </p>
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
            <div class="w-6 h-6 rounded-full border-2 border-gray-300 flex items-center justify-center text-xs mr-2">
              1
            </div>
            填写基本信息
          </div>
          <div class="w-12 h-0.5 bg-gray-200" />
          <div class="flex items-center text-nanyu-600">
            <div class="w-6 h-6 rounded-full bg-nanyu-600 text-white flex items-center justify-center text-xs mr-2">
              2
            </div>
            上传资料
          </div>
          <div class="w-12 h-0.5 bg-gray-200" />
          <div class="flex items-center text-gray-400">
            <div class="w-6 h-6 rounded-full border-2 border-gray-300 flex items-center justify-center text-xs mr-2">
              3
            </div>
            完成
          </div>
        </div>

        <!-- Upload Area -->
        <div class="bg-white border border-gray-200 rounded shadow-sm">
          <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
            <h2 class="text-sm font-semibold text-gray-900">
              上传文件
            </h2>
          </div>
          <div class="p-6">
            <div
              ref="uploadArea"
              class="border-2 border-dashed rounded p-8 text-center transition-colors group"
              :class="isUploading 
                ? 'border-nanyu-500 bg-nanyu-50 cursor-wait' 
                : isDragging 
                  ? 'border-nanyu-500 bg-nanyu-50 cursor-pointer' 
                  : 'border-gray-300 hover:border-nanyu-500 hover:bg-nanyu-50 cursor-pointer'"
              @click="!isUploading && triggerFileInput()"
              @dragover.prevent="!isUploading && handleDragOver($event)"
              @dragleave.prevent="!isUploading && handleDragLeave()"
              @drop.prevent="!isUploading && handleDrop($event)"
            >
              <input
                ref="fileInput"
                type="file"
                multiple
                accept=".docx"
                :disabled="isUploading"
                class="hidden"
                @change="handleFileSelect"
              >
              <!-- 上传中状态 -->
              <div
                v-if="isUploading"
                class="w-full"
              >
                <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-nanyu-600 mb-3" />
                <h3 class="text-sm font-medium text-gray-700 mb-1">
                  正在上传并解析文档...
                </h3>
                <p class="text-gray-600 text-xs mb-2">
                  当前文件：{{ uploadingFile }}
                </p>
                <p class="text-gray-500 text-xs">
                  进度：{{ uploadProgress.current }} / {{ uploadProgress.total }}
                </p>
                <div class="w-full max-w-xs mx-auto mt-3 bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-nanyu-500 h-2 rounded-full transition-all duration-300"
                    :style="`width: ${(uploadProgress.current / uploadProgress.total) * 100}%`"
                  />
                </div>
                <p class="text-gray-400 text-xs mt-3">
                  文档上传后会立即进行AI解析，请稍候...
                </p>
              </div>
              <!-- 正常状态 -->
              <template v-else>
                <div class="text-5xl mb-3 text-gray-300 group-hover:text-nanyu-400 transition-colors">
                  📄
                </div>
                <h3 class="text-sm font-medium text-gray-700 mb-1">
                  点击或拖拽文件到此处上传
                </h3>
                <p class="text-gray-400 text-xs">
                  仅支持 DOCX 格式（Word 文档），单个文件不超过 5MB
                </p>
                <p class="text-gray-400 text-xs mt-1">
                  文档将逐个上传并解析，请耐心等待
                </p>
                <p
                  v-if="uploadError"
                  class="text-red-500 text-xs mt-2"
                >
                  {{ uploadError }}
                </p>
              </template>
            </div>
          </div>

          <!-- File List -->
          <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
            <div class="flex items-center justify-between">
              <h3 class="text-sm font-semibold text-gray-900">
                已上传文件 ({{ documents.length }})
              </h3>
              <!-- 解析状态统计 -->
              <div
                v-if="documents.length > 0"
                class="flex items-center space-x-4 text-xs"
              >
                <span class="text-gray-600">
                  <span class="inline-block w-2 h-2 rounded-full bg-green-500 mr-1" />
                  已完成: {{ completedCount }}
                </span>
                <span
                  v-if="processingCount > 0"
                  class="text-gray-600"
                >
                  <span class="inline-block w-2 h-2 rounded-full bg-yellow-500 mr-1 animate-pulse" />
                  解析中: {{ processingCount }}
                </span>
                <span
                  v-if="failedCount > 0"
                  class="text-red-600"
                >
                  <span class="inline-block w-2 h-2 rounded-full bg-red-500 mr-1" />
                  失败: {{ failedCount }}
                </span>
              </div>
            </div>
          </div>
          <div class="p-6">
            <!-- Creating Meeting -->
            <div
              v-if="isCreatingMeeting"
              class="text-center py-8"
            >
              <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-nanyu-600" />
              <p class="mt-4 text-sm text-gray-600">
                正在创建会议...
              </p>
            </div>

            <!-- Loading -->
            <div
              v-else-if="isLoading"
              class="text-center py-8"
            >
              <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-nanyu-600" />
              <p class="mt-4 text-sm text-gray-600">
                加载中...
              </p>
            </div>

            <!-- Empty State -->
            <div
              v-else-if="documents.length === 0"
              class="text-center py-8 text-gray-400"
            >
              <svg
                class="w-12 h-12 mx-auto mb-2 text-gray-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <p class="text-sm">
                还没有上传文件
              </p>
            </div>

            <!-- File List -->
            <div
              v-else
              class="space-y-3"
            >
              <!-- 解析中的文档（优先显示） -->
              <template v-if="processingDocuments.length > 0">
                <div class="mb-4">
                  <h4 class="text-xs font-semibold text-gray-500 mb-2 flex items-center">
                    <span class="inline-block w-2 h-2 rounded-full bg-yellow-500 mr-2 animate-pulse" />
                    正在解析中 ({{ processingDocuments.length }})
                  </h4>
                  <div class="space-y-2">
                    <div
                      v-for="doc in processingDocuments"
                      :key="doc.id"
                      class="flex items-center p-3 border-2 border-yellow-200 bg-yellow-50 rounded hover:border-yellow-300 transition-colors"
                    >
                      <div
                        class="w-8 h-8 rounded flex items-center justify-center text-sm mr-3 font-semibold shrink-0"
                        :class="getFileTypeColorClass(doc.file_type)"
                      >
                        {{ getFileTypeIcon(doc.file_type) }}
                      </div>
                      <div class="grow min-w-0">
                        <h4 class="text-sm font-medium text-gray-800 truncate">
                          {{ doc.original_filename }}
                        </h4>
                        <div class="mt-2">
                          <div class="w-full bg-gray-200 rounded-full h-2">
                            <div
                              class="bg-yellow-500 h-2 rounded-full transition-all duration-300"
                              :style="`width: ${doc.parse_progress}%`"
                            />
                          </div>
                          <p class="text-xs text-gray-600 mt-1 flex items-center">
                            <span class="inline-block animate-spin mr-1">⏳</span>
                            解析中... {{ doc.parse_progress }}%
                          </p>
                        </div>
                      </div>
                      <button
                        :disabled="isDeleting === doc.id"
                        class="text-gray-400 hover:text-red-500 p-1.5 transition-colors disabled:opacity-50 shrink-0"
                        title="删除文件"
                        @click="handleDeleteDocument(doc.id)"
                      >
                        <span
                          v-if="isDeleting === doc.id"
                          class="inline-block animate-spin text-xs"
                        >⏳</span>
                        <span
                          v-else
                          class="text-lg"
                        >&times;</span>
                      </button>
                    </div>
                  </div>
                </div>
              </template>

              <!-- 已完成的文档 -->
              <template v-if="completedDocuments.length > 0">
                <div class="mb-4">
                  <h4 class="text-xs font-semibold text-gray-500 mb-2 flex items-center">
                    <span class="inline-block w-2 h-2 rounded-full bg-green-500 mr-2" />
                    解析完成 ({{ completedDocuments.length }})
                  </h4>
                  <div class="space-y-2">
                    <div
                      v-for="doc in completedDocuments"
                      :key="doc.id"
                      class="flex items-center p-3 border border-green-200 bg-green-50 rounded hover:border-green-300 transition-colors"
                    >
                      <div
                        class="w-8 h-8 rounded flex items-center justify-center text-sm mr-3 font-semibold shrink-0"
                        :class="getFileTypeColorClass(doc.file_type)"
                      >
                        {{ getFileTypeIcon(doc.file_type) }}
                      </div>
                      <div class="grow min-w-0">
                        <h4 class="text-sm font-medium text-gray-800 truncate">
                          {{ doc.original_filename }}
                        </h4>
                        <p class="text-xs text-gray-500 mt-0.5">
                          {{ doc.file_size_mb }} MB •
                          <span class="text-green-600 font-medium">✓ 已解析完成</span>
                        </p>
                      </div>
                      <button
                        :disabled="isDeleting === doc.id"
                        class="text-gray-400 hover:text-red-500 p-1.5 transition-colors disabled:opacity-50 shrink-0"
                        title="删除文件"
                        @click="handleDeleteDocument(doc.id)"
                      >
                        <span
                          v-if="isDeleting === doc.id"
                          class="inline-block animate-spin text-xs"
                        >⏳</span>
                        <span
                          v-else
                          class="text-lg"
                        >&times;</span>
                      </button>
                    </div>
                  </div>
                </div>
              </template>

              <!-- 失败的文档 -->
              <template v-if="failedDocuments.length > 0">
                <div class="mb-4">
                  <h4 class="text-xs font-semibold text-red-600 mb-2 flex items-center">
                    <span class="inline-block w-2 h-2 rounded-full bg-red-500 mr-2" />
                    解析失败 ({{ failedDocuments.length }})
                  </h4>
                  <div class="space-y-2">
                    <div
                      v-for="doc in failedDocuments"
                      :key="doc.id"
                      class="flex items-center p-3 border border-red-200 bg-red-50 rounded hover:border-red-300 transition-colors"
                    >
                      <div
                        class="w-8 h-8 rounded flex items-center justify-center text-sm mr-3 font-semibold shrink-0"
                        :class="getFileTypeColorClass(doc.file_type)"
                      >
                        {{ getFileTypeIcon(doc.file_type) }}
                      </div>
                      <div class="grow min-w-0">
                        <h4 class="text-sm font-medium text-gray-800 truncate">
                          {{ doc.original_filename }}
                        </h4>
                        <p class="text-xs text-red-600 mt-0.5">
                          {{ doc.file_size_mb }} MB •
                          <span class="font-medium">✗ 解析失败</span>
                          <span
                            v-if="doc.error_message"
                            class="ml-2 text-red-500"
                          >
                            {{ doc.error_message }}
                          </span>
                        </p>
                      </div>
                      <button
                        :disabled="isDeleting === doc.id"
                        class="text-gray-400 hover:text-red-500 p-1.5 transition-colors disabled:opacity-50 shrink-0"
                        title="删除文件"
                        @click="handleDeleteDocument(doc.id)"
                      >
                        <span
                          v-if="isDeleting === doc.id"
                          class="inline-block animate-spin text-xs"
                        >⏳</span>
                        <span
                          v-else
                          class="text-lg"
                        >&times;</span>
                      </button>
                    </div>
                  </div>
                </div>
              </template>

              <!-- 已上传但未开始解析的文档 -->
              <template v-if="uploadedDocuments.length > 0">
                <div>
                  <h4 class="text-xs font-semibold text-gray-500 mb-2 flex items-center">
                    <span class="inline-block w-2 h-2 rounded-full bg-gray-400 mr-2" />
                    已上传 ({{ uploadedDocuments.length }})
                  </h4>
                  <div class="space-y-2">
                    <div
                      v-for="doc in uploadedDocuments"
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
                        <h4 class="text-sm font-medium text-gray-800 truncate">
                          {{ doc.original_filename }}
                        </h4>
                        <p class="text-xs text-gray-500 mt-0.5">
                          {{ doc.file_size_mb }} MB •
                          <span class="text-gray-600">等待解析...</span>
                        </p>
                      </div>
                      <button
                        :disabled="isDeleting === doc.id"
                        class="text-gray-400 hover:text-red-500 p-1.5 transition-colors disabled:opacity-50 shrink-0"
                        title="删除文件"
                        @click="handleDeleteDocument(doc.id)"
                      >
                        <span
                          v-if="isDeleting === doc.id"
                          class="inline-block animate-spin text-xs"
                        >⏳</span>
                        <span
                          v-else
                          class="text-lg"
                        >&times;</span>
                      </button>
                    </div>
                  </div>
                </div>
              </template>
            </div>
          </div>

          <!-- Footer Actions -->
          <div class="px-6 py-4 border-t border-gray-200 bg-gray-50">
            <!-- 提示信息 -->
            <div
              v-if="processingCount > 0"
              class="mb-3 p-3 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-800"
            >
              <div class="flex items-start">
                <svg
                  class="w-5 h-5 mr-2 mt-0.5 shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <div>
                  <p class="font-medium">
                    有 {{ processingCount }} 个文档正在解析中
                  </p>
                  <p class="text-xs mt-1 text-yellow-700">
                    解析会在后台继续进行，您可以先进入下一步。解析完成后，南博士将能够更好地理解备课资料。
                  </p>
                </div>
              </div>
            </div>
            <div
              v-if="failedCount > 0"
              class="mb-3 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-800"
            >
              <div class="flex items-start">
                <svg
                  class="w-5 h-5 mr-2 mt-0.5 shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <div>
                  <p class="font-medium">
                    有 {{ failedCount }} 个文档解析失败
                  </p>
                  <p class="text-xs mt-1 text-red-700">
                    您可以删除失败的文档重新上传，或继续下一步（失败的文档将不会被南博士使用）。
                  </p>
                </div>
              </div>
            </div>
            
            <!-- 操作按钮 -->
            <div class="flex justify-between items-center">
              <router-link
                to="/meeting/create"
                class="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded transition-colors font-medium"
              >
                上一步
              </router-link>
              <div class="flex items-center space-x-3">
                <button
                  v-if="documents.length > 0"
                  :disabled="isRefreshing"
                  class="px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded transition-colors font-medium disabled:opacity-50"
                  title="刷新文档状态"
                  @click="handleRefresh"
                >
                  <span
                    v-if="isRefreshing"
                    class="inline-block animate-spin mr-1"
                  >⏳</span>
                  刷新状态
                </button>
                <button
                  :disabled="isCreatingMeeting || !meetingId"
                  class="px-4 py-2 text-sm bg-nanyu-600 text-white rounded hover:bg-nanyu-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  @click="handleNext"
                >
                  {{ isCreatingMeeting ? '正在创建会议...' : '下一步：完成' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
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
  lesson_type?: string
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
const isRefreshing = ref(false)
const isUploading = ref(false)
const uploadingFile = ref<string>('')
const uploadProgress = ref({ current: 0, total: 0 })
const meeting = ref<Meeting | null>(null)

// 计算属性：按状态分组文档
const processingDocuments = computed(() => 
  documents.value.filter(doc => doc.status === 'processing'),
)

const completedDocuments = computed(() => 
  documents.value.filter(doc => doc.status === 'completed'),
)

const failedDocuments = computed(() => 
  documents.value.filter(doc => doc.status === 'failed'),
)

const uploadedDocuments = computed(() => 
  documents.value.filter(doc => doc.status === 'uploaded'),
)

// 计算属性：统计数量
const processingCount = computed(() => processingDocuments.value.length)
const completedCount = computed(() => completedDocuments.value.length)
const failedCount = computed(() => failedDocuments.value.length)

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
      formData.value.grade,
      formData.value.lesson_type,
      teacherIds,
      formData.value.hostTeacherId,
    )

    meetingId.value = meetingData.id
    meeting.value = meetingData

    // 清除 sessionStorage 中的表单数据，避免下次新建会议时显示上次的信息
    sessionStorage.removeItem('meetingFormData')

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
    
    // 检查是否有 processing 状态的文档，如果有且定时器未运行，重新启动定时器
    const hasProcessing = documents.value.some(doc => doc.status === 'processing')
    if (hasProcessing && refreshInterval === null) {
      startRefreshInterval()
    }
  } catch (error) {
    uploadError.value = error instanceof Error ? error.message : '获取文档列表失败'
    throw error  // 重新抛出错误，让调用者知道失败了
  } finally {
    isLoading.value = false
  }
}

// 启动刷新定时器
const startRefreshInterval = () => {
  // 如果已经有定时器在运行，不重复启动
  if (refreshInterval !== null) {
    return
  }
  
  consecutiveFailures = 0
  
  refreshInterval = window.setInterval(() => {
    if (meetingId.value) {
      const hasProcessing = documents.value.some(doc => doc.status === 'processing')
      const hasFailed = documents.value.some(doc => doc.status === 'failed')
      
      // 只刷新有 processing 状态的文档，排除 failed 状态的文档
      if (hasProcessing && !hasFailed) {
        loadDocuments().then(() => {
          // 刷新成功，重置失败计数
          consecutiveFailures = 0
        }).catch(() => {
          // 刷新失败，增加失败计数
          consecutiveFailures++
          // 如果连续失败太多次，停止刷新（可能是网络问题）
          if (consecutiveFailures >= MAX_CONSECUTIVE_FAILURES) {
            console.warn('文档状态刷新连续失败，已停止自动刷新')
            stopRefreshInterval()
          }
        })
      } else if (hasFailed && !hasProcessing) {
        // 如果只有失败的文档，没有正在处理的，停止刷新
        stopRefreshInterval()
      } else if (!hasProcessing) {
        // 如果没有正在处理的文档，停止刷新
        stopRefreshInterval()
      }
    }
  }, 2000) // 每2秒刷新一次，更及时地更新状态
}

// 停止刷新定时器
const stopRefreshInterval = () => {
  if (refreshInterval !== null) {
    clearInterval(refreshInterval)
    refreshInterval = null
    consecutiveFailures = 0
  }
}

// 刷新文档状态
const handleRefresh = async () => {
  if (!meetingId.value) return
  
  isRefreshing.value = true
  try {
    await loadDocuments()
  } catch (error) {
    console.error('刷新文档状态失败:', error)
  } finally {
    isRefreshing.value = false
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
  // 如果正在上传，忽略新的选择
  if (isUploading.value) {
    return
  }
  
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

// 上传文件（串行上传，等待每个文档解析完成）
const uploadFiles = async (files: File[]) => {
  if (!meetingId.value) {
    uploadError.value = '会议未创建，请刷新页面重试'
    return
  }

  uploadError.value = ''

  // 过滤有效的文件
  const validFiles = files.filter(file => {
    const fileName = file.name.toLowerCase()
    if (!fileName.endsWith('.docx')) {
      uploadError.value = `文件 ${file.name} 格式不支持，仅支持 DOCX 格式`
      return false
    }
    if (file.size > 5 * 1024 * 1024) {
      uploadError.value = `文件 ${file.name} 超过5MB限制`
      return false
    }
    return true
  })

  if (validFiles.length === 0) {
    if (uploadError.value) {
      setTimeout(() => {
        uploadError.value = ''
      }, 3000)
    }
    return
  }

  // 开始串行上传
  isUploading.value = true
  uploadProgress.value = { current: 0, total: validFiles.length }

  try {
    // 一个接一个地上传和解析
    for (let i = 0; i < validFiles.length; i++) {
      const file = validFiles[i]
      uploadProgress.value.current = i + 1
      uploadingFile.value = file.name

      try {
        // 上传文档（后端会同步解析，所以这里会等待解析完成）
        const doc = await uploadDocument(meetingId.value, file)
        
        // 检查解析是否成功
        if (doc.status === 'failed') {
          const errorMsg = `文件 ${file.name} 上传成功，但解析失败${doc.error_message ? ': ' + doc.error_message : ''}`
          uploadError.value = uploadError.value ? `${uploadError.value}; ${errorMsg}` : errorMsg
        }
        
        // 添加到列表开头
        documents.value.unshift(doc)
        
        // 如果文档是 processing 状态，启动定时器
        if (doc.status === 'processing') {
          startRefreshInterval()
        }
        
        // 刷新文档列表以获取最新状态
        await loadDocuments()
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : `上传文件 ${file.name} 失败`
        uploadError.value = uploadError.value ? `${uploadError.value}; ${errorMsg}` : errorMsg
        // 继续上传下一个文件，不中断
        console.error(`上传文件失败: ${file.name}`, error)
      }
    }
  } finally {
    isUploading.value = false
    uploadingFile.value = ''
    uploadProgress.value = { current: 0, total: 0 }
    
    // 3秒后清除错误信息
    if (uploadError.value) {
      setTimeout(() => {
        uploadError.value = ''
      }, 5000)
    }
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
  
  // 如果正在上传，忽略拖拽
  if (isUploading.value) {
    return
  }
  
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

let refreshInterval: number | null = null
let consecutiveFailures = 0  // 连续失败次数
const MAX_CONSECUTIVE_FAILURES = 5  // 最大连续失败次数

onMounted(async () => {
  await initializeMeeting()
  
  // 初始化后检查是否有正在处理的文档，如果有则启动定时器
  const hasProcessing = documents.value.some(doc => doc.status === 'processing')
  if (hasProcessing) {
    startRefreshInterval()
  }
})

onUnmounted(() => {
  // 组件卸载时清除定时器
  stopRefreshInterval()
})
</script>

