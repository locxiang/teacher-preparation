<template>
  <div class="h-full w-full bg-gradient-to-br from-nanyu-50 to-gray-100 flex flex-col overflow-hidden">
    <!-- 顶部固定栏 -->
    <div class="bg-white/80 backdrop-blur-sm border-b border-gray-200 flex-shrink-0 z-10 shadow-sm">
      <div class="max-w-[1600px] mx-auto px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-semibold text-gray-900">AI 实时语音通话</h1>
            <p class="text-sm text-gray-500 mt-1">与AI进行实时语音对话，支持语音输入和语音输出</p>
          </div>
          <div class="flex items-center space-x-4">
            <!-- 语音开关 -->
            <label class="flex items-center cursor-pointer">
              <input
                type="checkbox"
                v-model="enableVoiceOutput"
                class="w-4 h-4 text-nanyu-600 border-gray-300 rounded focus:ring-nanyu-500"
              />
              <span class="ml-2 text-sm text-gray-700">语音播放</span>
            </label>
            <!-- 清空对话按钮 -->
            <button
              @click="clearChat"
              class="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors font-medium"
            >
              清空对话
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="flex-1 overflow-hidden flex max-w-[1600px] mx-auto w-full px-8 py-6 gap-6 min-h-0" style="height: 0;">
      <!-- 左侧：通话界面 -->
      <div class="w-2/5 flex flex-col items-center justify-center space-y-8 overflow-hidden min-h-0">
        <!-- 通话状态显示 -->
        <div class="text-center w-full">
          <div class="text-4xl font-bold text-gray-800 mb-4">
            <span v-if="isRecording && !isAIThinking && !isAISpeaking" class="text-red-600">
              正在说话...
            </span>
            <span v-else-if="isAIThinking" class="text-nanyu-600 flex items-center justify-center">
              <span class="inline-block animate-pulse mr-2">🤖</span>
              AI思考中
            </span>
            <span v-else-if="isAISpeaking" class="text-nanyu-600 flex items-center justify-center">
              <span class="inline-block animate-pulse mr-2">🔊</span>
              AI正在说话，请等待...
            </span>
            <span v-else class="text-gray-500">
              等待中...
            </span>
          </div>

          <!-- 实时识别文字显示区域 -->
          <div class="w-full max-w-2xl mx-auto">
            <div
              v-if="tempTranscript || (isRecording && !tempTranscript)"
              class="bg-white/90 backdrop-blur-sm border-2 border-dashed rounded-xl shadow-lg p-6 min-h-[120px] flex items-center justify-center"
              :class="tempTranscript ? 'border-nanyu-400' : 'border-gray-300'"
            >
              <div class="w-full">
                <div v-if="tempTranscript" class="text-2xl text-gray-800 font-medium leading-relaxed break-words">
                  {{ tempTranscript }}
                  <span class="inline-block w-1 h-6 bg-nanyu-600 ml-1 animate-pulse"></span>
                </div>
                <div v-else class="text-lg text-gray-400 italic">
                  正在识别中...
                </div>
              </div>
            </div>
            <div
              v-else-if="messages.length > 0 && messages[messages.length - 1].role === 'user'"
              class="bg-white/90 backdrop-blur-sm border border-gray-200 rounded-xl shadow-lg p-6 min-h-[120px] flex items-center justify-center"
            >
              <div class="text-center">
                <div class="text-sm text-gray-500 mb-2">已识别</div>
                <div class="text-xl text-gray-800 font-medium">{{ messages[messages.length - 1].content }}</div>
              </div>
            </div>
            <div
              v-else
              class="bg-white/90 backdrop-blur-sm border-2 border-dashed border-gray-300 rounded-xl shadow-lg p-6 min-h-[120px] flex items-center justify-center"
            >
              <div class="text-lg text-gray-400 italic">等待语音输入...</div>
            </div>
          </div>
        </div>

        <!-- 音频波形可视化 -->
        <div class="w-full max-w-2xl">
          <div class="bg-white/80 backdrop-blur-sm border border-gray-200 rounded-2xl shadow-lg p-6">
            <div class="flex items-end justify-center space-x-1 h-32 bg-gradient-to-b from-gray-50 to-gray-100 rounded-xl p-4">
              <div
                v-for="(bar, index) in audioBars"
                :key="index"
                class="flex-1 rounded-t transition-all duration-75"
                :class="isAISpeaking || isAIThinking ? 'bg-nanyu-500' : isRecording ? 'bg-red-500' : 'bg-gray-300'"
                :style="{ height: `${bar}%`, minHeight: '2px' }"
              />
            </div>
          </div>
        </div>

        <!-- 大号通话按钮 -->
        <div class="flex flex-col items-center space-y-4">
          <button
            @click="toggleRecording"
            :disabled="isAIThinking || isAISpeaking"
            :class="[
              'w-32 h-32 rounded-full shadow-2xl transition-all duration-300 flex items-center justify-center',
              isRecording
                ? 'bg-red-600 hover:bg-red-700 scale-110 animate-pulse'
                : 'bg-nanyu-600 hover:bg-nanyu-700 hover:scale-105',
              (isAIThinking || isAISpeaking) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
            ]"
            :title="isAISpeaking ? 'AI正在说话，请等待说完后再开始对话' : isAIThinking ? 'AI正在思考中...' : ''"
          >
            <svg
              v-if="!isRecording"
              class="w-16 h-16 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
              />
            </svg>
            <svg
              v-else
              class="w-16 h-16 text-white"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M6 6h12v12H6z" />
            </svg>
          </button>
          <p class="text-sm text-gray-600">
            {{ isRecording ? '点击停止录音' : '点击开始说话' }}
          </p>
        </div>

        <!-- 通话信息 -->
        <div class="flex items-center space-x-6 text-sm text-gray-600">
          <div class="flex items-center space-x-2">
            <div :class="['w-3 h-3 rounded-full', isRecording ? 'bg-red-500 animate-pulse' : 'bg-gray-400']"></div>
            <span>用户</span>
          </div>
          <div class="flex items-center space-x-2">
            <div :class="['w-3 h-3 rounded-full', isAISpeaking || isAIThinking ? 'bg-nanyu-600 animate-pulse' : 'bg-gray-400']"></div>
            <span>AI助手</span>
          </div>
        </div>
      </div>

      <!-- 右侧：对话历史 -->
      <div class="flex-1 h-200 flex flex-col bg-white/80 backdrop-blur-sm border border-gray-200 rounded-2xl shadow-lg overflow-hidden min-w-0 min-h-0">
        <div class="px-6 py-4 border-b border-gray-200 bg-gray-50 flex-shrink-0">
          <h2 class="text-lg font-semibold text-gray-900">对话记录</h2>
        </div>
        <div
          class="flex-1 overflow-y-scroll p-4 space-y-4 min-h-0 h-0"
          ref="chatContainer"
        >
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="[
              'flex',
              message.role === 'user' ? 'justify-end' : 'justify-start'
            ]"
          >
            <div
              :class="[
                'max-w-[85%] rounded-lg px-3 py-2 text-sm shadow-sm',
                message.role === 'user'
                  ? 'bg-nanyu-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              ]"
            >
              <div class="font-medium mb-1 text-xs opacity-80">
                {{ message.role === 'user' ? '我' : 'AI助手' }}
              </div>
              <div
                :class="[
                  'whitespace-pre-wrap break-words',
                  message.role === 'user' ? 'text-white' : 'text-gray-700'
                ]"
                v-html="formatMessage(message.content)"
              ></div>
              <div
                :class="[
                  'text-xs mt-1 opacity-70',
                  message.role === 'user' ? 'text-white' : 'text-gray-500'
                ]"
              >
                {{ formatTime(message.timestamp) }}
              </div>
            </div>
          </div>

          <!-- 正在输入指示器 -->
          <div v-if="isAIThinking" class="flex justify-start">
            <div class="bg-gray-100 rounded-lg px-3 py-2">
              <div class="flex items-center space-x-2">
                <div class="flex space-x-1">
                  <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0s"></div>
                  <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                  <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                </div>
                <span class="text-xs text-gray-500">AI正在思考...</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { marked } from 'marked'
import { AliyunISIASRService } from '@/services/aliyun-isi-asr'
import { streamAIChat } from '@/services/ai-chat'
import { AliyunTTSService, getTTSToken } from '@/services/aliyun-tts'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

const messages = ref<Message[]>([])
const isAIThinking = ref(false)
const isAISpeaking = ref(false)
const enableVoiceOutput = ref(true)
const chatContainer = ref<HTMLElement | null>(null)
const audioBars = ref<number[]>(Array(50).fill(2))
const isRecording = ref(false)
const tempTranscript = ref('')
const audioStream = ref<MediaStream | null>(null)

// 语音识别服务
let asrService: AliyunISIASRService | null = null
let ttsService: AliyunTTSService | null = null
let pendingTextBuffer = ''

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true,
})

// 格式化消息（Markdown转HTML）
const formatMessage = (content: string) => {
  try {
    return marked(content)
  } catch (error) {
    console.error('Markdown渲染错误:', error)
    return content.replace(/</g, '&lt;').replace(/>/g, '&gt;')
  }
}

// 格式化时间
const formatTime = (timestamp: number) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      // 使用平滑滚动到底部
      chatContainer.value.scrollTo({
        top: chatContainer.value.scrollHeight,
        behavior: 'smooth',
      })
    }
  })
}

// 处理音频数据（用于可视化）
const handleAudioData = (data: Uint8Array) => {
  // 如果AI正在说话，不处理音频数据（不显示波形，不检测声音）
  if (isAISpeaking.value) {
    return
  }

  // 只在录音时更新可视化
  if (!isRecording.value) {
    audioBars.value = Array(50).fill(2)
    return
  }

  const barCount = audioBars.value.length
  const dataLength = data.length

  if (dataLength === 0) {
    audioBars.value = Array(50).fill(2)
    return
  }

  const step = Math.floor(dataLength / barCount)
  const newBars: number[] = []

  for (let i = 0; i < barCount; i++) {
    const index = i * step
    if (index < dataLength) {
      const value = data[index] || 0
      const percentage = Math.max(2, Math.min(100, (value / 255) * 100))
      newBars.push(percentage)
    } else {
      newBars.push(2)
    }
  }

  audioBars.value = newBars
}

// 初始化TTS（只在收到AI响应时调用，不处理录音逻辑）
const initTTS = async () => {
  if (!enableVoiceOutput.value) {
    return
  }

  // 如果已经有TTS服务正在运行，先停止之前的播放
  if (ttsService && isAISpeaking.value) {
    console.log('[RealtimeChat] 停止之前的AI声音播放，开始新的播放')
    stopVoice()
  }

  try {
    console.log('[RealtimeChat] 开始获取TTS Token')
    const { token, app_key } = await getTTSToken()
    console.log('[RealtimeChat] ✅ TTS Token获取成功')

    ttsService = new AliyunTTSService()
    isAISpeaking.value = true
    console.log('[RealtimeChat] 创建TTS服务实例，准备启动合成')

    await ttsService.startSynthesis(
      {
        token,
        appKey: app_key,
        voice: 'longxiaochun',
        format: 'PCM',
        sampleRate: 24000,
        volume: 100,
        speechRate: 0,
        pitchRate: 0,
      },
      () => {
        // onComplete: 语音合成完成（所有文本都已发送到服务器）
        console.log('[RealtimeChat] 语音合成完成（所有文本已发送）')
        // 注意：这里不设置 isAISpeaking = false，因为音频可能还在播放
      },
      (error: Error) => {
        // onError: 语音合成出错
        console.error('[RealtimeChat] 语音合成错误:', error)
        isAISpeaking.value = false
        // 清理TTS资源
        if (ttsService) {
          ttsService.close()
          ttsService = null
        }
        // 错误时不自动开始录音，让用户手动操作
      },
      () => {
        // onPlaybackComplete: 音频播放完成
        console.log('[RealtimeChat] ✅ 音频播放完成')
        isAISpeaking.value = false

        // 清理TTS资源
        if (ttsService) {
          ttsService.close()
          ttsService = null
        }
        pendingTextBuffer = ''

        // AI播放完成后，自动开始监听（录音）
        nextTick(() => {
          if (!isAISpeaking.value && !isAIThinking.value && !isRecording.value) {
            console.log('[RealtimeChat] 自动开始录音监听')
            startRecording().catch((error) => {
              console.error('[RealtimeChat] 自动开始录音失败:', error)
            })
          } else {
            console.log('[RealtimeChat] 状态不允许自动开始录音:', {
              isAISpeaking: isAISpeaking.value,
              isAIThinking: isAIThinking.value,
              isRecording: isRecording.value,
            })
          }
        })
      },
    )

    console.log('[RealtimeChat] ✅ TTS startSynthesis调用完成，等待SynthesisStarted确认')
  } catch (error) {
    console.error('[RealtimeChat] 初始化语音合成失败:', error)
    enableVoiceOutput.value = false
    isAISpeaking.value = false
    ttsService = null
  }
}

// 发送文本进行语音合成
const synthesizeText = (text: string) => {
  if (!ttsService || !enableVoiceOutput.value) {
    return
  }

  try {
    pendingTextBuffer += text

    // 如果缓冲区有内容，立即发送（不等待句子结束），避免超时
    if (pendingTextBuffer.trim().length > 0) {
      // 检查是否有完整句子
      if (/[。！？\n]/.test(text)) {
        const sentences = pendingTextBuffer.split(/([。！？\n])/)
        for (let i = 0; i < sentences.length - 1; i += 2) {
          const sentence = sentences[i] + sentences[i + 1]
          if (sentence.trim()) {
            ttsService.sendText(sentence.trim())
          }
        }
        pendingTextBuffer = sentences[sentences.length - 1] || ''
      } else if (pendingTextBuffer.length >= 5) {
        // 进一步降低阈值，更频繁地发送，避免超时（从10降到5）
        console.log('[RealtimeChat] 发送文本片段到TTS（达到阈值）:', pendingTextBuffer.substring(0, 50))
        ttsService.sendText(pendingTextBuffer)
        pendingTextBuffer = ''
      } else {
        // 即使没有达到阈值，如果有内容也立即发送（避免超时）
        // 但至少要有1个字符
        if (pendingTextBuffer.trim().length >= 1 && text.trim().length > 0) {
          console.log('[RealtimeChat] 发送文本片段到TTS（保持连接）:', pendingTextBuffer.substring(0, 50))
          ttsService.sendText(pendingTextBuffer.trim())
          pendingTextBuffer = ''
        }
      }
    }
  } catch (error) {
    console.error('[RealtimeChat] 发送文本到TTS失败:', error)
    // 如果是因为合成未开始，尝试重新初始化
    if (error instanceof Error && error.message.includes('Synthesis has not started')) {
      console.log('[RealtimeChat] TTS合成未开始，尝试重新初始化')
      // 不在这里重新初始化，避免循环调用
    }
  }
}

// 停止语音播放
const stopVoice = () => {
  if (ttsService) {
    ttsService.stopPlayback()
    ttsService.stopSynthesis()
    ttsService.close()
    ttsService = null
  }
  pendingTextBuffer = ''
  isAISpeaking.value = false
}

// 发送AI消息
const sendAIMessage = async () => {
  isAIThinking.value = true

  // 标记是否已经初始化TTS（延迟初始化，在收到第一个chunk时才初始化）
  let ttsInitialized = false

  // 构建聊天历史（只保留最近的对话，转换为OpenAI格式）
  const recentMessages = messages.value.slice(-10).map(msg => ({
    role: msg.role === 'user' ? 'user' as const : 'assistant' as const,
    content: msg.content,
  }))

  try {
    await streamAIChat(
      undefined, // 不需要会议ID
      recentMessages, // 传递消息数组
      async (chunk: string) => {
        // 实时追加文本
        const lastMessage = messages.value[messages.value.length - 1]
        if (lastMessage && lastMessage.role === 'assistant') {
          lastMessage.content += chunk
        } else {
          messages.value.push({
            role: 'assistant',
            content: chunk,
            timestamp: Date.now(),
          })
        }
        scrollToBottom()

        // 如果启用语音，延迟初始化TTS（在收到第一个chunk时才初始化）
        if (enableVoiceOutput.value) {
          if (!ttsInitialized && !ttsService) {
            console.log('[RealtimeChat] 收到第一个AI响应chunk，开始初始化TTS，chunk内容:', chunk.substring(0, 50))
            ttsInitialized = true
            try {
              console.log('[RealtimeChat] 准备初始化TTS，chunk内容:', chunk.substring(0, 50))
              await initTTS()
              console.log('[RealtimeChat] TTS初始化完成，ttsService状态:', ttsService ? '存在' : '不存在')

              // TTS初始化成功后，立即发送第一个chunk，避免连接空闲超时
              if (ttsService && chunk.trim()) {
                console.log('[RealtimeChat] TTS初始化成功，立即发送第一个chunk:', chunk.substring(0, 50))
                // 直接发送，不使用缓冲区，确保立即发送
                try {
                  // TypeScript类型断言，确保类型正确
                  (ttsService as AliyunTTSService).sendText(chunk.trim())
                  console.log('[RealtimeChat] ✅ 第一个chunk已发送到TTS')
                } catch (sendError) {
                  console.error('[RealtimeChat] 发送第一个chunk失败:', sendError)
                }
              } else {
                console.warn('[RealtimeChat] TTS初始化后无法发送chunk:', {
                  ttsService: !!ttsService,
                  chunk: chunk.substring(0, 50),
                  chunkTrimmed: chunk.trim(),
                })
              }
            } catch (error) {
              console.error('[RealtimeChat] TTS初始化失败:', error)
              // 即使TTS初始化失败，也继续处理文本
            }
          } else {
            // 如果TTS已初始化，实时合成语音
            if (ttsService) {
              synthesizeText(chunk)
            }
          }
        }
      },
      () => {
        // 流结束：AI回复完毕
        isAIThinking.value = false
        console.log('[RealtimeChat] ✅ AI回复完毕')

        // 如果启用语音，发送剩余的文本并关闭TTS连接
        if (enableVoiceOutput.value && ttsService) {
          // 发送剩余的文本（如果有）
          if (pendingTextBuffer.trim()) {
            console.log('[RealtimeChat] 发送剩余的文本到TTS:', pendingTextBuffer.trim().substring(0, 50))
            ttsService.sendText(pendingTextBuffer.trim())
            pendingTextBuffer = ''
          }

          // 发送StopSynthesis指令，关闭TTS连接（但音频会继续播放直到完成）
          console.log('[RealtimeChat] AI回复完毕，发送StopSynthesis并关闭TTS连接')
          ttsService.stopSynthesis()
          // 注意：不在这里调用 ttsService.close()，让音频继续播放
          // close() 会在 onPlaybackComplete 回调中调用
        }
      },
      (error: Error) => {
        // 错误处理
        console.error('[RealtimeChat] AI对话失败:', {
          error,
          message: error.message,
          name: error.name,
          stack: error.stack,
        })

        // 构建详细的错误消息
        let errorMessage = `抱歉，发生了错误：${error.message}`
        if (error.name && error.name !== 'Error') {
          errorMessage += `\n\n错误类型：${error.name}`
        }

        // 添加常见错误的解决建议
        if (error.message.includes('HTTP 401') || error.message.includes('未登录')) {
          errorMessage += '\n\n提示：请检查登录状态，可能需要重新登录。'
        } else if (error.message.includes('HTTP 500')) {
          errorMessage += '\n\n提示：服务器内部错误，请稍后重试或联系管理员。'
        } else if (error.message.includes('网络') || error.message.includes('fetch')) {
          errorMessage += '\n\n提示：网络连接问题，请检查网络连接。'
        }

        messages.value.push({
          role: 'assistant',
          content: errorMessage,
          timestamp: Date.now(),
        })
        scrollToBottom()
        isAIThinking.value = false
        stopVoice()
      },
    )
  } catch (error) {
    console.error('[RealtimeChat] 调用AI对话服务失败:', {
      error,
      message: error instanceof Error ? error.message : '未知错误',
      stack: error instanceof Error ? error.stack : undefined,
    })

    let errorMessage = `抱歉，发生了错误：${error instanceof Error ? error.message : '未知错误'}`
    if (error instanceof Error && error.name && error.name !== 'Error') {
      errorMessage += `\n\n错误类型：${error.name}`
    }

    messages.value.push({
      role: 'assistant',
      content: errorMessage,
      timestamp: Date.now(),
    })
    scrollToBottom()
    isAIThinking.value = false
    stopVoice()
  }
}

// 获取麦克风权限
const getMicrophonePermission = async (): Promise<MediaStream> => {
  // 检查现有流是否有效（所有轨道都处于活动状态）
  if (audioStream.value) {
    const tracks = audioStream.value.getTracks()
    const allActive = tracks.length > 0 && tracks.every(track => track.readyState === 'live')

    if (allActive) {
      console.log('[RealtimeChat] 使用现有的音频流')
      return audioStream.value
    } else {
      console.log('[RealtimeChat] 现有音频流已停止，需要重新获取')
      // 清理无效的流
      audioStream.value.getTracks().forEach(track => track.stop())
      audioStream.value = null
    }
  }

  try {
    console.log('[RealtimeChat] 获取新的麦克风权限')
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        sampleRate: 16000,
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    })
    audioStream.value = stream
    console.log('[RealtimeChat] ✅ 成功获取麦克风权限')
    return stream
  } catch (error) {
    console.error('[RealtimeChat] 获取麦克风权限失败:', error)
    audioStream.value = null
    throw new Error('无法访问麦克风，请检查权限设置')
  }
}

// 切换录音
const toggleRecording = async () => {
  // 如果AI正在说话，禁止录音
  if (isAISpeaking.value) {
    console.log('[RealtimeChat] AI正在说话，禁止录音，请等待AI说完')
    return
  }

  if (isRecording.value) {
    stopRecording()
  } else {
    await startRecording()
  }
}

// 开始录音
const startRecording = async () => {
  // 如果AI正在说话，禁止录音
  if (isAISpeaking.value) {
    console.log('[RealtimeChat] AI正在说话，禁止开始录音')
    return
  }

  // 如果已经在录音，先停止
  if (isRecording.value && asrService) {
    console.log('[RealtimeChat] 已经在录音，先停止之前的录音')
    stopRecording()
    // 等待一小段时间确保资源清理完成
    await new Promise(resolve => setTimeout(resolve, 100))
  }

  try {
    console.log('[RealtimeChat] 开始录音流程')

    // 获取麦克风权限（会检查流是否有效，无效则重新获取）
    const stream = await getMicrophonePermission()

    // 创建新的ISI ASR服务实例（确保是全新的实例）
    console.log('[RealtimeChat] 创建新的ASR服务实例')
    asrService = new AliyunISIASRService()

    // 4. 设置回调
    asrService.onResult((result) => {
      console.log('[RealtimeChat] 识别结果:', result)

      // 如果AI正在说话，忽略识别结果（不处理，不显示）
      if (isAISpeaking.value) {
        console.log('[RealtimeChat] AI正在说话，忽略语音识别结果')
        return
      }

      if (result.isFinal) {
        // 最终结果
        if (result.text.trim()) {
          // 清空临时显示
          tempTranscript.value = ''
          // 发送消息
          handleSendMessageFromVoice(result.text.trim())
        }
      } else {
        // 中间结果，实时显示
        tempTranscript.value = result.text
      }
    })

    asrService.onError((error) => {
      console.error('[RealtimeChat] 语音识别错误:', error)
      isRecording.value = false
      alert(`语音识别失败: ${error.message}`)
    })

    asrService.onAudioData(handleAudioData)

    // 5. 开始识别（ISI服务会自动连接WebSocket并获取Token）
    await asrService.startRecognition(stream)

    isRecording.value = true
    console.log('[RealtimeChat] 语音识别已启动')
  } catch (error) {
    console.error('[RealtimeChat] 启动录音失败:', error)
    isRecording.value = false
    alert(`启动录音失败: ${error instanceof Error ? error.message : '未知错误'}`)
  }
}

// 停止录音
const stopRecording = () => {
  console.log('[RealtimeChat] 停止录音')

  if (asrService) {
    asrService.stopRecognition()
    asrService = null
  }

  // 清理音频流（ASR服务已经停止了流，但我们需要清理引用）
  // 注意：不要在这里停止流，因为ASR服务已经处理了
  // 但需要清理引用，以便下次重新获取
  if (audioStream.value) {
    const tracks = audioStream.value.getTracks()
    const allEnded = tracks.every(track => track.readyState === 'ended')
    if (allEnded) {
      console.log('[RealtimeChat] 音频流已结束，清理引用')
      audioStream.value = null
    }
  }

  isRecording.value = false
  tempTranscript.value = ''
  audioBars.value = Array(50).fill(2)
  console.log('[RealtimeChat] ✅ 录音已停止')
}

// 从语音识别结果发送消息
const handleSendMessageFromVoice = async (text: string) => {
  if (!text.trim()) {
    return
  }

  // 如果AI正在思考，等待完成
  if (isAIThinking.value) {
    console.log('[RealtimeChat] AI正在思考，等待完成后再发送消息')
    // 可以选择等待或者直接添加消息
    // 这里选择直接添加消息，不等待AI完成
  }

  // 停止录音（在发送AI消息之前）
  if (isRecording.value) {
    console.log('[RealtimeChat] 用户消息已识别，停止录音，准备发送给AI')
    stopRecording()
  }

  // 添加用户消息
  const userMessage = {
    role: 'user' as const,
    content: text.trim(),
    timestamp: Date.now(),
  }

  messages.value.push(userMessage)
  console.log('[RealtimeChat] 已添加用户消息:', userMessage)

  scrollToBottom()

  // 发送AI请求
  await sendAIMessage()
}

// 清空对话
const clearChat = () => {
  if (confirm('确定要清空所有对话记录吗？')) {
    messages.value = []
    stopVoice()
  }
}

onMounted(() => {
  // 添加欢迎消息和模拟对话样例
  const now = Date.now()

  messages.value.push({
    role: 'assistant',
    content: '你好！我是备课AI助手，可以与你进行实时语音对话，帮助你进行教学准备和讨论。点击中间的按钮开始说话，我会实时识别你的语音并为你提供专业的教学建议和备课支持。',
    timestamp: now - 300000,
  })
  // 确保初始时滚动到底部
  scrollToBottom()
})

onUnmounted(() => {
  stopVoice()
  stopRecording()
  // 清理音频流
  if (audioStream.value) {
    audioStream.value.getTracks().forEach(track => track.stop())
    audioStream.value = null
  }
})
</script>

<style scoped>
/* Markdown内容样式 */
:deep(.markdown-body) {
  line-height: 1.6;
}

:deep(.markdown-body h1),
:deep(.markdown-body h2),
:deep(.markdown-body h3) {
  font-weight: 600;
  margin-top: 0.5em;
  margin-bottom: 0.25em;
  font-size: 1em;
}

:deep(.markdown-body p) {
  margin-bottom: 0.5em;
}

:deep(.markdown-body code) {
  background-color: rgba(0, 0, 0, 0.1);
  padding: 0.2em 0.4em;
  border-radius: 0.25rem;
  font-size: 0.85em;
}

:deep(.markdown-body pre) {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 0.5em;
  border-radius: 0.25rem;
  overflow-x: auto;
  margin: 0.5em 0;
}

:deep(.markdown-body pre code) {
  background-color: transparent;
  padding: 0;
}

/* 聊天记录滚动条样式 - 确保滚动条明显可见 */
.chat-container {
  scrollbar-width: thin;
  scrollbar-color: rgba(107, 114, 128, 0.9) rgba(229, 231, 235, 0.5);
  /* 确保可以滚动 */
  position: relative;
}

.chat-container::-webkit-scrollbar {
  width: 10px;
  /* 确保滚动条始终显示 */
  -webkit-appearance: none;
}

.chat-container::-webkit-scrollbar-track {
  background: rgba(229, 231, 235, 0.5);
  border-radius: 5px;
  margin: 4px 0;
}

.chat-container::-webkit-scrollbar-thumb {
  background-color: rgba(107, 114, 128, 0.9);
  border-radius: 5px;
  border: 2px solid rgba(229, 231, 235, 0.5);
  min-height: 30px;
}

.chat-container::-webkit-scrollbar-thumb:hover {
  background-color: rgba(75, 85, 99, 1);
}

.chat-container::-webkit-scrollbar-thumb:active {
  background-color: rgba(55, 65, 81, 1);
}
</style>
