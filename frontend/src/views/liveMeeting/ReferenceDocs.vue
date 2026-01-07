<template>
  <div class="bg-white border border-gray-200 rounded shadow-sm p-4 flex-grow flex flex-col min-h-0">
    <h3 class="text-xs font-semibold text-gray-900 mb-3 shrink-0 flex items-center">
      <svg
        class="w-4 h-4 mr-2 text-gray-600"
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
      参考资料
    </h3>
    <div class="overflow-y-auto flex-grow space-y-1">
      <div
        v-if="isLoading"
        class="text-xs text-gray-400 text-center py-2"
      >
        加载中...
      </div>
      <div
        v-else-if="documents.length === 0"
        class="text-xs text-gray-400 text-center py-2"
      >
        暂无参考资料
      </div>
      <div
        v-for="doc in documents"
        :key="doc.id"
        class="flex items-center text-xs text-gray-600 hover:bg-gray-50 p-1.5 rounded cursor-pointer transition-colors"
        :title="doc.original_filename"
      >
        <span
          class="mr-1.5"
          :class="getFileIconClass(doc.file_type)"
        >
          {{ getFileIcon(doc.file_type) }}
        </span>
        <span class="truncate">{{ doc.original_filename }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { getDocuments, type Document } from '@/services/document'

interface Props {
  meetingId: string
}

const props = defineProps<Props>()

const documents = ref<Document[]>([])
const isLoading = ref(false)

// 获取文件图标
const getFileIcon = (fileType: string): string => {
  const iconMap: Record<string, string> = {
    pdf: '📄',
    doc: '📝',
    docx: '📝',
    ppt: '📊',
    pptx: '📊',
    txt: '📃',
    md: '📃',
    xls: '📈',
    xlsx: '📈',
  }
  return iconMap[fileType.toLowerCase()] || '📄'
}

// 获取文件图标颜色类
const getFileIconClass = (fileType: string): string => {
  const colorMap: Record<string, string> = {
    pdf: 'text-red-500',
    doc: 'text-blue-500',
    docx: 'text-blue-500',
    ppt: 'text-orange-500',
    pptx: 'text-orange-500',
    txt: 'text-gray-500',
    md: 'text-gray-500',
    xls: 'text-green-500',
    xlsx: 'text-green-500',
  }
  return colorMap[fileType.toLowerCase()] || 'text-gray-500'
}

// 加载文档列表
const loadDocuments = async () => {
  if (!props.meetingId) return

  isLoading.value = true
  try {
    const data = await getDocuments(props.meetingId)
    documents.value = data
  } catch (error) {
    console.error('加载参考资料失败:', error)
    documents.value = []
  } finally {
    isLoading.value = false
  }
}

// 监听 meetingId 变化
watch(() => props.meetingId, () => {
  loadDocuments()
})

onMounted(() => {
  loadDocuments()
})
</script>

