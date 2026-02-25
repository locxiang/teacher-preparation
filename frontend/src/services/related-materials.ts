/**
 * 相关资料服务 - 根据对话内容搜索网上相关资料
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export interface RelatedMaterial {
  title: string
  url: string
  snippet: string
  tags: string[]
}

export interface RelatedMaterialsResponse {
  success: boolean
  keyword?: string
  data: RelatedMaterial[]
  message?: string
}

export interface SearchResult {
  keyword: string
  data: RelatedMaterial[]
}

/**
 * 根据对话内容搜索相关资料
 */
export async function searchRelatedMaterials(
  messages: Array<{ role: 'user' | 'assistant'; content: string }>,
): Promise<SearchResult> {
  const token = localStorage.getItem('access_token')
  if (!token) {
    throw new Error('未登录')
  }

  const response = await fetch(`${API_BASE_URL}/api/related-materials/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ messages }),
  })

  const result: RelatedMaterialsResponse = await response.json()

  if (!response.ok) {
    throw new Error(result.message || '搜索相关资料失败')
  }

  if (!result.success) {
    throw new Error(result.message || '搜索相关资料失败')
  }

  return {
    keyword: result.keyword || '',
    data: result.data || [],
  }
}
