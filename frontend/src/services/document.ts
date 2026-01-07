/**
 * 文档服务 - 处理文档上传相关的API调用
 */

const API_BASE_URL = ''

export interface Document {
  id: number
  meeting_id: string
  filename: string
  original_filename: string
  file_path: string
  file_size: number
  file_size_mb: number
  file_type: string
  mime_type: string
  status: 'uploaded' | 'processing' | 'completed' | 'failed'
  parse_progress: number
  error_message?: string
  user_id: number
  created_at: string
  updated_at: string
}

export interface DocumentListResponse {
  success: boolean
  data: Document[]
  total: number
}

export interface DocumentResponse {
  success: boolean
  data: Document
}

/**
 * 获取请求头（包含认证token）
 */
function getHeaders(): HeadersInit {
  const headers: HeadersInit = {}

  const token = localStorage.getItem('access_token')
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  return headers
}

/**
 * 上传文档
 */
export async function uploadDocument(
  meetingId: string,
  file: File,
): Promise<Document> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/api/documents/upload/${meetingId}`, {
    method: 'POST',
    headers: getHeaders(),
    body: formData,
  })

  const data: DocumentResponse = await response.json()

  if (!response.ok) {
    throw new Error(data.success === false ? data.message || '上传文档失败' : '未授权')
  }

  return data.data
}

/**
 * 获取会议的所有文档
 */
export async function getDocuments(meetingId: string): Promise<Document[]> {
  const response = await fetch(`${API_BASE_URL}/api/documents/list/${meetingId}`, {
    method: 'GET',
    headers: getHeaders(),
  })

  const data: DocumentListResponse = await response.json()

  if (!response.ok) {
    throw new Error(data.success === false ? data.message || '获取文档列表失败' : '未授权')
  }

  return data.data || []
}

/**
 * 删除文档
 */
export async function deleteDocument(documentId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}`, {
    method: 'DELETE',
    headers: getHeaders(),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.success === false ? data.message || '删除文档失败' : '未授权')
  }
}

/**
 * 获取文件类型图标
 */
export function getFileTypeIcon(fileType: string): string {
  const iconMap: Record<string, string> = {
    pdf: 'PDF',
    doc: 'DOC',
    docx: 'DOC',
    ppt: 'PPT',
    pptx: 'PPT',
    txt: 'TXT',
    md: 'TXT',
    xls: 'XLS',
    xlsx: 'XLS',
  }
  return iconMap[fileType.toLowerCase()] || 'FILE'
}

/**
 * 获取文件类型颜色类
 */
export function getFileTypeColorClass(fileType: string): string {
  const colorMap: Record<string, string> = {
    pdf: 'bg-red-100 text-red-600',
    doc: 'bg-blue-100 text-blue-600',
    docx: 'bg-blue-100 text-blue-600',
    ppt: 'bg-orange-100 text-orange-600',
    pptx: 'bg-orange-100 text-orange-600',
    txt: 'bg-gray-100 text-gray-600',
    md: 'bg-gray-100 text-gray-600',
    xls: 'bg-green-100 text-green-600',
    xlsx: 'bg-green-100 text-green-600',
  }
  return colorMap[fileType.toLowerCase()] || 'bg-gray-100 text-gray-600'
}

