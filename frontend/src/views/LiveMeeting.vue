<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <!-- 错误弹窗 -->
    <ConfirmDialog
      :visible="showErrorDialog"
      title="无法开始会议"
      subtitle="缺少必要的任务信息"
      :message="errorDialogMessage"
      confirm-text="返回上传页面"
      cancel-text="返回首页"
      :loading="false"
      @confirm="router.push(`/meeting/${meetingId}/upload`)"
      @cancel="router.push('/')"
      @update:visible="showErrorDialog = $event"
    />

    <!-- 顶部固定栏 -->
    <MeetingHeader
      :meeting="meeting"
      :meeting-id="meetingId"
      :message-count="messages.length"
      :task-info="taskInfo"
      :has-microphone-permission="hasMicrophonePermission"
      :is-requesting-permission="isRequestingPermission"
      :is-recording="isRecording"
      @request-permission="requestMicrophonePermission"
      @toggle-recording="handleToggleRecording"
    />

    <!-- 主内容区域 -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <div class="max-w-[1600px] mx-auto px-8 py-4 w-full flex-1 flex flex-col min-h-0">
        <!-- Meeting Stages Indicator -->
        <MeetingStages
          :stages="stages"
          :current-stage-index="currentStageIndex"
        />

        <div class="flex-1 flex space-x-4 overflow-hidden min-h-0">
          <!-- Left Sidebar -->
          <div class="w-64 flex flex-col space-y-4 overflow-y-auto shrink-0 min-h-0">
            <!-- Audio Visualizer -->
            <AudioVisualizer
              :audio-bars="audioBars"
              :current-speaker="currentSpeaker"
              :is-recording="isRecording"
              :silence-duration="silenceDuration"
              :is-a-i-speaking="isAISpeaking"
              :is-a-i-generating="isAIGenerating"
            />

            <!-- Digital Human Video Area -->
            <DigitalHuman />

            <!-- Participants -->
            <ParticipantsList
              :teachers="meeting?.teachers"
            />

            <!-- Reference Docs -->
            <ReferenceDocs :meeting-id="meetingId" />
          </div>

          <!-- Center: Chat History -->
          <div class="flex-1 flex flex-col overflow-hidden min-h-0">
            <ChatHistory
              :messages="messages"
              :stages="stages"
              :current-stage-index="currentStageIndex"
              :is-recording="isRecording"
              :is-a-i-generating="isAIGenerating"
              :is-a-i-speaking="isAISpeaking"
              @trigger-ai="triggerAISpeech"
              @stop-ai-voice="stopAIVoicePlayback"
            />
          </div>

          <!-- Right Column: Related Materials -->
          <RelatedMaterials :messages="messages" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { AliyunASRDirectService } from '@/services/aliyun-asr-direct'
import { getMeeting, appendMessage, type Meeting, type MessageData } from '@/services/meeting'
import type { RecognitionResult } from '@/services/aliyun-asr'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { streamAIChat } from '@/services/ai-chat'
import { AliyunTTSService, getTTSToken } from '@/services/aliyun-tts'
import MeetingHeader from './liveMeeting/MeetingHeader.vue'
import MeetingStages from './liveMeeting/MeetingStages.vue'
import AudioVisualizer from './liveMeeting/AudioVisualizer.vue'
import ParticipantsList from './liveMeeting/ParticipantsList.vue'
import ReferenceDocs from './liveMeeting/ReferenceDocs.vue'
import DigitalHuman from './liveMeeting/DigitalHuman.vue'
import ChatHistory from './liveMeeting/ChatHistory.vue'
import RelatedMaterials from './liveMeeting/RelatedMaterials.vue'

interface Stage {
  id: string
  name: string
  description: string
}

interface Message {
  id: string
  type: 'human' | 'ai'
  speaker: string
  content: string
  timestamp: number // 绝对时间戳（真实时间）
  relativeTime?: number // 相对时间（从录音开始的毫秒数）
  stageIndex: number
  isFinal?: boolean
}

const stages: Stage[] = [
  { id: 'host', name: '主持人发言', description: '主持人介绍会议主题、目标和流程，明确本次备课的重点。' },
  { id: 'teachers', name: '教师发言', description: '各位老师轮流发表观点，AI 实时记录并标记重点。' },
  { id: 'discussion', name: '集体研讨', description: '针对分歧点进行深入讨论，AI 辅助梳理共识。' },
  { id: 'conclusion', name: '形成结论', description: '总结会议成果，确定最终教学方案和行动计划。' },
]

const currentStageIndex = ref(0)
const route = useRoute()
const router = useRouter()
const meetingId = ref(route.params.id as string || 'demo-meeting-' + Date.now())
const meeting = ref<Meeting | null>(null)

// 语音识别服务
let asrService: AliyunASRDirectService | null = null
const isRecording = ref(false)
const currentSpeaker = ref<string | null>(null)
const wsConnected = ref(false)

// 麦克风权限管理
const hasMicrophonePermission = ref(false)
const isRequestingPermission = ref(false)
let audioStream: MediaStream | null = null
const errorMessage = ref<string>('')

// 任务管理
const taskInfo = ref<{ TaskId?: string; MeetingJoinUrl?: string; TaskStatus?: string } | null>(null)

// 消息列表
const messages = ref<Message[]>([])
const currentTranscriptMessageId = ref<string | null>(null)
const savedMessageIds = ref<Set<string>>(new Set()) // 已保存的消息ID集合，避免重复保存

// 音频可视化数据
const audioBars = ref<number[]>(Array(50).fill(2))

// 静默计时器相关
const lastSpeechTimestamp = ref<number | null>(null)
const silenceDuration = ref<number>(0)
let silenceTimer: number | null = null

// 音频音量检测相关
const SILENCE_DELAY = 500
const BASELINE_SAMPLES = 100
const VARIANCE_WINDOW = 20
const VARIANCE_THRESHOLD = 0.5
let consecutiveSpeechFrames = 0
let isSpeaking = false
let lastSpeechDetectedTime = 0
let silenceStartTime: number | null = null
let volumeDebugCount = 0
let recordingStartTime = 0

// 动态阈值相关
let volumeHistory: number[] = []
let volumeWindow: number[] = []
let noiseBaseline = 0
let baselineCalculated = false
let samplesCollected = 0

// AI说话相关
const isAISpeaking = ref(false)
const isAIGenerating = ref(false)
let ttsService: AliyunTTSService | null = null
let pendingTextBuffer = ''
const SILENCE_THRESHOLD = 10
let aiSpeechStartTime: number | null = null // AI开始说话的时间戳，用于暂停静默计时

// 处理语音识别结果
const handleRecognitionResult = (result: RecognitionResult) => {
  const speaker = result.speaker || '未知'

  // 当识别到有效的文本内容时，才打断 AI 说话（避免被无意义的噪音打断）
  if (result.text && result.text.trim() && (isAISpeaking.value || isAIGenerating.value)) {
    console.log('[LiveMeeting] 🛑 识别到新内容，停止AI说话:', result.text.substring(0, 20))
    stopAIVoice()
    isAIGenerating.value = false
  }

  if (result.isFinal) {
    if (currentTranscriptMessageId.value) {
      const index = messages.value.findIndex(m => m.id === currentTranscriptMessageId.value)
      if (index !== -1) {
        messages.value[index].content = result.text
        messages.value[index].isFinal = true
      }
      currentTranscriptMessageId.value = null
    } else {
      const newMessage: Message = {
        id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: 'human',
        speaker: speaker,
        content: result.text,
        timestamp: result.timestamp,
        relativeTime: result.relativeTime,
        stageIndex: currentStageIndex.value,
        isFinal: true,
      }
      messages.value.push(newMessage)
    }
  } else {
    if (!currentTranscriptMessageId.value) {
      const tempMessage: Message = {
        id: `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: 'human',
        speaker: speaker,
        content: result.text,
        timestamp: result.timestamp,
        relativeTime: result.relativeTime,
        stageIndex: currentStageIndex.value,
        isFinal: false,
      }
      messages.value.push(tempMessage)
      currentTranscriptMessageId.value = tempMessage.id
    } else {
      const index = messages.value.findIndex(m => m.id === currentTranscriptMessageId.value)
      if (index !== -1) {
        messages.value[index].content = result.text
        messages.value[index].speaker = speaker
        messages.value[index].timestamp = result.timestamp
        messages.value[index].relativeTime = result.relativeTime
      }
    }
  }

  if (speaker && speaker !== '未知') {
    currentSpeaker.value = speaker
  }

  if (result.isFinal) {
    // 找到对应的消息并保存
    let messageToSave: Message | null = null

    if (currentTranscriptMessageId.value) {
      // 更新现有消息
      const index = messages.value.findIndex(m => m.id === currentTranscriptMessageId.value)
      if (index !== -1) {
        messageToSave = messages.value[index]
      }
      currentTranscriptMessageId.value = null
    } else {
      // 新创建的消息（在 else 分支中创建的）
      const index = messages.value.length - 1
      if (index >= 0) {
        messageToSave = messages.value[index]
      }
    }

    if (messageToSave && messageToSave.isFinal) {
      saveMessageToDatabase(messageToSave)
    }
  }
}

// 保存单条消息到数据库（增量保存）
const saveMessageToDatabase = async (message: Message) => {
  // 检查消息是否已保存
  if (savedMessageIds.value.has(message.id)) {
    return
  }

  // 只保存最终结果的消息
  if (!message.isFinal) {
    return
  }

  // 必须有内容
  if (!message.content || !message.content.trim()) {
    return
  }

  // 对于AI消息，额外检查内容是否完整
  if (message.type === 'ai') {
    const content = message.content.trim()
    if (content === '' || content === 'AI回答生成失败') {
      return
    }
  }

  try {
    const messageData: MessageData = {
      name: message.speaker || '未知',
      time: message.timestamp,
      type: message.type,
      content: message.content.trim(),
    }

    await appendMessage(meetingId.value, messageData)
    savedMessageIds.value.add(message.id)
    console.log(`[LiveMeeting] ✅ 消息已保存: ${message.type === 'ai' ? 'AI' : '人类'} - ${message.speaker}`)
  } catch (error) {
    console.error('[LiveMeeting] ❌ 保存消息失败:', error)
  }
}

// 保存消息到数据库（批量保存，用于兼容旧逻辑）
const saveMessagesToDatabase = async () => {
  try {
    // 找出所有未保存的最终消息
    const unsavedMessages = messages.value.filter(msg => {
      if (savedMessageIds.value.has(msg.id)) {
        return false
      }
      if (!msg.isFinal) {
        return false
      }
      if (!msg.content || !msg.content.trim()) {
        return false
      }
      if (msg.type === 'ai') {
        const content = msg.content.trim()
        if (content === '' || content === 'AI回答生成失败') {
          return false
        }
      }
      return true
    })

    if (unsavedMessages.length === 0) {
      return
    }

    // 按时间戳排序，逐个保存
    const sortedMessages = [...unsavedMessages].sort((a, b) => a.timestamp - b.timestamp)

    for (const msg of sortedMessages) {
      await saveMessageToDatabase(msg)
    }

    console.log(`[LiveMeeting] ✅ 批量保存完成（共 ${sortedMessages.length} 条消息）`)
  } catch (error) {
    console.error('[LiveMeeting] ❌ 保存聊天记录失败:', error)
  }
}

// 处理识别错误
const handleRecognitionError = (error: Error) => {
  console.error('Recognition error:', error)
  errorMessage.value = error.message || '语音识别错误'
}

// 计算音频数据的RMS（均方根）音量
const calculateRMSVolume = (data: Uint8Array): number => {
  if (data.length === 0) {
    return 0
  }

  let sum = 0
  for (let i = 0; i < data.length; i++) {
    const sample = (data[i] - 128) / 128
    sum += sample * sample
  }

  const rms = Math.sqrt(sum / data.length)
  const percentage = Math.min(100, Math.max(0, rms * 1000))
  return percentage
}

// 计算音量数组的方差
const calculateVariance = (values: number[]): number => {
  if (values.length < 2) {
    return 0
  }

  const mean = values.reduce((sum, val) => sum + val, 0) / values.length
  const variance = values.reduce((sum, val) => {
    const diff = val - mean
    return sum + diff * diff
  }, 0) / values.length

  return variance
}

// 处理音频数据
const handleAudioData = (data: Uint8Array) => {
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

  // 计算音频可视化数据
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

  // 检测是否有有效语音
  const currentVolume = calculateRMSVolume(data)
  const now = Date.now()

  // 收集样本计算环境噪音基线
  if (!baselineCalculated) {
    volumeHistory.push(currentVolume)
    samplesCollected++

    if (samplesCollected >= BASELINE_SAMPLES) {
      const sorted = [...volumeHistory].sort((a, b) => a - b)
      const medianIndex = Math.floor(sorted.length / 2)
      noiseBaseline = sorted[medianIndex]
      baselineCalculated = true
      console.log(`[音量检测] 环境噪音基线已计算: ${noiseBaseline.toFixed(2)}%`)

      if (!isSpeaking && silenceStartTime === null) {
        silenceStartTime = recordingStartTime
        lastSpeechTimestamp.value = recordingStartTime
      }
    }
  }

  // 使用滑动窗口计算音量方差
  volumeWindow.push(currentVolume)
  if (volumeWindow.length > VARIANCE_WINDOW) {
    volumeWindow.shift()
  }

  const variance = volumeWindow.length >= 2 ? calculateVariance(volumeWindow) : 0

  volumeDebugCount++
  if (volumeDebugCount % 50 === 0) {
    console.log(`[音量检测] 当前音量: ${currentVolume.toFixed(2)}%, 基线: ${noiseBaseline.toFixed(2)}%, 方差: ${variance.toFixed(4)}, 阈值: ${VARIANCE_THRESHOLD}, 是否说话: ${isSpeaking}, 静默时长: ${silenceDuration.value}秒`)
  }

  // 基于方差判断是否有人说话
  if (variance > VARIANCE_THRESHOLD) {
    consecutiveSpeechFrames++
    lastSpeechDetectedTime = now

    if (consecutiveSpeechFrames >= 2) {
      if (!isSpeaking) {
        isSpeaking = true
        lastSpeechTimestamp.value = now
        silenceStartTime = null
        silenceDuration.value = 0

        // 注意：不再基于音量检测打断 AI，改为在语音识别到有效内容时打断（见 handleRecognitionResult）
      } else {
        lastSpeechTimestamp.value = now
      }
    }
  } else {
    consecutiveSpeechFrames = 0

    if (isSpeaking && lastSpeechDetectedTime > 0) {
      const timeSinceLastSpeech = now - lastSpeechDetectedTime
      if (timeSinceLastSpeech >= SILENCE_DELAY) {
        isSpeaking = false
        silenceStartTime = lastSpeechTimestamp.value || lastSpeechDetectedTime
        console.log(`[音量检测] 进入静默状态，静默开始时间: ${new Date(silenceStartTime).toLocaleTimeString()}`)
      }
    } else if (!isSpeaking && baselineCalculated && silenceStartTime === null) {
      silenceStartTime = recordingStartTime
      lastSpeechTimestamp.value = recordingStartTime
    }
  }
}

// 初始化语音合成
const initTTS = async (): Promise<void> => {
  // 如果已经有TTS服务正在运行，先停止之前的播放和合成，避免两段音频同时播放
  if (ttsService) {
    console.log('[LiveMeeting] 检测到已有TTS服务，先停止之前的播放和合成')
    try {
      ttsService.stopPlayback() // 停止音频播放
      ttsService.stopSynthesis() // 停止合成
      ttsService.close() // 关闭连接
    } catch (error) {
      console.error('[LiveMeeting] 清理旧TTS服务失败:', error)
    }
    ttsService = null
    pendingTextBuffer = '' // 清空待发送的文本缓冲区
    isAISpeaking.value = false // 重置状态
  }

  console.log('[LiveMeeting] 开始初始化语音合成服务')
  try {
    const { token, app_key } = await getTTSToken()
    ttsService = new AliyunTTSService()

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
        console.log('[LiveMeeting] ✅ 语音合成完成')
      },
      (error: Error) => {
        console.error('[LiveMeeting] ❌ 语音合成错误:', error)
        isAISpeaking.value = false
        errorMessage.value = `语音合成失败: ${error.message}`
        // 清理TTS服务
        if (ttsService) {
          try {
            ttsService.close()
          } catch (e) {
            console.error('[LiveMeeting] 关闭TTS服务失败:', e)
          }
          ttsService = null
        }
      },
      () => {
        console.log('[LiveMeeting] ✅ 音频播放完成')
        isAISpeaking.value = false

        // AI播放完成，重置静默开始时间，重新开始静默计时
        if (aiSpeechStartTime !== null && isRecording.value) {
          const now = Date.now()
          // 重置静默开始时间为当前时间，重新开始计时
          silenceStartTime = now
          lastSpeechTimestamp.value = now
          silenceDuration.value = 0
          aiSpeechStartTime = null
          console.log('[LiveMeeting] ✅ AI播放完成，重新开始静默计时')
        }
      },
    )
  } catch (error) {
    console.error('[LiveMeeting] ❌ 初始化语音合成失败:', error)
    isAISpeaking.value = false
    errorMessage.value = `语音合成初始化失败: ${error instanceof Error ? error.message : '未知错误'}`
  }
}

// 发送文本进行语音合成
const synthesizeText = (text: string) => {
  if (!ttsService) {
    return
  }

  try {
    pendingTextBuffer += text

    if (/[。！？\n]/.test(text)) {
      const sentences = pendingTextBuffer.split(/([。！？\n])/)
      for (let i = 0; i < sentences.length - 1; i += 2) {
        const sentence = sentences[i] + sentences[i + 1]
        if (sentence.trim()) {
          ttsService.sendText(sentence.trim())
        }
      }
      pendingTextBuffer = sentences[sentences.length - 1] || ''
    } else if (pendingTextBuffer.length >= 20) {
      ttsService.sendText(pendingTextBuffer)
      pendingTextBuffer = ''
    }
  } catch (error) {
    console.error('[LiveMeeting] ❌ 发送文本到TTS失败:', error)
  }
}

// 停止AI语音播放（仅停止播放器，不关闭TTS服务）
const stopAIVoicePlayback = () => {
  if (ttsService) {
    // 只调用播放器的 stop 方法，不关闭 TTS 服务
    ttsService.stopPlayback()
  }
  isAISpeaking.value = false
  pendingTextBuffer = ''

  // 如果AI被中断，重置静默开始时间
  if (aiSpeechStartTime !== null && isRecording.value) {
    const now = Date.now()
    silenceStartTime = now
    lastSpeechTimestamp.value = now
    silenceDuration.value = 0
    aiSpeechStartTime = null
    console.log('[LiveMeeting] ✅ AI播放已停止，重新开始静默计时')
  }
}

// 停止AI语音播放（完全停止，包括关闭服务）
const stopAIVoice = () => {
  if (ttsService) {
    ttsService.stopPlayback()
    ttsService.stopSynthesis()
    ttsService.close()
    ttsService = null
  }
  isAISpeaking.value = false
  pendingTextBuffer = ''

  // 如果AI被中断，重置静默开始时间
  if (aiSpeechStartTime !== null && isRecording.value) {
    const now = Date.now()
    silenceStartTime = now
    lastSpeechTimestamp.value = now
    silenceDuration.value = 0
    aiSpeechStartTime = null
    console.log('[LiveMeeting] ✅ AI被中断，重新开始静默计时')
  }
}

// 触发AI说话
const triggerAISpeech = async () => {
  if (isAISpeaking.value || isAIGenerating.value || !isRecording.value) {
    return
  }

  // 检查最新一条消息是否是AI发送的，如果是则不触发
  // 从数组末尾开始查找最新的最终消息（因为新消息总是 push 到数组末尾）
  let latestMessage: Message | null = null
  for (let i = messages.value.length - 1; i >= 0; i--) {
    if (messages.value[i].isFinal) {
      latestMessage = messages.value[i]
      break
    }
  }

  if (latestMessage) {
    console.log(`[LiveMeeting] 🔍 最新最终消息: ${latestMessage.type === 'ai' ? 'AI' : '人类'} - ${latestMessage.speaker} - ${latestMessage.content.substring(0, 20)}`)
  }

  if (latestMessage && latestMessage.type === 'ai') {
    console.log('[LiveMeeting] ⏸️ 最新一条消息是AI发送的，跳过触发AI说话')
    return
  }

  console.log('[LiveMeeting] 🎯 触发AI说话，静默时长:', silenceDuration.value, '秒')

  // 记录AI开始说话的时间，暂停静默计时
  aiSpeechStartTime = Date.now()
  isAIGenerating.value = true
  isAISpeaking.value = true
  pendingTextBuffer = ''

  // 暂停静默计时（不清除 silenceStartTime，但会在计时器中检查 AI 状态）
  console.log('[LiveMeeting] ⏸️ AI开始说话，暂停静默计时')

  // 获取最近的对话消息（包括人类和AI消息），转换为OpenAI格式
  const recentMessages = messages.value
    .filter(msg => msg.isFinal)
    .slice(-10)
    .map(msg => ({
      role: msg.type === 'ai' ? 'assistant' as const : 'user' as const,
      content: msg.type === 'human'
        ? `${msg.speaker || '未知'}: ${msg.content}`
        : msg.content,
    }))

  // 如果没有历史消息，添加会议主题作为初始消息
  if (recentMessages.length === 0) {
    recentMessages.push({
      role: 'user',
      content: `会议主题: ${meeting.value?.name || '备课会议'}`,
    })
  }

  // 标记是否已经初始化TTS（延迟初始化，在收到第一个chunk时才初始化）
  let ttsInitialized = false
  // 缓存TTS初始化完成前到达的chunks，避免丢失
  let pendingChunksBeforeTTSReady: string[] = []

  const aiMessageId = `ai_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  let aiResponseText = ''

  try {
    await streamAIChat(
      meetingId.value || undefined,
      recentMessages, // 传递消息数组而不是字符串
      async (chunk: string) => {
        aiResponseText += chunk

        const existingIndex = messages.value.findIndex(m => m.id === aiMessageId)
        if (existingIndex === -1) {
          const newMessage: Message = {
            id: aiMessageId,
            type: 'ai',
            speaker: '南博士',
            content: aiResponseText,
            timestamp: Date.now(),
            relativeTime: undefined, // AI消息没有相对时间
            stageIndex: currentStageIndex.value,
            isFinal: false,
          }
          messages.value.push(newMessage)
        } else {
          messages.value[existingIndex].content = aiResponseText
        }

        // 延迟初始化TTS（在收到第一个chunk时才初始化）
        if (!ttsInitialized && !ttsService) {
          console.log('[LiveMeeting] 收到第一个AI响应chunk，开始初始化TTS，chunk内容:', chunk.substring(0, 50))
          ttsInitialized = true
          // 缓存第一个chunk，等TTS初始化完成后再发送
          pendingChunksBeforeTTSReady.push(chunk)

          try {
            console.log('[LiveMeeting] 准备初始化TTS，chunk内容:', chunk.substring(0, 50))
            await initTTS()
            console.log('[LiveMeeting] TTS初始化完成，ttsService状态:', ttsService ? '存在' : '不存在')

            // TTS初始化成功后，发送所有缓存的chunks（包括第一个chunk）
            if (ttsService && pendingChunksBeforeTTSReady.length > 0) {
              const allPendingText = pendingChunksBeforeTTSReady.join('')
              console.log('[LiveMeeting] TTS初始化成功，发送所有缓存的chunks，总长度:', allPendingText.length)
              try {
                // 先发送第一个chunk（避免超时），然后通过synthesizeText处理剩余的
                if (allPendingText.trim()) {
                  (ttsService as AliyunTTSService).sendText(allPendingText.trim())
                  console.log('[LiveMeeting] ✅ 所有缓存的chunks已发送到TTS')
                }
              } catch (sendError) {
                console.error('[LiveMeeting] 发送缓存的chunks失败:', sendError)
              }
              // 清空缓存
              pendingChunksBeforeTTSReady = []
            }
          } catch (error) {
            console.error('[LiveMeeting] TTS初始化失败:', error)
            // 即使TTS初始化失败，也继续处理文本
            ttsService = null // 确保清理失败的实例
            ttsInitialized = false // 允许下次重试
            pendingChunksBeforeTTSReady = [] // 清空缓存
          }
        } else if (!ttsService && ttsInitialized) {
          // TTS正在初始化中，缓存chunk等待初始化完成
          console.log('[LiveMeeting] TTS正在初始化中，缓存chunk:', chunk.substring(0, 50))
          pendingChunksBeforeTTSReady.push(chunk)
        } else if (ttsService) {
          // 如果TTS已初始化，实时合成语音
          synthesizeText(chunk)
        }
      },
      () => {
        isAIGenerating.value = false

        const existingIndex = messages.value.findIndex(m => m.id === aiMessageId)
        if (existingIndex !== -1) {
          messages.value[existingIndex].isFinal = true
          // AI消息完成，立即保存单条消息
          saveMessageToDatabase(messages.value[existingIndex])
        }

        if (ttsService) {
          if (pendingTextBuffer.trim()) {
            ttsService.sendText(pendingTextBuffer.trim())
            pendingTextBuffer = ''
          }
          ttsService.stopSynthesis()
        }
      },
      (error: Error) => {
        console.error('[LiveMeeting] ❌ AI对话失败:', error)
        errorMessage.value = error.message || 'AI对话失败，请重试'
        isAIGenerating.value = false
        isAISpeaking.value = false
        stopAIVoice()

        const existingIndex = messages.value.findIndex(m => m.id === aiMessageId)
        if (existingIndex !== -1) {
          messages.value[existingIndex].isFinal = true
          messages.value[existingIndex].content = aiResponseText || 'AI回答生成失败'
          // 即使出错，也保存已生成的消息
          saveMessageToDatabase(messages.value[existingIndex])
        }
      },
    )
  } catch (error) {
    console.error('[LiveMeeting] ❌ AI对话异常:', error)
    errorMessage.value = error instanceof Error ? error.message : 'AI对话失败，请重试'
    isAIGenerating.value = false
    isAISpeaking.value = false
    stopAIVoice()
  }
}

// 请求麦克风权限
const requestMicrophonePermission = async () => {
  isRequestingPermission.value = true
  errorMessage.value = ''

  try {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('浏览器不支持麦克风访问，请使用 HTTPS 协议或更新浏览器')
    }

    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
        sampleRate: 16000,
        channelCount: 1,
      },
    })

    audioStream = stream
    hasMicrophonePermission.value = true
    console.log('麦克风授权成功')
  } catch (error) {
    console.error('Failed to request microphone permission:', error)
    const err = error as DOMException
    errorMessage.value = err.name === 'NotAllowedError'
      ? '无法访问麦克风，请检查浏览器权限设置'
      : err.name === 'NotFoundError'
      ? '未找到麦克风设备'
      : err.message || '无法获取麦克风权限，请检查设备连接'

    hasMicrophonePermission.value = false
    if (audioStream) {
      audioStream.getTracks().forEach(track => track.stop())
      audioStream = null
    }
  } finally {
    isRequestingPermission.value = false
  }
}

// 切换录音状态
const handleToggleRecording = () => {
  if (isRecording.value) {
    handleStopRecording()
  } else {
    handleStartRecording()
  }
}

// 开始录音
const handleStartRecording = async () => {
  try {
    errorMessage.value = ''

    // 检查麦克风权限和音频流状态
    if (!hasMicrophonePermission.value || !audioStream) {
      errorMessage.value = '请先授权麦克风'
      return
    }

    // 检查音频流的 tracks 是否仍然活跃
    const activeTracks = audioStream.getTracks().filter(track => track.readyState === 'live')
    if (activeTracks.length === 0) {
      console.log('[LiveMeeting] 音频流 tracks 已停止，重新获取麦克风权限')
      // 清理旧的流
      audioStream.getTracks().forEach(track => track.stop())
      audioStream = null
      hasMicrophonePermission.value = false

      // 重新获取麦克风权限
      await requestMicrophonePermission()

      if (!hasMicrophonePermission.value || !audioStream) {
        errorMessage.value = '无法重新获取麦克风权限'
        return
      }
    }

    if (!taskInfo.value?.MeetingJoinUrl) {
      errorMessage.value = '请先创建实时记录'
      return
    }

    const wsUrl = taskInfo.value.MeetingJoinUrl
    asrService = new AliyunASRDirectService()

    asrService.onResult(handleRecognitionResult)
    asrService.onError(handleRecognitionError)
    asrService.onAudioData(handleAudioData)

    await asrService.startRecognition(wsUrl, audioStream)

    isRecording.value = true
    wsConnected.value = true
    startSilenceTimer()
  } catch (error) {
    console.error('Failed to start recording:', error)
    const err = error instanceof Error ? error : new Error('无法开始录音')
    errorMessage.value = err.message || '无法开始录音，请检查设备连接'
    isRecording.value = false
    wsConnected.value = false
    asrService = null
  }
}

// 停止录音
const handleStopRecording = async () => {
  if (asrService) {
    asrService.stopRecognition()
    asrService = null
  }

  isRecording.value = false
  wsConnected.value = false
  stopSilenceTimer()
  stopAIVoice()
  isAIGenerating.value = false

  if (currentTranscriptMessageId.value) {
    const index = messages.value.findIndex(m => m.id === currentTranscriptMessageId.value)
    if (index !== -1 && !messages.value[index].isFinal) {
      messages.value.splice(index, 1)
    }
    currentTranscriptMessageId.value = null
  }

  await saveMessagesToDatabase()
  audioBars.value = Array(50).fill(2)
}

// 释放麦克风权限
const releaseMicrophone = () => {
  handleStopRecording()

  if (audioStream) {
    audioStream.getTracks().forEach(track => track.stop())
    audioStream = null
  }

  hasMicrophonePermission.value = false
}

// 启动静默计时器
const startSilenceTimer = () => {
  if (silenceTimer) {
    return
  }

  recordingStartTime = Date.now()
  lastSpeechTimestamp.value = null
  silenceDuration.value = 0
  consecutiveSpeechFrames = 0
  isSpeaking = false
  lastSpeechDetectedTime = 0
  silenceStartTime = null

  volumeHistory = []
  volumeWindow = []
  noiseBaseline = 0
  baselineCalculated = false
  samplesCollected = 0

  silenceTimer = window.setInterval(() => {
    if (!isRecording.value) {
      return
    }

    // 如果AI正在说话或生成中，暂停静默计时
    if (isAISpeaking.value || isAIGenerating.value) {
      // 保持当前的 silenceDuration 不变，不增加计时
      // 但也不重置为0，保持当前值
      return
    }

    if (!isSpeaking) {
      if (silenceStartTime !== null) {
        const now = Date.now()
        const elapsed = Math.floor((now - silenceStartTime) / 1000)
        silenceDuration.value = elapsed

        if (elapsed >= SILENCE_THRESHOLD && !isAISpeaking.value && !isAIGenerating.value) {
          console.log(`[LiveMeeting] ⏰ 静默时长达到${SILENCE_THRESHOLD}秒，触发AI说话`)
          triggerAISpeech()
        }
      } else if (baselineCalculated && recordingStartTime > 0) {
        const now = Date.now()
        const elapsed = Math.floor((now - recordingStartTime) / 1000)
        silenceDuration.value = elapsed

        if (elapsed >= SILENCE_THRESHOLD && !isAISpeaking.value && !isAIGenerating.value) {
          console.log(`[LiveMeeting] ⏰ 静默时长达到${SILENCE_THRESHOLD}秒，触发AI说话`)
          triggerAISpeech()
        }
      } else {
        silenceDuration.value = 0
      }
    } else {
      silenceDuration.value = 0
    }
  }, 1000)
}

// 停止静默计时器
const stopSilenceTimer = () => {
  if (silenceTimer) {
    clearInterval(silenceTimer)
    silenceTimer = null
  }
  silenceDuration.value = 0
  lastSpeechTimestamp.value = null
  consecutiveSpeechFrames = 0
  isSpeaking = false
  lastSpeechDetectedTime = 0
  silenceStartTime = null
  aiSpeechStartTime = null

  volumeHistory = []
  volumeWindow = []
  noiseBaseline = 0
  baselineCalculated = false
  samplesCollected = 0
}

// 错误弹窗
const showErrorDialog = ref(false)
const errorDialogMessage = ref('')

// 解析转写文本为消息列表（支持 JSONL 格式和旧格式）
const parseTranscriptToMessages = (transcriptText: string): Message[] => {
  if (!transcriptText || !transcriptText.trim()) {
    return []
  }

  const lines = transcriptText.split('\n').filter(line => line.trim())
  const parsedMessages: Message[] = []

  lines.forEach((line, index) => {
    try {
      // 尝试解析 JSONL 格式（新格式）
      const messageData = JSON.parse(line)
      if (messageData.name && messageData.time && messageData.type && messageData.content) {
        parsedMessages.push({
          id: `history_${index}_${messageData.time}`,
          type: messageData.type === 'ai' ? 'ai' : 'human',
          speaker: messageData.name,
          content: messageData.content,
          timestamp: messageData.time,
          stageIndex: currentStageIndex.value,
          isFinal: true,
        })
        // 标记为已保存
        savedMessageIds.value.add(`history_${index}_${messageData.time}`)
        return
      }
    } catch {
      // 不是 JSON 格式，尝试解析旧格式（说话人: 内容）
    }

    // 尝试解析旧格式（说话人: 内容）
    const match = line.match(/^(.+?)[：:]\s*(.+)$/)
    if (match) {
      const speakerName = match[1].trim()
      const content = match[2].trim()

      // 判断是否是AI消息
      const isAI = speakerName.includes('AI') || speakerName.includes('助手')
      const meetingStartTime = meeting.value?.created_at ? new Date(meeting.value.created_at).getTime() : Date.now()

      parsedMessages.push({
        id: `history_${index}_${Date.now()}`,
        type: isAI ? 'ai' : 'human',
        speaker: speakerName,
        content: content,
        timestamp: meetingStartTime + index * 1000,
        stageIndex: currentStageIndex.value,
        isFinal: true,
      })
    } else if (line.trim()) {
      // 如果没有匹配到格式，作为普通消息
      const meetingStartTime = meeting.value?.created_at ? new Date(meeting.value.created_at).getTime() : Date.now()
      parsedMessages.push({
        id: `history_${index}_${Date.now()}`,
        type: 'human',
        speaker: '未知',
        content: line.trim(),
        timestamp: meetingStartTime + index * 1000,
        stageIndex: currentStageIndex.value,
        isFinal: true,
      })
    }
  })

  return parsedMessages
}

// 加载会议信息
const loadMeeting = async () => {
  try {
    const data = await getMeeting(meetingId.value)
    meeting.value = data

    // 加载历史聊天记录
    if (data.transcript) {
      const historyMessages = parseTranscriptToMessages(data.transcript)
      if (historyMessages.length > 0) {
        // 将历史消息添加到消息列表（历史消息在底部，新消息会追加在后面）
        messages.value = historyMessages
        console.log(`[LiveMeeting] 加载了 ${historyMessages.length} 条历史消息`)
      }
    } else if (data.transcripts && data.transcripts.length > 0) {
      // 如果有多个transcript，使用最新的
      const latestTranscript = data.transcripts[data.transcripts.length - 1]
      if (latestTranscript.text) {
        const historyMessages = parseTranscriptToMessages(latestTranscript.text)
        if (historyMessages.length > 0) {
          messages.value = historyMessages
          console.log(`[LiveMeeting] 从transcripts加载了 ${historyMessages.length} 条历史消息`)
        }
      }
    }

    if (data.task_id && data.stream_url) {
      taskInfo.value = {
        TaskId: data.task_id,
        MeetingJoinUrl: data.stream_url,
        TaskStatus: 'NEW',
      }
      console.log('使用会议已有的任务信息:', taskInfo.value)
    } else {
      errorDialogMessage.value = '会议没有关联的实时记录任务。\n\n请返回上传资料页面，点击"开始会议"按钮创建任务。'
      showErrorDialog.value = true
      console.error('会议缺少任务信息:', data)
    }
  } catch (error) {
    console.error('Failed to load meeting:', error)
    errorDialogMessage.value = '加载会议信息失败'
    showErrorDialog.value = true
  }
}

onUnmounted(() => {
  handleStopRecording()
  releaseMicrophone()
  stopSilenceTimer()
})

onMounted(async () => {
  await loadMeeting()
})
</script>
