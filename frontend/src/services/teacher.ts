/**
 * 教师服务 - 处理教师相关的API调用
 */

const API_BASE_URL = ''

export interface Teacher {
  id: number
  name: string
  subject: string
  feature_id?: string
  has_voiceprint: boolean
  user_id: number
  created_at: string
  updated_at: string
}

export interface TeacherListResponse {
  success: boolean
  data: Teacher[]
  total: number
}

export interface TeacherResponse {
  success: boolean
  data: Teacher
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
 * 获取教师列表
 */
export async function getTeachers(): Promise<Teacher[]> {
  const response = await fetch(`${API_BASE_URL}/api/teachers`, {
    method: 'GET',
    headers: getHeaders(),
  })

  const data: TeacherListResponse = await response.json()

  if (!response.ok) {
    throw new Error(data.success === false ? '获取教师列表失败' : '未授权')
  }

  return data.data || []
}

/**
 * 创建教师
 */
export async function createTeacher(
  name: string,
  subject: string,
  featureId?: string,
): Promise<Teacher> {
  const response = await fetch(`${API_BASE_URL}/api/teachers`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({
      name,
      subject,
      feature_id: featureId,
    }),
  })

  const data: TeacherResponse = await response.json()

  if (!response.ok) {
    throw new Error(data.success === false ? data.message || '创建教师失败' : '未授权')
  }

  return data.data
}

/**
 * 更新教师信息
 */
export async function updateTeacher(
  teacherId: number,
  updates: {
    name?: string
    subject?: string
    feature_id?: string
  },
): Promise<Teacher> {
  const response = await fetch(`${API_BASE_URL}/api/teachers/${teacherId}`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify(updates),
  })

  const data: TeacherResponse = await response.json()

  if (!response.ok) {
    throw new Error(data.success === false ? data.message || '更新教师失败' : '未授权')
  }

  return data.data
}

/**
 * 删除教师
 */
export async function deleteTeacher(teacherId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/teachers/${teacherId}`, {
    method: 'DELETE',
    headers: getHeaders(),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.success === false ? data.message || '删除教师失败' : '未授权')
  }
}

