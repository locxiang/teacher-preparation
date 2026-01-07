/**
 * 会议服务 - 处理会议相关的API调用
 */

// API 基础 URL（使用相对路径，由 Vite 代理处理）
const API_BASE_URL = ''

export interface Transcript {
  id: number
  meeting_id: string
  text: string
  summary?: any
  key_points?: string[]
  duration?: number
  created_at: string
  updated_at: string
}

export interface Teacher {
  id: number
  name: string
  subject: string
  is_host?: boolean
}

export interface Meeting {
  id: string
  name: string
  description?: string
  subject?: string  // 学科：数学、语文等
  grade?: string  // 年级：初一年级、初二年级、初三年级、高一年级、高二年级、高三年级等
  lesson_type?: string  // 备课类型：新课、复习、专题等
  status: 'pending' | 'running' | 'stopped' | 'completed'
  task_id?: string  // 通义听悟任务ID（重要）
  stream_url?: string
  user_id: number
  created_at: string
  updated_at: string
  transcript?: string
  transcripts?: Transcript[]
  summary?: any
  key_points?: string[]
  teachers?: Teacher[]  // 参与的老师列表
  host_teacher?: Teacher  // 主持人
}

export interface MeetingListResponse {
  success: boolean
  data: Meeting[]
  total: number
}

export interface MeetingResponse {
  success: boolean
  data: Meeting
}

/**
 * 获取请求头（包含认证token）
 */
function getHeaders(): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }

  const token = localStorage.getItem('access_token')
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  return headers
}

/**
 * 获取会议列表
 */
export async function getMeetings(status?: string): Promise<Meeting[]> {
  const url = status
    ? `${API_BASE_URL}/api/meetings?status=${status}`
    : `${API_BASE_URL}/api/meetings`

  const response = await fetch(url, {
    method: 'GET',
    headers: getHeaders(),
  })

  const data: MeetingListResponse = await response.json()

  if (!response.ok) {
    throw new Error(data.success === false ? '获取会议列表失败' : '未授权')
  }

  return data.data || []
}

/**
 * 获取单个会议信息
 */
export async function getMeeting(meetingId: string): Promise<Meeting> {
  const response = await fetch(`${API_BASE_URL}/api/meetings/${meetingId}`, {
    method: 'GET',
    headers: getHeaders(),
  })

  const data: MeetingResponse = await response.json()

  if (!response.ok) {
    throw new Error(data.success === false ? '获取会议信息失败' : '未授权')
  }

  return data.data
}

/**
 * 创建会议
 */
export async function createMeeting(
  name: string,
  description?: string,
  subject?: string,
  grade?: string,
  lessonType?: string,
  teacherIds?: number[],
  hostTeacherId?: number,
): Promise<Meeting> {
  const response = await fetch(`${API_BASE_URL}/api/meetings`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({
      name,
      description,
      subject,
      grade,
      lesson_type: lessonType,
      teacher_ids: teacherIds,
      host_teacher_id: hostTeacherId,
    }),
  })

  const data: MeetingResponse = await response.json()

  if (!response.ok) {
    throw new Error(data.success === false ? data.message || '创建会议失败' : '未授权')
  }

  return data.data
}

/**
 * 停止会议
 */
export async function stopMeeting(meetingId: string): Promise<Meeting> {
  const response = await fetch(`${API_BASE_URL}/api/meetings/${meetingId}/stop`, {
    method: 'POST',
    headers: getHeaders(),
  })

  const data: MeetingResponse = await response.json()

  if (!response.ok) {
    throw new Error(data.success === false ? data.message || '停止会议失败' : '未授权')
  }

  return data.data
}

/**
 * 完成会议（将状态设置为 completed）
 */
export async function completeMeeting(meetingId: string): Promise<Meeting> {
  const response = await fetch(`${API_BASE_URL}/api/meetings/${meetingId}/complete`, {
    method: 'POST',
    headers: getHeaders(),
  })

  const data: MeetingResponse = await response.json()

  if (!response.ok) {
    throw new Error(data.success === false ? data.message || '完成会议失败' : '未授权')
  }

  return data.data
}

/**
 * 删除会议
 */
export async function deleteMeeting(meetingId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/meetings/${meetingId}`, {
    method: 'DELETE',
    headers: getHeaders(),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.success === false ? data.message || '删除会议失败' : '未授权')
  }
}

/**
 * 格式化日期
 */
export function formatDate(dateString: string): string {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

/**
 * 更新转写文本（旧接口，兼容）
 */
export async function updateTranscript(meetingId: string, transcript: string): Promise<Meeting> {
  const response = await fetch(`${API_BASE_URL}/api/meetings/${meetingId}/transcript`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify({
      transcript,
    }),
  })

  const data: MeetingResponse = await response.json()

  if (!response.ok) {
    throw new Error(data.success === false ? data.message || '更新转写文本失败' : '未授权')
  }

  return data.data
}

/**
 * 追加单条消息到转写记录（新接口，推荐使用）
 */
export interface MessageData {
  name: string
  time: number  // Unix时间戳（毫秒）
  type: 'human' | 'ai'
  content: string
}

export async function appendMessage(meetingId: string, message: MessageData): Promise<Meeting> {
  const response = await fetch(`${API_BASE_URL}/api/meetings/${meetingId}/transcript`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(message),
  })

  const data: MeetingResponse = await response.json()

  if (!response.ok) {
    throw new Error(data.success === false ? data.message || '追加消息失败' : '未授权')
  }

  return data.data
}

/**
 * 计算会议时长（分钟）
 */
export function calculateDuration(meeting: Meeting): number {
  if (!meeting.created_at) return 0
  const start = new Date(meeting.created_at).getTime()
  const end = meeting.updated_at ? new Date(meeting.updated_at).getTime() : Date.now()
  return Math.floor((end - start) / 1000 / 60)
}

/**
 * 下载会议总结Word文档
 */
export async function downloadSummary(meetingId: string): Promise<void> {
  const token = localStorage.getItem('access_token')
  const headers: HeadersInit = {}
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(`${API_BASE_URL}/api/meetings/${meetingId}/summary/download`, {
    method: 'GET',
    headers: headers,
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.message || '下载会议总结失败')
  }

  // 获取文件名（从响应头或使用默认名称）
  const contentDisposition = response.headers.get('Content-Disposition')
  let filename = `会议总结_${meetingId}.docx`
  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
    if (filenameMatch && filenameMatch[1]) {
      filename = filenameMatch[1].replace(/['"]/g, '')
      // 处理URL编码的文件名
      try {
        filename = decodeURIComponent(filename)
      } catch {
        // 如果解码失败，使用原始文件名
      }
    }
  }

  // 下载文件
  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)
}

