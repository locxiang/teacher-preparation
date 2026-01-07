/**
 * 认证服务 - 处理登录、注册、用户信息等API调用
 */

// API 基础 URL
// 使用相对路径，让 Vite 代理或 Nginx 代理处理
// 浏览器无法解析 Docker 内部服务名，所以使用相对路径
const API_BASE_URL = ''

export interface User {
  id: number
  username: string
  email: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LoginResponse {
  success: boolean
  data: {
    user: User
    access_token: string
  }
  message: string
}

export interface RegisterResponse {
  success: boolean
  data: {
    user: User
    access_token: string
  }
  message: string
}

export interface UserInfoResponse {
  success: boolean
  data: User
}

/**
 * 获取存储的 token
 */
export function getToken(): string | null {
  return localStorage.getItem('access_token')
}

/**
 * 设置 token
 */
export function setToken(token: string): void {
  localStorage.setItem('access_token', token)
}

/**
 * 移除 token
 */
export function removeToken(): void {
  localStorage.removeItem('access_token')
}

/**
 * 获取请求头（包含认证token）
 */
function getHeaders(): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }

  const token = getToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  return headers
}

/**
 * 用户注册
 */
export async function register(
  username: string,
  email: string,
  password: string,
): Promise<RegisterResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({
      username,
      email,
      password,
    }),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.message || '注册失败')
  }

  // 保存 token
  if (data.success && data.data?.access_token) {
    setToken(data.data.access_token)
  }

  return data
}

/**
 * 用户登录
 */
export async function login(
  usernameOrEmail: string,
  password: string,
): Promise<LoginResponse> {
  // 判断是用户名还是邮箱
  const isEmail = usernameOrEmail.includes('@')
  const payload = isEmail
    ? { email: usernameOrEmail, password }
    : { username: usernameOrEmail, password }

  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(payload),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.message || '登录失败')
  }

  // 保存 token
  if (data.success && data.data?.access_token) {
    setToken(data.data.access_token)
  }

  return data
}

/**
 * 用户登出
 */
export function logout(): void {
  removeToken()
}

/**
 * 获取当前用户信息
 */
export async function getCurrentUser(): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    method: 'GET',
    headers: getHeaders(),
  })

  const data: UserInfoResponse = await response.json()

  if (!response.ok) {
    throw new Error(data.success === false ? '获取用户信息失败' : '未授权')
  }

  return data.data
}

/**
 * 检查是否已登录
 */
export function isAuthenticated(): boolean {
  return !!getToken()
}

/**
 * 获取用户列表
 */
export async function getUsers(): Promise<User[]> {
  const response = await fetch(`${API_BASE_URL}/api/auth/users`, {
    method: 'GET',
    headers: getHeaders(),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.message || '获取用户列表失败')
  }

  return data.data
}

/**
 * 更新用户状态
 */
export async function updateUserStatus(userId: number, isActive: boolean): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/api/auth/users/${userId}/status`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify({
      is_active: isActive,
    }),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.message || '更新用户状态失败')
  }

  return data.data
}

/**
 * 删除用户
 */
export async function deleteUser(userId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/auth/users/${userId}`, {
    method: 'DELETE',
    headers: getHeaders(),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.message || '删除用户失败')
  }
}

export interface ApiKeyInfo {
  name: string
  value: string
  is_set: boolean | null
  full_value: string | null
}

export interface ApiKeysResponse {
  success: boolean
  data: {
    backend: {
      alibaba_cloud: {
        access_key_id: ApiKeyInfo
        access_key_secret: ApiKeyInfo
      }
      tytingwu: {
        app_key: ApiKeyInfo
      }
      flask: {
        secret_key: ApiKeyInfo
      }
    }
    frontend: {
      xunfei: {
        app_id: ApiKeyInfo
        access_key_id: ApiKeyInfo
        access_key_secret: ApiKeyInfo
      }
    }
  }
}

/**
 * 获取API密钥信息
 */
export async function getApiKeys(): Promise<ApiKeysResponse['data']> {
  const response = await fetch(`${API_BASE_URL}/api/auth/api-keys`, {
    method: 'GET',
    headers: getHeaders(),
  })

  const data: ApiKeysResponse = await response.json()

  if (!response.ok) {
    throw new Error(data.success === false ? '获取API密钥信息失败' : '未授权')
  }

  return data.data
}

