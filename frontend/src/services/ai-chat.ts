/**
 * AI对话服务 - 处理SSE流式响应
 */

// 使用相对路径，让浏览器自动使用当前访问的域名/IP
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

/**
 * 流式AI对话
 * @param meetingId 会议ID（可选）
 * @param chatHistory 聊天记录（字符串格式，用于向后兼容）
 * @param messages 消息数组（OpenAI格式：{role: 'user'|'assistant', content: string}[]）
 * @param onChunk 接收到数据块时的回调
 * @param onComplete 流完成时的回调
 * @param onError 错误回调
 */
export async function streamAIChat(
  meetingId: string | undefined,
  chatHistory: string | number | Array<{role: 'user' | 'assistant', content: string}>,
  onChunk: (chunk: string) => void,
  onComplete: () => void,
  onError: (error: Error) => void,
): Promise<void> {
  try {
    const token = localStorage.getItem('access_token')
    if (!token) {
      throw new Error('未登录')
    }

    // 构建请求URL
    const url = `${API_BASE_URL}/api/ai-chat/stream`

    // 构建请求体
    const requestBody: Record<string, unknown> = {
      meeting_id: meetingId || null,
    }

    // 如果 chatHistory 是数组，传递 messages 和 max_history
    if (Array.isArray(chatHistory)) {
      requestBody.messages = chatHistory
      requestBody.max_history = chatHistory.length // 默认使用数组长度
      console.log('[AI Chat] 发送消息数组，数量:', chatHistory.length, 'max_history:', chatHistory.length)
    } else if (typeof chatHistory === 'number') {
      // 如果是数字，表示 max_history（需要配合 messages 使用）
      requestBody.max_history = chatHistory
      console.log('[AI Chat] 发送 max_history:', chatHistory)
    } else {
      // 向后兼容：字符串格式
      requestBody.chat_history = chatHistory
      console.log('[AI Chat] 发送 chat_history 字符串，长度:', chatHistory.length)
    }

    console.log('[AI Chat] 请求URL:', url)
    console.log('[AI Chat] 请求体:', JSON.stringify(requestBody, null, 2))

    // 发送POST请求，使用SSE
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(requestBody),
    })

    console.log('[AI Chat] 响应状态:', response.status, response.statusText)
    // 记录响应头（使用 forEach 遍历）
    const responseHeaders: Record<string, string> = {}
    response.headers.forEach((value, key) => {
      responseHeaders[key] = value
    })
    console.log('[AI Chat] 响应头:', responseHeaders)

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error('[AI Chat] HTTP错误:', {
        status: response.status,
        statusText: response.statusText,
        errorData,
      })
      const errorMessage = errorData.message || errorData.error || `HTTP ${response.status}: ${response.statusText}`
      throw new Error(errorMessage)
    }

    if (!response.body) {
      throw new Error('响应体为空')
    }

    // 读取SSE流
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    try {
      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          break
        }

        // 解码数据块
        buffer += decoder.decode(value, { stream: true })

        // 处理SSE格式的数据
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // 保留最后一个不完整的行

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6) // 移除 'data: ' 前缀

            // 检查是否是结束标记
            if (data === '[DONE]') {
              onComplete()
              return
            }

            try {
              // 解析JSON数据
              const parsed = JSON.parse(data)
              console.log('[AI Chat] 收到SSE数据:', parsed)

              // 检查是否是错误消息
              if (parsed.error) {
                console.error('[AI Chat] SSE流中的错误:', parsed.error, '错误类型:', parsed.type)
                const error = new Error(parsed.error)
                if (parsed.type) {
                  error.name = parsed.type
                }
                onError(error)
                return
              }

              // 处理不同的数据格式
              if (parsed.content) {
                // OpenAI格式: { content: "文本" }
                onChunk(parsed.content)
              } else if (parsed.text) {
                // 自定义格式: { text: "文本" }
                onChunk(parsed.text)
              } else if (typeof parsed === 'string') {
                // 直接是字符串
                onChunk(parsed)
              } else {
                console.warn('[AI Chat] 未知的数据格式:', parsed)
              }
            } catch (parseError) {
              // 如果不是JSON，直接作为文本处理
              console.warn('[AI Chat] 解析JSON失败，作为文本处理:', data, parseError)
              if (data && data !== '[DONE]') {
                onChunk(data)
              }
            }
          } else if (line.trim() === '') {
            // 空行，忽略
            continue
          }
        }
      }

      // 处理剩余的buffer
      if (buffer.trim()) {
          if (buffer.startsWith('data: ')) {
            const data = buffer.slice(6)
            if (data !== '[DONE]') {
              try {
                const parsed = JSON.parse(data)
                if (parsed.content) {
                  onChunk(parsed.content)
                } else if (parsed.text) {
                  onChunk(parsed.text)
                }
              } catch {
                if (data && data !== '[DONE]') {
                  onChunk(data)
                }
              }
            }
          }
      }

      onComplete()
      console.log('[AI Chat] SSE流读取完成')
    } catch (streamError) {
      console.error('[AI Chat] 读取SSE流时出错:', streamError)
      onError(streamError instanceof Error ? streamError : new Error('读取流时出错'))
    } finally {
      reader.releaseLock()
      console.log('[AI Chat] 释放流读取器')
    }
  } catch (error) {
    console.error('[AI Chat] 请求失败:', {
      error,
      message: error instanceof Error ? error.message : '未知错误',
      stack: error instanceof Error ? error.stack : undefined,
    })
    onError(error instanceof Error ? error : new Error('未知错误'))
  }
}

