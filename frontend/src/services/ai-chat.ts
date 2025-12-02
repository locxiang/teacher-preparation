/**
 * AI对话服务 - 处理SSE流式响应
 */

// 使用相对路径，让浏览器自动使用当前访问的域名/IP
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

/**
 * 流式AI对话
 * @param meetingId 会议ID（可选）
 * @param chatHistory 聊天记录
 * @param onChunk 接收到数据块时的回调
 * @param onComplete 流完成时的回调
 * @param onError 错误回调
 */
export async function streamAIChat(
  meetingId: string | undefined,
  chatHistory: string,
  onChunk: (chunk: string) => void,
  onComplete: () => void,
  onError: (error: Error) => void
): Promise<void> {
  try {
    const token = localStorage.getItem('access_token')
    if (!token) {
      throw new Error('未登录')
    }

    // 构建请求URL
    const url = `${API_BASE_URL}/api/ai-chat/stream`

    // 发送POST请求，使用SSE
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        meeting_id: meetingId || null,
        chat_history: chatHistory,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`)
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
              }
            } catch {
              // 如果不是JSON，直接作为文本处理
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
    } finally {
      reader.releaseLock()
    }
  } catch (error) {
    onError(error instanceof Error ? error : new Error('未知错误'))
  }
}

