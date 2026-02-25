/**
 * 网络资料服务 - 根据对话内容搜索网上资料
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

/** 搜索引擎：谷歌 | 百度 */
export type SearchEngine = 'google' | 'baidu'

/**
 * 根据对话内容搜索网络资料
 * @param messages 对话消息
 * @param engine 搜索引擎，默认百度
 */
export async function searchRelatedMaterials(
  messages: Array<{ role: 'user' | 'assistant'; content: string }>,
  engine: SearchEngine = 'baidu',
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
    body: JSON.stringify({ messages, engine }),
  })

  const result: RelatedMaterialsResponse = await response.json()

  if (!response.ok) {
    throw new Error(result.message || '搜索网络资料失败')
  }

  if (!result.success) {
    throw new Error(result.message || '搜索网络资料失败')
  }

  return {
    keyword: result.keyword || '',
    data: result.data || [],
  }
}
